"""Entry point for the Panoptikon application."""

import sys
from typing import List, Optional

import click

from panoptikon.config import config_manager
from panoptikon.ui import app_launcher


@click.group()
def cli() -> None:
    """Panoptikon file search utility.

    A high-performance file search application inspired by the Windows "Everything" utility.
    """
    pass


@cli.command()
@click.option("--config-path", "-c", help="Path to the configuration file.")
def run(config_path: Optional[str] = None) -> None:
    """Run the Panoptikon application.

    Args:
        config_path: Optional path to a configuration file.
    """
    # Load configuration
    if config_path:
        config_manager.load_config(config_path)
    else:
        config_manager.load_default_config()

    # Launch the application
    app_launcher.launch()


@cli.command()
@click.option("--path", "-p", help="Path to index.")
def index(path: Optional[str] = None) -> None:
    """Index a directory without starting the full application.

    Args:
        path: Optional path to index. If not provided, the default paths will be indexed.
    """
    from panoptikon.index import indexer

    # Load configuration
    config_manager.load_default_config()

    # Run indexer
    if path:
        indexer.index_path(path)
    else:
        indexer.index_default_paths()

    click.echo("Indexing complete.")


def main(args: Optional[List[str]] = None) -> int:
    """Main function called when the module is run directly.

    Args:
        args: Command line arguments.

    Returns:
        int: Exit code.
    """
    try:
        if args is None:
            args = sys.argv[1:]
        cli(args)
        return 0
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        return 1


if __name__ == "__main__":
    sys.exit(main()) 