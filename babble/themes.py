import collections.abc
import dataclasses
import typing

from babble.window import Coordinates
from babble.window import RGBColor


ChannelFunction: typing.TypeAlias = collections.abc.Callable[
    [Coordinates, int, int], int,
]


@dataclasses.dataclass(slots=True, frozen=True)
class Theme:
    red: ChannelFunction
    green: ChannelFunction
    blue: ChannelFunction

    @classmethod
    def new_uniform(cls, function: ChannelFunction) -> typing.Self:
        """
        Return a theme for which the red, green and blue channel functions are
        identical.
        """

        return cls(function, function, function)

    def get(self, coordinates: Coordinates, width: int, height: int) -> RGBColor:
        """
        Get the color of the pixel at the provided `coordinates`.
        """

        return RGBColor(
            self.red(coordinates, width, height),
            self.green(coordinates, width, height),
            self.blue(coordinates, width, height),
        )
