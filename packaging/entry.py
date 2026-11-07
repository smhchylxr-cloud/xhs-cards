"""Entry point for the one-file Windows build.

PyInstaller wants a script, not a console_entry, so this exists only for packaging.
"""

import sys

from xhs_cards.cli import main

if __name__ == "__main__":
    sys.exit(main())
