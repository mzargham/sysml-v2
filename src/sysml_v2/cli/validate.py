"""``sysml validate`` — validate SysML v2 model files."""

from __future__ import annotations

import sys
from pathlib import Path

import click
import httpx
from rich.console import Console
from rich.table import Table

from sysml_v2.config import load_config
from sysml_v2.parsing.loader import find_models, load

console = Console()


def _validate_local(files: list[Path]) -> list[tuple[Path, str]]:
    """Parse each file with sysml2py. Return list of (path, error_message)."""
    errors: list[tuple[Path, str]] = []
    for path in files:
        try:
            load(path)
        except Exception as exc:
            errors.append((path, str(exc)))
    return errors


def _validate_server(files: list[Path], server_url: str) -> list[tuple[Path, str]]:
    """POST file contents to a Gearshift ``/parse`` endpoint for validation.

    Falls back gracefully if the server is unreachable.
    """
    errors: list[tuple[Path, str]] = []
    try:
        client = httpx.Client(base_url=server_url, timeout=10)
    except Exception:
        console.print(
            "[yellow]![/yellow] Could not connect to server. "
            "Falling back to local validation."
        )
        return _validate_local(files)

    for path in files:
        content = path.read_text()
        try:
            resp = client.post("/parse", content=content, headers={"Content-Type": "text/plain"})
            if resp.status_code != 200:
                data = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
                msg = data.get("error", data.get("message", f"HTTP {resp.status_code}"))
                errors.append((path, msg))
        except httpx.ConnectError:
            console.print(
                "[yellow]![/yellow] Server unreachable. "
                "Falling back to local validation."
            )
            client.close()
            return _validate_local(files)
        except Exception as exc:
            errors.append((path, str(exc)))

    client.close()
    return errors


@click.command()
@click.argument(
    "path",
    default="models",
    type=click.Path(exists=True),
)
@click.option(
    "--server",
    is_flag=True,
    default=False,
    help="Validate via a running Gearshift server (deeper analysis).",
)
def validate(path: str, server: bool) -> None:
    """Validate SysML v2 model files.

    PATH can be a file or directory (default: models/).
    """
    target = Path(path)
    if target.is_file():
        files = [target]
    else:
        files = find_models(target)

    if not files:
        console.print("[yellow]No .sysml files found.[/yellow]")
        sys.exit(0)

    console.print(f"Validating {len(files)} file(s)...")

    mode = "server" if server else load_config().validate.mode
    if mode == "server":
        cfg = load_config()
        errors = _validate_server(files, cfg.server.url)
    else:
        errors = _validate_local(files)

    # Report results
    passed = len(files) - len(errors)

    if errors:
        table = Table(title="Validation Errors", show_lines=True)
        table.add_column("File", style="red")
        table.add_column("Error")
        for file_path, msg in errors:
            table.add_row(str(file_path), msg)
        console.print(table)

    console.print()
    console.print(
        f"[green]{passed} passed[/green], "
        f"[red]{len(errors)} failed[/red] "
        f"({len(files)} total)"
    )

    if mode == "local" and not server:
        console.print(
            "\n[dim]Note: Local validation uses sysml2py (limited to "
            "Part/Item/Attribute). For deeper analysis, use --server "
            "with a running Gearshift instance.[/dim]"
        )

    sys.exit(1 if errors else 0)
