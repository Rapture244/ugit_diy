# src/ugit_diy/__main__.py
"""ugit_diy package entry point.

Allows running the package with:
    python -m ugit_diy
"""

# stdlib
from __future__ import annotations

import sys

# 3rd party
# Local
from ugit_diy.cli import main

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
