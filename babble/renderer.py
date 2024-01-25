from __future__ import annotations

import collections.abc
import dataclasses
import typing

from babble.window import Coordinates
from babble.window import EMPTY_PIXEL
from babble.window import RGBColor
from babble.window import Window

_T = typing.TypeVar("_T")
_U = typing.TypeVar("_U")


PipelineResult: typing.TypeAlias = tuple[Coordinates, _T]
PipelineFunction: typing.TypeAlias = collections.abc.Callable[
    [Coordinates, _T, int, int], PipelineResult[_U],
]

_EMPTY_PIXEL_RENDERING = "\x1b[49m "


class RenderingPipeline(typing.Generic[_T], typing.NamedTuple):
    """
    A pipeline to make the rendering cleaner.
    """

    coordinates: Coordinates
    data: _T
    width: int
    height: int

    def apply(self, function: PipelineFunction[_T, _U]) -> RenderingPipeline[_U]:
        """
        Apply a pipeline function to the wrapped values.
        """

        return RenderingPipeline(*function(*self), self.width, self.height)

    def __rshift__(self, function: PipelineFunction[_T, _U]) -> RenderingPipeline[_U]:
        return self.apply(function)


@dataclasses.dataclass(slots=True)
class WindowRenderer:
    """
    Engine that renders the Context windows.
    """

    windows: dict[Coordinates, Window] = dataclasses.field(default_factory=dict)

    def render(self, width: int, height: int) -> str:
        """
        Render registered windows into a printable string.
        """

        grid = [[_EMPTY_PIXEL_RENDERING for _ in range(width)] for _ in range(height)]

        for coordinates, window in self.windows.items():
            pipeline = (
                RenderingPipeline(coordinates, list(window.rows()), width, height)
                >> truncate
                >> resize
                >> render
            )

            for y, row in enumerate(pipeline.data):
                for x, pixel in enumerate(row):
                    if pixel != _EMPTY_PIXEL_RENDERING:
                        grid[y][x] = pixel

        return "\x1b[49m\n".join("".join(row) for row in grid)

    def register(self, coordinates: Coordinates, window: Window) -> None:
        """
        Register the `window` at the `coordinates`.
        """

        self.windows[coordinates] = window


def truncate(
    coordinates: Coordinates,
    data: list[list[RGBColor]],
    width: int,
    height: int,
) -> PipelineResult[list[list[RGBColor]]]:
    """
    Truncate the pixels of a window's grid that are outside of the Context
    viewport ; for example, if the window's coordinates are negative, or
    bigger than the Context size.
    """

    new_x = min(width, max(0, coordinates.x))
    new_y = min(height, max(0, coordinates.y))
    new_coordinates = Coordinates(new_x, new_y)

    result: list[list[RGBColor]] = []

    for row in data[abs(min(0, new_y)) : min(height, new_y + len(data))]:
        result.append(row[abs(min(0, new_x)) : new_x + len(row)])

    return new_coordinates, result


def resize(
    coordinates: Coordinates,
    data: list[list[RGBColor]],
    width: int,
    height: int,
) -> PipelineResult[list[list[RGBColor]]]:
    """
    Resize a window's grid to fit the whole Context by adding empty pixels.
    """

    result = [[EMPTY_PIXEL for _ in range(width)] for _ in range(coordinates.y)]

    for row in data:
        right_padding = width - (coordinates.x + len(row))

        padded_row: list[RGBColor] = []

        for _ in range(coordinates.x):
            padded_row.append(EMPTY_PIXEL)

        padded_row.extend(row)

        for _ in range(right_padding):
            padded_row.append(EMPTY_PIXEL)

        result.append(padded_row)

    result.extend(
        [EMPTY_PIXEL for _ in range(width)]
        for _ in range(height - (coordinates.y + len(data)))
    )

    return coordinates, result


def render_pixel(pixel: RGBColor) -> str:
    """
    Render a specific pixel into a background-colored terminal cell.
    """

    return (
        _EMPTY_PIXEL_RENDERING
        if pixel == EMPTY_PIXEL
        else "\x1b[48;2;{};{};{}m ".format(*pixel)
    )


def render(
    coordinates: Coordinates,
    data: list[list[RGBColor]],
    width: int,
    height: int,
) -> PipelineResult[list[list[str]]]:
    """
    Render a window's data into a grid of background-colored termianl cells.
    """

    return coordinates, [[render_pixel(pixel) for pixel in row] for row in data]
