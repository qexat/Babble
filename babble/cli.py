# pyright: reportUnusedCallResult = false
import argparse
import os
import typing

from babble.app import App
from babble.app import AppParams
from babble.builtins import themes
from babble.util import emit_warning_pps_performance
from babble.util import positive_int
from babble.util import prompt_confirmation
from babble.util import should_warn_pps_performance


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
    app_params: AppParams = {
        "is_randomizing": namespace.randomize_at_launch,
        "immersive": namespace.immersive,
        "pixels_per_step": namespace.pixels_per_step,
        "theme": themes.get_unchecked(namespace.theme),
    }

    if should_warn_pps_performance(app_params["pixels_per_step"]):
        emit_warning_pps_performance(app_params["pixels_per_step"])

        if not prompt_confirmation():
            return os.EX_DATAERR

    with App("Babble", **app_params) as app:
        app.run()

    return os.EX_OK
