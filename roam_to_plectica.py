#! /usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from typing import List


@dataclass
class Block:
    string: str
    children: List[Block] = field(default_factory=list)


@dataclass
class Page:
    title: str
    children: List[Block]


def flatten(input_list, new_list=None):
    if new_list is None:
        new_list = []

    for item in input_list:
        print(item['string'])

        new_list += [item['string']]

        if 'children' not in item or not item['children']:
            pass
        else:
            flatten(item['children'], new_list)

    return new_list


parser = argparse.ArgumentParser()
parser.add_argument("input")
args = parser.parse_args()

with open(args.input) as f:
    data = json.load(f)

page = data[0]
page['string'] = page['title']
cards = flatten([page])
for card in cards:
    print(card)
