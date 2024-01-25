import argparse
import os
import typing

from babble.app import App
from babble.app import AppParams
from babble.util import positive_int


class BabbleNamespace(typing.Protocol):
    randomize_at_launch: bool
    immersive: bool
    pixels_per_step: int


def parse_args() -> BabbleNamespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("--randomize-at-launch", "-rl", action="store_true")
    parser.add_argument("--immersive", "-i", action="store_true")
    parser.add_argument("--pixels-per-step", "-pps", type=positive_int, default=1_000)

    return typing.cast(BabbleNamespace, parser.parse_args())


def main() -> int:
    namespace = parse_args()
    app_params: AppParams = {
        "is_randomizing": namespace.randomize_at_launch,
        "immersive": namespace.immersive,
        "pixels_per_step": namespace.pixels_per_step,
    }

    with App("Babble", **app_params) as app:
        app.run()

    return os.EX_OK
