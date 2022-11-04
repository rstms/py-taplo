"""Console script for py_taplo."""

import atexit
import os
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile

import click
import click.core

from .taplo import Taplo

from .exception_handler import ExceptionHandler
from .shell import _shell_completion
from .version import __timestamp__, __version__

header = f"{__name__.split('.')[0]} v{__version__} {__timestamp__}"


def _ehandler(ctx, option, debug):
    ctx.obj = dict(ehandler=ExceptionHandler(debug))
    ctx.obj["debug"] = debug


def _buffer_file(input_file):
    with NamedTemporaryFile("w+", delete=False) as bfp:
        with click.open_file(input_file) as ifp:
            bfp.write(ifp.read())
        filename = bfp.name
    atexit.register(os.unlink, str(filename))
    return filename


@click.group("ptt", context_settings={"auto_envvar_prefix": "PTT"})
@click.version_option(message=header)
@click.option(
    "-d",
    "--debug",
    is_eager=True,
    is_flag=True,
    callback=_ehandler,
    help="debug mode",
)
@click.option(
    "--shell-completion",
    is_flag=False,
    flag_value="[auto]",
    callback=_shell_completion,
    help="configure shell completion",
)
@click.pass_context
def cli(ctx, debug, shell_completion):
    """py_taplo top-level help"""
    ctx.obj["taplo"] = Taplo()


@cli.command
@click.pass_context
def version(ctx):
    """output taplo version"""
    click.echo(ctx.obj["taplo"].version())


@cli.command
@click.pass_context
@click.option(
    "-p",
    "--python",
    "_format",
    flag_value="dict",
    help="select python dict format",
)
@click.option(
    "-j", "--json", "_format", flag_value="json", help="select json format"
)
@click.option(
    "-t",
    "--toml",
    "_format",
    flag_value="toml",
    help="select toml ouput format",
)
@click.option(
    "-r",
    "--raw",
    "_format",
    flag_value="value",
    help="unformatted data (use with selector)",
)
@click.option(
    "-s",
    "--selector",
    type=str,
    help="element selection key ex: 'project.name'",
)
@click.argument(
    "toml_file",
    type=click.Path(
        dir_okay=False,
        allow_dash=True,
        readable=True,
        exists=True,
        path_type=Path,
    ),
)
@click.pass_context
def get(ctx, _format, selector, toml_file):
    """output toml file in the selected format, optionally selecting sections or elements"""
    _format = _format or "json"
    if toml_file.name == "-":
        toml_file = _buffer_file(toml_file)
    click.echo(
        ctx.obj["taplo"].get(
            toml_file, output_format=_format, selector=selector
        )
    )


@cli.command
@click.pass_context
@click.argument(
    "toml_file",
    type=click.Path(
        dir_okay=False,
        allow_dash=True,
        readable=True,
        exists=True,
        path_type=Path,
    ),
)
def fmt(ctx, toml_file):
    """reformat toml file"""
    if toml_file.name == "-":
        toml_file = _buffer_file(toml_file)
    click.echo(ctx.obj["taplo"].fmt(toml_file))


@cli.command
@click.pass_context
@click.argument(
    "toml_file",
    type=click.Path(
        dir_okay=False,
        allow_dash=True,
        readable=True,
        exists=True,
        path_type=Path,
    ),
)
def lint(ctx, toml_file):
    """verify syntax of toml file writing errors to stdout"""
    taplo = ctx.obj["taplo"]
    if toml_file.name == "-":
        toml_file = _buffer_file(toml_file)
    click.echo(taplo.lint(toml_file))


if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover
