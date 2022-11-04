"""Console script for py_taplo."""

import atexit
import os
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile

import click
import click.core

from .exception_handler import ExceptionHandler
from .shell import _shell_completion
from .taplo import Taplo
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


@cli.command()
@click.option(
    "-p",
    "--python",
    "output_format",
    flag_value="dict",
    help="select python dict format",
)
@click.option(
    "-j",
    "--json",
    "output_format",
    flag_value="json",
    default=True,
    help="select json format",
)
@click.option(
    "-t",
    "--toml",
    "output_format",
    flag_value="toml",
    help="select toml ouput format",
)
@click.option(
    "-r",
    "--raw",
    "output_format",
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
    default="-",
)
@click.pass_context
def get(ctx, selector, output_format, toml_file):
    """output toml file in the selected format, optionally selecting sections or elements"""
    if toml_file.name == "-":
        toml_file = _buffer_file(toml_file)
    taplo = ctx.obj["taplo"]
    func = {
        "json": taplo.json,
        "dict": taplo.dict,
        "toml": taplo.toml,
        "value": taplo.get,
    }
    click.echo(func[output_format](toml_file, selector=selector))


@cli.command
@click.option(
    "-i",
    "--in-place",
    is_flag=True,
    help="overwrite the file with the formatted output",
)
@click.option('-v', '--verbose', is_flag=True, help='verbose output')
@click.argument(
    "toml_file",
    type=click.Path(
        dir_okay=False,
        allow_dash=True,
        readable=True,
        exists=True,
        path_type=Path,
    ),
    default="-",
)
@click.pass_context
def fmt(ctx, in_place, verbose, toml_file):
    """reformat toml file"""
    if toml_file.name == "-":
        toml_file = _buffer_file(toml_file)
        in_place = False
    opts = dict(in_place=in_place)
    if verbose:
        opts['verbose'] = None
    click.echo(ctx.obj["taplo"].fmt(toml_file, **opts))


@cli.command
@click.option(
    "-i",
    "--in-place",
    is_flag=True,
    help="overwrite the file with the formatted output",
)
@click.option('-v', '--verbose', is_flag=True, help='verbose output')
@click.argument(
    "toml_file",
    type=click.Path(
        dir_okay=False,
        allow_dash=True,
        readable=True,
        exists=True,
        path_type=Path,
    ),
    default="-",
)
@click.pass_context
def lint(ctx, in_place, verbose, toml_file):
    """verify syntax of toml file writing errors to stdout"""
    taplo = ctx.obj["taplo"]
    if toml_file.name == "-":
        toml_file = _buffer_file(toml_file)
        in_place=False
    opts = dict(in_place=in_place)
    if verbose:
        opts['verbose'] = None
    click.echo(taplo.lint(toml_file, **opts))


if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover
