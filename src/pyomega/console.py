# src/pyomega/console.py
import click

from . import __version__


@click.command()
@click.version_option(version=__version__)
def main():
    """The PyOmega project."""
    click.echo("PyOmega")