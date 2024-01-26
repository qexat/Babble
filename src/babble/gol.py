import collections.abc
import dataclasses
import typing

import coquille.sequences

from babble.tuilib.context import Context
from babble.tuilib.context import ContextSignal
from babble.tuilib.util import keyhints_repr
from babble.tuilib.window import Coordinates
from babble.tuilib.window import EMPTY_PIXEL
from babble.tuilib.window import RGBColor
from babble.tuilib.window import Window


class GoLSettings(typing.TypedDict):
    """
    Settings for the Game of Life context.
    """

    birth_rule: set[int]
    survive_rule: set[int]
    death_rule: set[int]


DEFAULT_SETTINGS: GoLSettings = {
    "birth_rule": {3},
    "survive_rule": {2, 3},
    "death_rule": {0, 1, *range(4, 9)},
}

LIVING_CELL = RGBColor(255, 255, 255)
DEAD_CELL = EMPTY_PIXEL

RUNNING_HINT = (
    "\x1b[35mSimulating, please wait...\x1b[39m \x1b[2m(Ctrl+C to interrupt)\x1b[22m"
)

_GLIDER_COORDINATES = [
    Coordinates(2, 1),
    Coordinates(0, 2),
    Coordinates(2, 2),
    Coordinates(1, 3),
    Coordinates(2, 3),
]


@dataclasses.dataclass(slots=True)
class GoLContext(Context[GoLSettings]):
    """
    Core of the Game of Life. That's where all the logics actually happen.
    """

    window: Window
    settings: GoLSettings
    global_keyhints: dict[str, str]

    def __post_init__(self) -> None:
        self.status_message = keyhints_repr(
            enter="new generation",
            space="run until no cell",
            g="add glider",
            r="randomize",
            e="erase",
            q="quit",
            **self.global_keyhints,
        )
        self.default_status_message = self.status_message

    def receive_key(self, key: str) -> collections.abc.Iterator[ContextSignal]:
        match key:
            case "space":
                if self.has_living_cells():
                    self.status_message = RUNNING_HINT
                    yield ContextSignal.BLOCK

                    try:
                        yield from self.run()
                    finally:
                        self.restore_status_message()
            case "enter":
                self.next_generation()
            case "g":
                self.add_glider()
            case "e":
                self.window.reset()
            case "r":
                self.randomize()
            case "q":
                yield ContextSignal.ABORT
            case _:
                pass

        yield ContextSignal.LISTEN

    def randomize(self) -> None:
        i = 0

        while i < 100:
            coordinates = Coordinates.random(self.window.width, self.window.height)

            if self.window.set_pixel(coordinates, LIVING_CELL):
                i += 1

    def has_living_cells(self) -> bool:
        return LIVING_CELL in self.window.pixels

    def get_living_neighbors(self, coordinates: Coordinates) -> list[RGBColor]:
        vertical_slice = slice(
            max(0, coordinates.y - 1), min(self.window.height, coordinates.y + 2),
        )
        horizontal_slice = slice(
            max(0, coordinates.x - 1), min(self.window.width, coordinates.x + 2),
        )

        return [
            cell
            for y, row in enumerate(
                list(self.window.rows())[vertical_slice], start=vertical_slice.start,
            )
            for x, cell in enumerate(
                row[horizontal_slice], start=horizontal_slice.start,
            )
            if cell == LIVING_CELL and coordinates != (x, y)
        ]

    def get_living_neighbors_count(self, coordinates: Coordinates) -> int:
        return len(self.get_living_neighbors(coordinates))

    def should_die(self, coordinates: Coordinates, cell: RGBColor) -> bool:
        return (
            cell == LIVING_CELL
            and self.get_living_neighbors_count(coordinates)
            not in self.settings["survive_rule"]
        )

    def should_birth(self, coordinates: Coordinates, cell: RGBColor) -> bool:
        return (
            cell == DEAD_CELL
            and self.get_living_neighbors_count(coordinates)
            in self.settings["birth_rule"]
        )

    def next_generation(self) -> None:
        window_copy = self.window.copy()

        for coordinates, cell in self.window:
            if self.should_die(coordinates, cell):
                window_copy.set_pixel_unchecked(coordinates, DEAD_CELL)

        for coordinates, cell in self.window:
            if self.should_birth(coordinates, cell):
                window_copy.set_pixel_unchecked(coordinates, LIVING_CELL)

        self.window.pixels = window_copy.pixels

    def run(self) -> collections.abc.Iterator[ContextSignal]:
        try:
            while self.has_living_cells():
                self.next_generation()
                yield ContextSignal.BLOCK
        except KeyboardInterrupt:
            pass
        finally:
            # Interrupting might not reset the background color
            coquille.apply(coquille.sequences.default_background_color)

    def add_glider(self) -> None:
        for coordinate in _GLIDER_COORDINATES:
            self.window.set_pixel_unchecked(coordinate, LIVING_CELL)
