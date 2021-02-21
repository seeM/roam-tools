#! /usr/bin/env python3
"""
Rename page links to daily notes from the Roam format to ISO format.
"""
import argparse
import re
from pathlib import Path

from utils import date_from_roam_match, ROAM_DATE_PATTERN


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("dir")
args = parser.parse_args()

args.dir = Path(args.dir)

for p in args.dir.iterdir():
    if not p.is_file() or p.suffix != ".md":
        continue
    with open(p) as f:
        text = f.read()

    original = text
    count = 0
    while True:
        match = re.search(ROAM_DATE_PATTERN, text)
        if match is None:
            break
        date = date_from_roam_match(match)
        span = match.span()
        text = text[:span[0]] + str(date) + text[span[1]:]
        count += 1

    with open(p, "w") as f:
        f.write(text)

    if count:
        print(f"Modified {count} dates in '{p}'")
