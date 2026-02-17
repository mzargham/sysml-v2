"""``sysml init`` — scaffold a new SysML v2 project."""

from __future__ import annotations

import shutil
import subprocess
from importlib import resources
from pathlib import Path
from string import Template

import click
from rich.console import Console

console = Console()

# Mapping from template path → output path for files that need renaming.
# Template names avoid dots/underscores that confuse git or IDEs.
_RENAMES: dict[str, str] = {
    "gitignore": ".gitignore",
    "_vscode": ".vscode",
}


def _template_root() -> Path:
    """Return the filesystem path to the bundled templates directory."""
    return Path(str(resources.files("sysml_v2") / "templates"))


def _copy_templates(dest: Path, project_name: str, backend: str) -> None:
    """Copy template files to *dest*, applying renames and substitutions."""
    src = _template_root()

    for item in sorted(src.rglob("*")):
        rel = item.relative_to(src)

        # Skip the alternative docker-compose based on chosen backend
        if backend == "flexo" and rel.name == "docker-compose.gearshift.yml":
            continue
        if backend == "gearshift" and rel.name == "docker-compose.yml":
            continue

        # Apply renames to each path component
        parts = []
        for part in rel.parts:
            parts.append(_RENAMES.get(part, part))
        out = dest / Path(*parts)

        if item.is_dir():
            out.mkdir(parents=True, exist_ok=True)
            continue

        out.parent.mkdir(parents=True, exist_ok=True)

        if item.suffix == ".tpl":
            # Template file — substitute variables and drop .tpl extension
            out = out.with_suffix("")
            content = item.read_text()
            content = Template(content).safe_substitute(project_name=project_name)
            out.write_text(content)
        else:
            shutil.copy2(item, out)

    # For gearshift, rename the compose file to the standard name
    if backend == "gearshift":
        gs = dest / "docker" / "docker-compose.gearshift.yml"
        if gs.exists():
            gs.rename(dest / "docker" / "docker-compose.yml")


@click.command("init")
@click.argument("path", default=".", type=click.Path())
@click.option(
    "--backend",
    type=click.Choice(["flexo", "gearshift"]),
    default="flexo",
    help="API server backend (default: flexo).",
)
@click.option("--yes", "-y", is_flag=True, help="Skip interactive prompts.")
def init_cmd(path: str, backend: str, yes: bool) -> None:
    """Scaffold a new SysML v2 project.

    PATH is the target directory (default: current directory).
    """
    dest = Path(path).resolve()
    project_name = dest.name

    if dest.exists() and any(dest.iterdir()):
        # Directory not empty — confirm
        if not yes and not click.confirm(
            f"Directory '{dest}' is not empty. Continue?"
        ):
            raise SystemExit(0)
    dest.mkdir(parents=True, exist_ok=True)

    console.print(f"[bold]Initializing SysML v2 project:[/bold] {project_name}")
    console.print(f"  Backend: {backend}")
    console.print()

    # 1. Copy templates
    _copy_templates(dest, project_name, backend)
    console.print("[green]\u2713[/green] Project files created")

    # 2. git init
    if not (dest / ".git").exists():
        subprocess.run(["git", "init", str(dest)], capture_output=True, check=False)
        console.print("[green]\u2713[/green] Git repository initialized")

    # 3. Clone standard library
    lib_dest = dest / "lib" / "SysML-v2-Release"
    if not lib_dest.exists():
        if yes or click.confirm("Clone the SysML v2 standard library?", default=True):
            console.print("  Cloning standard library...")
            result = subprocess.run(
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    "https://github.com/Systems-Modeling/SysML-v2-Release.git",
                    str(lib_dest),
                ],
                capture_output=True,
            )
            if result.returncode == 0:
                console.print("[green]\u2713[/green] Standard library cloned")
            else:
                console.print(
                    "[yellow]![/yellow] Could not clone standard library. "
                    "Clone manually:\n"
                    f"  git clone --depth 1 https://github.com/Systems-Modeling/"
                    f"SysML-v2-Release.git {lib_dest}"
                )

    console.print()
    console.print("[bold green]Done![/bold green] Next steps:")
    console.print(f"  cd {dest.name}")
    console.print("  code .                  # open in VS Code")
    console.print("  sysml serve up          # start the API server (builds on first run)")
    console.print("  sysml validate models/  # validate your models")
