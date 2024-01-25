import collections.abc
import dataclasses
import random
import typing

import coquille.sequences
from babble.tuilib.context import Context
from babble.tuilib.context import ContextSignal
from babble.tuilib.themes import Theme
from babble.tuilib.util import keyhints_repr
from babble.tuilib.window import Coordinates
from babble.tuilib.window import EMPTY_PIXEL
from babble.tuilib.window import Window


FILLING_HINT = (
    "\x1b[35mFilling, please wait...\x1b[39m \x1b[2m(Ctrl+C to interrupt)\x1b[22m"
)


class BabbleSettings(typing.TypedDict):
    """
    Settings of the Babble context.
    """

    pixels_per_step: int
    theme: Theme


@dataclasses.dataclass(slots=True)
class BabbleContext(Context[BabbleSettings]):
    """
    Core of Babble. That's where all the logics actually happen.
    """

    window: Window
    settings: BabbleSettings
    global_keyhints: dict[str, str]

    def __post_init__(self) -> None:
        self.status_message = keyhints_repr(
            enter="add noise",
            space="random fill",
            s="sort",
            r="shuffle",
            e="erase",
            q="quit",
            **self.global_keyhints,
        )
        self.default_status_message = self.status_message

    def receive_key(self, key: str) -> collections.abc.Iterator[ContextSignal]:
        match key:
            case "space":
                if not self.is_fully_filled():
                    self.status_message = FILLING_HINT
                    yield ContextSignal.BLOCK

                    try:
                        yield from self.fill_random()
                    finally:
                        self.restore_status_message()
            case "enter":
                self.add_random_noise()
            case "e":
                self.window.reset()
            case "r":
                random.shuffle(self.window.pixels)
            case "s":
                self.window.pixels.sort()
            case "q":
                yield ContextSignal.ABORT
            case _:
                pass

        yield ContextSignal.LISTEN

    def is_fully_filled(self) -> bool:
        """
        Return `True` if the window has no empty pixel else `False`.
        """

        return EMPTY_PIXEL not in self.window.pixels

    def add_random_noise(self) -> None:
        """
        Add random pixels to the `window`.
        """

        nb_pixels = self.settings["pixels_per_step"]

        if nb_pixels < 0:
            raise ValueError("the number of pixels must be non-negative")

        i = 0

        while i < nb_pixels:
            coordinates = Coordinates.random(self.window.width, self.window.height)
            color = self.settings["theme"].get(
                coordinates,
                self.window.width,
                self.window.height,
            )

            if self.window.set_pixel(coordinates, color):
                i += 1

    def fill_random(self) -> collections.abc.Iterator[ContextSignal]:
        """
        Fill randomly the window until it is fully crowded.
        """

        try:
            while not self.is_fully_filled():
                self.add_random_noise()
                yield ContextSignal.BLOCK
        except KeyboardInterrupt:
            # Interrupting might not reset the background color
            coquille.apply(coquille.sequences.default_background_color)
