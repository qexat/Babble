# pyright: reportUnusedCallResult = false
import argparse
import os
import typing

from babble.babble import BabbleContext
from babble.babble import BabbleSettings
from babble.builtins import themes
from babble.gol import DEFAULT_SETTINGS
from babble.gol import GoLContext
from babble.tuilib.app import App
from babble.tuilib.util import emit_warning_pps_performance
from babble.tuilib.util import positive_int
from babble.tuilib.util import prompt_confirmation
from babble.tuilib.util import should_warn_pps_performance


class BabbleNamespace(typing.Protocol):
    randomize_at_launch: bool
    immersive: bool
    pixels_per_step: int
    theme: str


def parse_args() -> BabbleNamespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("--randomize-at-launch", "-rl", action="store_true")
    parser.add_argument("--immersive", "-i", action="store_true")
    parser.add_argument("--pixels-per-step", "-pps", type=positive_int, default=1_000)
    parser.add_argument(
        "--theme",
        choices=themes.list().keys(),
        default="babble",
    )

    return typing.cast(BabbleNamespace, parser.parse_args())


def main() -> int:
    namespace = parse_args()

    context_settings: BabbleSettings = {
        "pixels_per_step": namespace.pixels_per_step,
        "theme": themes.get_unchecked(namespace.theme),
    }

    if should_warn_pps_performance(context_settings["pixels_per_step"]):
        emit_warning_pps_performance(context_settings["pixels_per_step"])

        if not prompt_confirmation():
            return os.EX_DATAERR

    with App("Babble", BabbleContext, immersive=namespace.immersive) as app:
        app.run(context_settings)

    return os.EX_OK


def main_gol() -> int:
    with App("Game of Life", GoLContext) as app:
        app.run(DEFAULT_SETTINGS)

    return os.EX_OK
