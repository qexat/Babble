from babble.themes import Theme
from babble.window import Coordinates
from babble.window import Window


def add_random_noise(window: Window, nb_pixels: int, theme: Theme) -> None:
    """
    Add `nb_pixels` random pixels to the `window`.
    """

    if nb_pixels < 0:
        raise ValueError("the number of pixels must be non-negative")

    i = 0

    while i < nb_pixels:
        coordinates = Coordinates.random(window.width, window.height)
        color = theme.get(coordinates, window.width, window.height)

        if window.set_pixel(coordinates, color):
            i += 1
