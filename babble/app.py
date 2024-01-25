# pyright: reportMissingTypeStubs = false
import dataclasses
import random
import shutil
import typing

import coquille.sequences
import outspin

from babble.builtins import themes
from babble.funcs import add_random_noise
from babble.renderer import WindowRenderer
from babble.themes import Theme
from babble.util import is_fully_filled
from babble.util import make_keys_hint
from babble.util import offset_write
from babble.window import Coordinates
from babble.window import Window


PIXELS_PER_STEP_DEFAULT = 1000

KEYS_HINT = make_keys_hint(
    enter="add noise",
    space="random fill",
    s="sort",
    r="randomize",
    e="erase",
    f="force refresh",
    i="switch immersive",
    q="quit",
)
FILLING_HINT = (
    "\x1b[35mFilling, please wait...\x1b[39m \x1b[2m(Ctrl+C to interrupt)\x1b[22m"
)

CONTEXT_MARGIN = 5


@dataclasses.dataclass(slots=True)
class App:
    """
    TUI-based application.
    """

    name: str
    renderer: WindowRenderer = dataclasses.field(default_factory=WindowRenderer)

    is_randomizing: bool = dataclasses.field(default=False)
    immersive: bool = dataclasses.field(default=False)
    pixels_per_step: int = dataclasses.field(default=PIXELS_PER_STEP_DEFAULT)
    theme: Theme = dataclasses.field(default=themes.BABBLE)

    is_requesting_exit: bool = dataclasses.field(init=False, default=False)

    def __enter__(self) -> typing.Self:
        coquille.apply(coquille.sequences.enable_alternative_screen_buffer)
        coquille.apply(coquille.sequences.erase_in_display(2))
        coquille.apply(coquille.sequences.hide_cursor)
        coquille.apply(coquille.sequences.cursor_position(1, 1))

        return self

    def __exit__(self, *_) -> None:
        coquille.apply(coquille.sequences.disable_alternative_screen_buffer)
        coquille.apply(coquille.sequences.show_cursor)

    @property
    def header(self) -> str:
        """
        The header of the application shows its title.
        """

        return f"\x1b[1;45m {self.name} \x1b[22;49m"

    def draw_header(self) -> None:
        """
        Draw the application header in the terminal.

        Side-effect: write to stdout.
        """

        if not self.immersive:
            offset_write(self.header, x=2, y=0)

    def draw_windows(self, width: int, height: int) -> None:
        """
        Draw the application window in the terminal.

        The renderer technically allows for multiple windows -- this never
        happens in practice. But, this is why a `Context` is mentioned: it
        refers to the frame containing every window.

        Side-effect: write to stdout.
        """

        context_width = width - CONTEXT_MARGIN
        context_height = height - CONTEXT_MARGIN
        rendering = self.renderer.render(context_width, context_height)

        offset_write(rendering, x=2, y=2)
        coquille.apply(coquille.sequences.default_background_color)

    def draw_statusbar(self, height: int) -> None:
        """
        Draw the application status bar in the terminal.

        Side-effect: write to stdout.
        """

        message = coquille.sequences.erase_in_line(2)
        message += FILLING_HINT if self.is_randomizing else KEYS_HINT

        if not self.immersive:
            offset_write(message, x=2, y=height - 2)

    def draw(self) -> None:
        """
        Draw the app interface.
        """

        # We refresh the terminal size at every iteration
        width, height = shutil.get_terminal_size()

        # We draw bottom to top, this order is mandatory due to the
        # way it is done (it prints over previous lines)
        self.draw_statusbar(height)
        self.draw_windows(width, height)
        self.draw_header()

    def listen_user(self, window: Window) -> None:
        """
        Listen for a pressed key and act accordingly.
        """

        match outspin.get_key():
            case "space":
                if not is_fully_filled(window):
                    self.is_randomizing = True
            case "enter":
                add_random_noise(window, self.pixels_per_step, self.theme)
            case "e":
                window.reset()
            case "r":
                random.shuffle(window.pixels)
            case "s":
                window.pixels.sort()
            case "i":
                self.immersive = not self.immersive
                coquille.apply(coquille.sequences.erase_in_display(2))
            case "f":
                coquille.apply(coquille.sequences.erase_in_display(2))
                self.draw()
            case "q" | "esc":
                self.is_requesting_exit = True
            case _:
                # If the key pressed is not recognized, we simply ignore it.
                pass

    def run(self) -> None:
        """
        Run the app.
        """

        width, height = shutil.get_terminal_size()
        window_width = width - CONTEXT_MARGIN
        window_height = height - CONTEXT_MARGIN

        window = Window.empty(window_width, window_height)
        self.renderer.register(Coordinates(0, 0), window)

        while True:
            try:
                self.draw()

                if self.is_randomizing:  # i.e. we pressed space earlier
                    add_random_noise(window, self.pixels_per_step, self.theme)

                    if is_fully_filled(window):
                        self.is_randomizing = False
                else:
                    self.listen_user(window)
            except KeyboardInterrupt:
                # Interrupting might not reset the background color
                coquille.apply(coquille.sequences.default_background_color)

                self.is_randomizing = False

            if self.is_requesting_exit:
                # we don't use `return` because that's basically the same
                # thing in this context, but `break` allows us to add some
                # "at exit" stuff later if needed
                break


class AppParams(typing.TypedDict):
    is_randomizing: bool
    immersive: bool
    pixels_per_step: int
    theme: Theme
