"""``sysml serve`` — manage the local SysML v2 API server."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import click
import httpx
from rich.console import Console

from sysml_v2.config import BACKENDS, load_config

console = Console()


def _find_compose_file(backend: str | None = None) -> Path | None:
    """Locate the docker-compose file for the given backend.

    Walks up from cwd looking for ``docker/docker-compose.yml`` (gorenje)
    or ``docker/docker-compose.gearshift.yml`` (gearshift).
    Falls back to the plain ``docker-compose.yml`` regardless of backend.
    """
    cfg = load_config()
    backend = backend or cfg.server.backend

    if backend == "gearshift":
        names = ["docker-compose.gearshift.yml", "docker-compose.yml"]
    else:
        names = ["docker-compose.yml"]

    current = Path.cwd().resolve()
    for directory in (current, *current.parents):
        docker_dir = directory / "docker"
        for name in names:
            candidate = docker_dir / name
            if candidate.is_file():
                return candidate
    return None


def _compose(args: list[str], compose_file: Path) -> int:
    """Run ``docker compose -f <file> <args>`` and return the exit code."""
    cmd = ["docker", "compose", "-f", str(compose_file), *args]
    result = subprocess.run(cmd)
    return result.returncode


@click.group()
@click.option(
    "--backend",
    type=click.Choice(BACKENDS),
    default=None,
    help="Override API server backend from sysml.toml.",
)
@click.pass_context
def serve(ctx: click.Context, backend: str | None) -> None:
    """Manage the local SysML v2 API server (Docker)."""
    ctx.ensure_object(dict)
    ctx.obj["backend"] = backend


@serve.command()
@click.pass_context
def up(ctx: click.Context) -> None:
    """Start the API server."""
    compose_file = _find_compose_file(ctx.obj.get("backend"))
    if compose_file is None:
        console.print("[red]Error:[/red] No docker-compose file found.")
        console.print("  Run 'sysml init' first, or check you're in a SysML project.")
        sys.exit(1)
    console.print(f"Starting server using [bold]{compose_file.name}[/bold]...")
    console.print("  (first run builds from source — this may take a few minutes)")
    sys.exit(_compose(["up", "-d", "--build"], compose_file))


@serve.command()
@click.pass_context
def down(ctx: click.Context) -> None:
    """Stop the API server."""
    compose_file = _find_compose_file(ctx.obj.get("backend"))
    if compose_file is None:
        console.print("[red]Error:[/red] No docker-compose file found.")
        sys.exit(1)
    sys.exit(_compose(["down"], compose_file))


@serve.command()
@click.pass_context
def logs(ctx: click.Context) -> None:
    """Tail API server logs."""
    compose_file = _find_compose_file(ctx.obj.get("backend"))
    if compose_file is None:
        console.print("[red]Error:[/red] No docker-compose file found.")
        sys.exit(1)
    sys.exit(_compose(["logs", "-f"], compose_file))


@serve.command()
@click.pass_context
def pull(ctx: click.Context) -> None:
    """Pull latest Docker images."""
    compose_file = _find_compose_file(ctx.obj.get("backend"))
    if compose_file is None:
        console.print("[red]Error:[/red] No docker-compose file found.")
        sys.exit(1)
    sys.exit(_compose(["pull"], compose_file))


@serve.command()
@click.pass_context
def status(ctx: click.Context) -> None:
    """Check if the API server is running."""
    compose_file = _find_compose_file(ctx.obj.get("backend"))
    if compose_file is None:
        console.print("[red]Error:[/red] No docker-compose file found.")
        sys.exit(1)

    # Check container status
    _compose(["ps"], compose_file)

    # Check API health
    cfg = load_config()
    url = cfg.server.url
    console.print()
    try:
        resp = httpx.get(f"{url}/", timeout=3)
        console.print(
            f"[green]\u2713[/green] API server reachable at {url} "
            f"(HTTP {resp.status_code})"
        )
    except httpx.ConnectError:
        console.print(f"[yellow]![/yellow] API server not reachable at {url}")
