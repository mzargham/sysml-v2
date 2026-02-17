"""``sysml serve`` — manage the local SysML v2 API server."""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

import click
import httpx
from rich.console import Console

from sysml_v2.config import BACKENDS, load_config

console = Console()

# JWT token for local Flexo dev instance — "root" user with super_admins group (expires 2029)
# Payload: {"aud":"flexo-mms-audience","iss":"http://flexo-mms-services","username":"root","groups":["super_admins"],"exp":1893456000}
# Secret:  thisissomethingreallylong1234567801234567890
_FLEXO_JWT = (
    "eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9."
    "eyJhdWQiOiAiZmxleG8tbW1zLWF1ZGllbmNlIiwgImlzcyI6ICJodHRwOi8vZmxleG8tbW1zLXNlcnZpY2VzIiwgInVzZXJuYW1lIjogInJvb3QiLCAiZ3JvdXBzIjogWyJzdXBlcl9hZG1pbnMiXSwgImV4cCI6IDE4OTM0NTYwMDB9."
    "40no1-AmUNJSb0XXaq8lPs-yxpTJWEH67dHJkXbLCVI"
)


def _find_compose_file(backend: str | None = None) -> Path | None:
    """Locate the docker-compose file for the given backend.

    Walks up from cwd looking for ``docker/docker-compose.yml`` (flexo)
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


def _init_flexo_org(layer1_url: str = "http://localhost:8080") -> bool:
    """Initialize the Flexo MMS org after first startup.

    Waits for the layer1 service, then creates the ``sysmlv2`` org.
    This is idempotent — safe to call on every ``serve up``.
    """
    # Wait for layer1 to be reachable
    console.print("  Waiting for Flexo layer1 service...")
    for attempt in range(30):
        try:
            resp = httpx.get(f"{layer1_url}/", timeout=2)
            if resp.status_code < 500:
                break
        except httpx.ConnectError:
            pass
        time.sleep(2)
    else:
        console.print("[yellow]![/yellow] Layer1 service not reachable — org init skipped.")
        return False

    # Create the sysmlv2 org (idempotent PUT)
    console.print("  Initializing sysmlv2 org...")
    try:
        resp = httpx.put(
            f"{layer1_url}/orgs/sysmlv2",
            content='<> dct:title "sysml2"@en .',
            headers={
                "Content-Type": "text/turtle",
                "Authorization": f"Bearer {_FLEXO_JWT}",
            },
            timeout=10,
        )
        if resp.status_code < 400:
            console.print("[green]\u2713[/green] Flexo org initialized")
            return True
        else:
            console.print(
                f"[yellow]![/yellow] Org init returned HTTP {resp.status_code} "
                f"(may already exist — this is OK)"
            )
            return True
    except httpx.HTTPError as exc:
        console.print(f"[yellow]![/yellow] Org init failed: {exc}")
        return False


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

    cfg = load_config()
    backend = ctx.obj.get("backend") or cfg.server.backend

    console.print(f"Starting server using [bold]{compose_file.name}[/bold]...")

    if backend == "gearshift":
        console.print("  (first run builds from source — this may take a few minutes)")
        rc = _compose(["up", "-d", "--build"], compose_file)
    else:
        # Flexo uses pre-built images — no build step
        rc = _compose(["up", "-d"], compose_file)

    if rc != 0:
        sys.exit(rc)

    # Flexo requires org initialization after first startup
    if backend == "flexo":
        _init_flexo_org()

        # Confirm the SysML v2 API is responding
        api_url = cfg.server.url
        console.print(f"  Checking API at {api_url}...")
        for attempt in range(15):
            try:
                resp = httpx.get(f"{api_url}/projects", timeout=3)
                if resp.status_code < 500:
                    console.print(
                        f"[green]\u2713[/green] API server ready at {api_url}"
                    )
                    break
            except httpx.ConnectError:
                pass
            time.sleep(2)
        else:
            console.print(
                f"[yellow]![/yellow] API not yet responding at {api_url} — "
                "it may still be starting up"
            )


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
        resp = httpx.get(f"{url}/projects", timeout=3)
        console.print(
            f"[green]\u2713[/green] API server reachable at {url} "
            f"(HTTP {resp.status_code})"
        )
    except httpx.ConnectError:
        console.print(f"[yellow]![/yellow] API server not reachable at {url}")
