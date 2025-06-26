"""Application entry point that launches the command line interface.

Routes are visualized automatically using :func:`save_route_map` from the
``visualization_osmnx`` module.
"""
from cli import run_cli
from gui_tkinter import RoutingGUI
import sys

def main() -> None:
    """Start the command line interface or GUI depending on arguments."""
    if len(sys.argv) > 1 and sys.argv[1] == "gui":
        RoutingGUI().run()
    else:
        nt = sys.argv[1] if len(sys.argv) > 1 else "drive"
        run_cli(network_type=nt)


if __name__ == "__main__":
    main()
