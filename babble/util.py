import io
import sys
import typing

import coquille.sequences

from babble.window import EMPTY_PIXEL
from babble.window import Window


def positive_int(raw_value: str) -> int:
    """
    Refined integer "type" for `argparse`.
    """

    value = int(raw_value)

    if value <= 0:
        raise ValueError("value must be strictly positive")

    return value


def is_fully_filled(window: Window) -> bool:
    """
    Return `True` if the window has no empty pixel else `False`.
    """

    return EMPTY_PIXEL not in window.pixels


def offset_write(
    string: str,
    x: int,
    y: int,
    output: typing.TextIO | None = None,
) -> None:
    """
    Write the provided `string` to `output` with an offset (`x`, `y`).

    If `output` is not provided, it defaults to `sys.stdout`.
    """

    _output = output or sys.stdout
    buffer = io.StringIO()

    buffer.write("\n" * y)

    for line in string.splitlines():
        print(" " * x + line + "\x1b[49m", file=buffer)

    coquille.apply(coquille.sequences.cursor_position(0, 0), file=_output)
    _output.write(buffer.getvalue())


def make_keys_hint(**descriptions: str) -> str:
    """
    Build a nice-looking printable string of the keys hints in the status bar.
    """

    return " \x1b[2m│\x1b[22m ".join(
        f"\x1b[1m{key}\x1b[22m: \x1b[95m{description}\x1b[39m"
        for key, description in descriptions.items()
    )
