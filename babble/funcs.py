from babble.window import Coordinates
from babble.window import RGBColor
from babble.window import Window


def add_random_noise(window: Window, nb_pixels: int) -> None:
    """
    Add `nb_pixels` random pixels to the `window`.
    """

    if nb_pixels < 0:
        raise ValueError("the number of pixels must be non-negative")

    i = 0

    while i < 100:
        coordinates = Coordinates.random(window.width, window.height)
        color = RGBColor(
            int(coordinates.x / window.width * 255),
            0,
            255 - int(coordinates.y / window.height * 255),
        )

        if window.set_pixel(coordinates, color):
            i += 1
