import collections.abc
import dataclasses
import random
import typing


class Coordinates(typing.NamedTuple):
    x: int
    y: int

    @classmethod
    def random(cls, x_max: int, y_max: int) -> typing.Self:
        """
        Constructor for random coordinates.

        The resulting `x` will be between 0 and `x_max`.
        The resulting `y` will be between 0 and `y_max`.
        """

        return cls(random.randint(0, x_max), random.randint(0, y_max))


class RGBColor(typing.NamedTuple):
    red: int
    green: int
    blue: int

    @classmethod
    def random(cls) -> typing.Self:
        """
        Constructor for a random color.
        """

        return cls(*(random.randint(0, 255) for _ in range(3)))


EMPTY_PIXEL = RGBColor(256, 256, 256)


@dataclasses.dataclass(slots=True)
class Window:
    """
    Window inside a Context where the pixels are shown.
    """

    width: int
    height: int
    pixels: list[RGBColor] = dataclasses.field(default_factory=list)

    def __iter__(self) -> collections.abc.Iterator[tuple[Coordinates, RGBColor]]:
        for i, pixel in enumerate(self.pixels):
            y, x = divmod(i, self.width)

            yield Coordinates(x, y), pixel

    @classmethod
    def empty(cls, width: int, height: int) -> typing.Self:
        """
        Constructor for an empty window of size `width` × `height`.
        """

        return cls(width, height, [EMPTY_PIXEL for _ in range(width * height)])

    def is_inbounds(self, coordinates: Coordinates) -> bool:
        """
        Return True if `coordinates` are inside the window, else False.
        """

        return (0 <= coordinates.x < self.width) and (0 <= coordinates.y < self.height)

    def get_pixel(self, coordinates: Coordinates) -> RGBColor | None:
        """
        Return the pixel at the provided `coordinates` if they are inbounds, else None.
        """

        if not self.is_inbounds(coordinates):
            return None

        return self.get_pixel_unchecked(coordinates)

    def get_pixel_unchecked(self, coordinates: Coordinates) -> RGBColor:
        """
        Unchecked version of `get_pixel()`. Instead of returning `None`, raises an `IndexError`.
        """

        return self.pixels[self.width * coordinates.y + coordinates.x]

    def set_pixel(self, coordinates: Coordinates, value: RGBColor) -> RGBColor | None:
        """
        Set the pixel at the `coordinates` with the color `value` and return the previous
        value of that pixel. If the coordinates are out of bounds, return None.
        """

        if not self.is_inbounds(coordinates):
            return None

        return self.set_pixel_unchecked(coordinates, value)

    def set_pixel_unchecked(
        self,
        coordinates: Coordinates,
        value: RGBColor,
    ) -> RGBColor:
        """
        Unchecked version of `set_pixel`. Instead of returning `None`, raises an `IndexError`.
        """

        previous = self.get_pixel_unchecked(coordinates)
        self.pixels[self.width * coordinates.y + coordinates.x] = value

        return previous

    def reset(self) -> None:
        """
        Clean the window to emptiness.
        """

        self.pixels = [EMPTY_PIXEL for _ in range(self.width * self.height)]

    def rows(self) -> collections.abc.Iterator[list[RGBColor]]:
        """
        Get a list of the window rows.
        """

        for i in range(self.height):
            yield self.pixels[i * self.width : (i + 1) * self.width]

    def copy(self) -> typing.Self:
        return self.__class__(self.width, self.height, self.pixels.copy())
