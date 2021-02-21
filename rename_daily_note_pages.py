#! /usr/bin/env python3
"""
Rename daily notes markdown files from the Roam format to ISO format.
"""
import argparse
from pathlib import Path

from utils import date_from_roam_string


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("dir")
args = parser.parse_args()

args.dir = Path(args.dir)

for p in args.dir.iterdir():
    if not p.is_file():
        continue
    date = date_from_roam_string(p.stem)
    new_p = p.parent / f"{date}.md"
    print(p.name, "->", new_p)
    p.rename(new_p)
