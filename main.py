"""Application entry point that launches the command line interface.

Routes are visualized automatically using :func:`save_route_map` from the
``visualization_osmnx`` module.
"""
from cli import run_cli
if __name__ == "__main__":
    run_cli()
