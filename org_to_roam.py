#! /usr/bin/env python3
import argparse
import re
import sys
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from typing import List
from typing import Optional
from typing import Sequence

import orgparse


BULLETS_RE = r"^(\-|\*||[0-9]+\.)\s+"


@dataclass
class Block:
    string: str
    children: List["Block"] = field(default_factory=list)

    INDENT = 4
    BULLET = "-"

    def print(self, level: int = 0) -> str:
        indent = level * self.INDENT * " "
        string = indent + self.BULLET + " " + self.string + "\n"
        for c in self.children:
            string += c.print(level + 1)
        return string

    def __str__(self) -> str:
        return self.print()


def parse_javascript_datetime(timestamp: int) -> datetime:
    return datetime.utcfromtimestamp(timestamp / 1000)


@dataclass
class Page:
    title: str
    children: List[Block]

    def __str__(self) -> str:
        s = ""
        s += "".join(str(c) for c in self.children)
        return s


def org_to_roam(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Convert org FILE to Roam markdown.",
    )
    parser.add_argument("file")
    args = parser.parse_args()

    org_root = orgparse.load(args.file)
    roam_page = org_root_to_roam_page(org_root)

    print(roam_page)

    return 0


def org_root_to_roam_page(org_root) -> Page:
    splitted = str(org_root).strip().split("\n", 1)
    title = splitted[0]
    body = splitted[1] if len(splitted) > 1 else None

    # TODO: Handle non-date titles
    title = title.replace("#+title: ", "")
    splitted = title.split(",")
    if len(splitted) > 1:
        maybe_date = splitted[1].strip()
        try:
            date = datetime.strptime(maybe_date, "%d %B %Y")
        except ValueError:
            title = title
        else:
            title = format_roam_date(date)
    else:
        title = title

    children = []

    if body is not None:
        body = body.strip()
        first_child = Block(body)
        children.append(first_child)

    children += [org_node_to_roam_block(c) for c in org_root.children]
    return Page(
        title=title,
        children=children,
    )


def org_node_to_roam_block(org_node) -> Block:
    heading = org_node.heading.strip()

    # Parse todo states to Roam todos
    if org_node.todo == "TODO":
        heading = "{{[[TODO]]}} " + heading
    elif org_node.todo == "DONE":
        heading = "{{[[DONE]]}} " + heading
    else:
        heading = re.sub("^CANCELLED ", "{{[[CANCELLED]]}}", heading)

    block = Block(heading)

    body = org_node.body.strip()
    if body:
        # Split paragraphs into sibling blocks
        # TODO: All of below hints that we probably want an org markup parser
        for paragraph in body.split("\n\n"):
            # TODO: Don't remove newlines before bulleted points.
            lines = [x.strip() for x in paragraph.split("\n")]

            result = []
            while lines:
                # Consume the current line
                line = lines.pop(0)

                # Strip the bullet / number chars, just get the body
                # text.
                line = re.sub(BULLETS_RE, "", line)

                if not lines:
                    # We're at the last line, there's no next line
                    result.append(line)
                else:
                    # Peek the next line
                    next_line = lines[0]

                    if re.match(BULLETS_RE, next_line):
                        # It's a list of some sort, treat this as its own line
                        # and move on
                        result.append(line)
                    else:
                        # It's wrapped text, consume the next line, merge it
                        # onto the current line, and pop the result back into
                        # the lines stack for the next iteration.
                        next_line = lines.pop(0)
                        merged = line + " " + next_line
                        lines.insert(0, merged)

            final = []
            for r in result:
                # Convert markup
                r = re.sub(r"\[file\:[^\]]*\]", "", r)
                r = re.sub(r"\[\[([^\]]*)\]\[([^\]]*)\]\]", "[\\2](\\1)", r)  # links
                # TODO: Don't have working italics for now because it breaks links
                r = re.sub(r"\=([^\=]+)\=", "`\\1`", r)
                r = re.sub(r"\/([^\/]+)\/", "__\\1__", r)
                # r = re.sub(r"(https?\:\/.*)(__)", "\\1/", r)
                r = re.sub(r"\*([^\*]+)\*", "**\\1**", r)
                r = re.sub(r"\#\+begin_src ", "```", r)
                r = re.sub(r"\#\+end_src", "```", r)
                r = re.sub(r"^\[ \]", "{{[[TODO]]}}", r)
                r = re.sub(r"^\[X\]", "{{[[DONE]]}}", r)
                final.append(r)

            block.children += [Block(x) for x in final]

    block.children.extend(
        [org_node_to_roam_block(c) for c in org_node.children],
    )

    return block


def format_roam_date(dt: datetime) -> str:
    year = dt.year
    month = dt.strftime("%B")
    day = make_ordinal(dt.day)
    return f"{month} {day}, {year}"


# From: https://stackoverflow.com/a/50992575
def make_ordinal(n):
    """
    Convert an integer to its ordinal representation.

    Examples:
    >>> make_ordinal(0)
    '0th'
    >>> make_ordinal(3)
    '3rd'
    >>> make_ordinal(122)
    '122nd'
    >>> make_ordinal(213)
    '213th'
    """
    n = int(n)
    suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    return str(n) + suffix


if __name__ == "__main__":
    sys.exit(org_to_roam())
