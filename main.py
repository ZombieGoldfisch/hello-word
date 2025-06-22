"""Application entry point that launches the command line interface.

Routes are visualized automatically using :func:`save_route_map` from the
``visualization_osmnx`` module.
"""
from cli import run_cli
import sys

if __name__ == "__main__":
    nt = sys.argv[1] if len(sys.argv) > 1 else "drive"
    run_cli(network_type=nt)
