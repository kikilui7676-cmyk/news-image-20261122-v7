#!/usr/bin/env python3
"""make.fun entry point: copy entry.png to the output directory.

Standard library only. The output directory comes from the
MAKEFUN_OUTPUT_DIR environment variable (default /output).
"""

import os
import shutil
from pathlib import Path


def main():
    src = Path(__file__).resolve().parent / "entry.png"
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, out_dir / "entry.png")


if __name__ == "__main__":
    main()
