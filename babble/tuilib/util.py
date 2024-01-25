# pyright: reportMissingTypeStubs = false, reportUnusedCallResult = false
import collections.abc
import io
import sys
import typing

import coquille.sequences
import outspin


_T = typing.TypeVar("_T")


UPPER_LIMIT_PIXELS_PER_STEP = 50_000


def positive_int(raw_value: str) -> int:
    """
    Refined integer "type" for `argparse`.
    """

    value = int(raw_value)

    if value <= 0:
        raise ValueError("value must be strictly positive")

    return value


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


def all_indices(
    sequence: collections.abc.Sequence[_T],
    item: _T,
) -> collections.abc.Iterator[int]:
    """
    Get all the indices where the `item` is present.
    """

    for index, _item in enumerate(sequence):
        if _item == item:
            yield index


def get_items(
    sequence: collections.abc.Sequence[_T],
    *indices: int,
) -> collections.abc.Iterator[_T]:
    """
    Basically a batch of `__getitem__`s.
    """

    for index in indices:
        yield sequence[index]


def merge_duplicate_hints(hints: dict[str, str], joiner: str = "/") -> dict[str, str]:
    """
    Merge keys with the same description into one.

    >>> merge_duplicate_hints({"q": "quit", "esc": "quit"})
    {"q/esc": "quit"}
    """

    result: dict[str, str] = {}
    keys = list(hints.keys())
    values = list(hints.values())

    for index, value in enumerate(values):
        if values.count(value) > 1:
            key = joiner.join(get_items(keys, *all_indices(values, value)))
        else:
            key = keys[index]

        if key not in result:
            result[key] = value

    return result


def keyhints_repr(**descriptions: str) -> str:
    """
    Build a nice-looking printable string of the keys hints in the status bar.
    """

    return " \x1b[2m│\x1b[22m ".join(
        f"\x1b[1m{key}\x1b[22m: \x1b[95m{description}\x1b[39m"
        for key, description in merge_duplicate_hints(
            descriptions,
            "\x1b[22m/\x1b[1m",
        ).items()
    )


def should_warn_pps_performance(pixels_per_step: int) -> bool:
    """
    Check if the user should be warned about potential performance impact of
    high pixels-per-step values.
    """

    return pixels_per_step > UPPER_LIMIT_PIXELS_PER_STEP


def emit_warning_pps_performance(pixels_per_step: int) -> None:
    print(
        f"\x1b[1;33mWARNING:\x1b[22;39m \x1b[1;96m{pixels_per_step:,}\x1b[22;39m is higher than the "
        f"recommended max pixels-per-step value of \x1b[1;96m{UPPER_LIMIT_PIXELS_PER_STEP:,}\x1b[22;39m. "
        "\x1b[33mIt might impact performance.\x1b[39m",
        file=sys.stderr,
    )


def prompt_confirmation() -> bool:
    """
    Prompt a confirmation to the user.

    Returns `True` if they confirmed, `False` otherwise.
    """

    sys.stderr.write("Do you want to continue? (y/n) ")
    sys.stderr.flush()

    return outspin.get_key() in ("y", "Y")
