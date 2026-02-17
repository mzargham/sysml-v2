"""SysML v2 CLI — ``sysml`` command group."""

import click

from sysml_v2 import __version__
from sysml_v2.cli.init_cmd import init_cmd
from sysml_v2.cli.serve import serve
from sysml_v2.cli.validate import validate


@click.group()
@click.version_option(__version__, prog_name="sysml")
def main() -> None:
    """SysML v2 toolchain — model development and analysis."""


main.add_command(init_cmd, name="init")
main.add_command(serve)
main.add_command(validate)
