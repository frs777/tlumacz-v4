"""Command-line bootstrap for Tlumacz V4."""

import argparse

from . import __version__


def main() -> int:
    parser = argparse.ArgumentParser(prog="tlumacz")
    parser.add_argument("--version", action="version", version=__version__)
    parser.parse_args()
    return 0
