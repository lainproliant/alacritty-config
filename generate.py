#!/usr/bin/env python
# --------------------------------------------------------------------
# generate.py
#
# Author: Lain Musgrove (lain.proliant@gmail.com)
# Date: Thursday January 2, 2020
#
# Distributed under terms of the MIT license.
# --------------------------------------------------------------------
import argparse
import json
import os
import random
import re
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from jinja2 import Template


# -------------------------------------------------------------------
def load_base16():
    xdefaults_file = Path.home() / ".Xdefaults"

    base16 = {}
    with open(xdefaults_file, "r") as infile:
        for line in infile.readlines():
            match = re.match(r"#define (base.*) (#.*)$", line.strip())
            if match:
                base16[match.group(1)] = match.group(2)
    return base16


# -------------------------------------------------------------------
BASE16 = load_base16()
BG_HEX = int(BASE16['base00'][1:], 16)

# -------------------------------------------------------------------
def hex_to_rgb(color):
    return ((color & 0xFF0000) >> 16, (color & 0x00FF00) >> 8, (color & 0x0000FF) >> 0)

BG_RGB = hex_to_rgb(BG_HEX)

# -------------------------------------------------------------------
class Config:
    red: int = BG_RGB[0]
    green: int = BG_RGB[1]
    blue: int = BG_RGB[2]
    extra: Dict[str, Any] = {'alpha': 1.0}
    random = False
    use_xdefaults = False

    @property
    def parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser()
        r, g, b = hex_to_rgb(BG_HEX)
        parser.add_argument("-r", dest="red", type=int)
        parser.add_argument("-g", dest="green", type=int)
        parser.add_argument("-b", dest="blue", type=int)
        parser.add_argument("-a", dest="alpha", type=float)
        parser.add_argument("-R", "--random", action="store_true", default=False)
        return parser

    def randomize(self) -> int:
        """ Gives a random value between 0 and 128, with a 1/3 chance of being 0. """
        return random.choices([0, 1], [1, 2])[0] * random.randint(0, 128)

    def parse_args(self):
        self.parser.parse_args(namespace=self)
        if self.random:
            self.red = self.randomize()
            self.green = self.randomize()
            self.blue = self.randomize()
        if self.alpha:
            self.extra['alpha'] = self.alpha
        return self

    @property
    def color(self) -> Tuple[int, int, int, float]:
        return (self.red, self.green, self.blue, self.extra['alpha'])

    @color.setter
    def color(self, value: Tuple[int, int, int, float]):
        self.red, self.green, self.blue, self.extra['alpha'] = value


# -------------------------------------------------------------------
def load_template():
    with open("alacritty.yml.jinja", "r") as infile:
        return Template(infile.read())


# -------------------------------------------------------------------
def load_font_config():
    with open(os.path.expanduser("~/.font/config.json"), "r") as infile:
        return json.load(infile)


# -------------------------------------------------------------------
def main():
    config = Config()

    try:
        with open("extra.json", "r") as infile:
            config.extra = json.load(fp=infile)
    except Exception:
        print("Couldn't load extra.json, using defaults.", file=sys.stderr)

    config = config.parse_args()
    template = load_template()
    font_config = load_font_config()
    print(template.render(config=config, **font_config))

    with open("extra.json", "w") as outfile:
        json.dump(config.extra, fp=outfile)


# -------------------------------------------------------------------
if __name__ == "__main__":
    main()
