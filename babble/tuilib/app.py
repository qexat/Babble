# pyright: reportMissingTypeStubs = false
import dataclasses
import shutil
import typing

import coquille.sequences
import outspin

from babble.tuilib.context import Context
from babble.tuilib.context import ContextSettingsT
from babble.tuilib.context import ContextSignal
from babble.tuilib.renderer import WindowRenderer
from babble.tuilib.util import keyhints_repr
from babble.tuilib.util import offset_write
from babble.tuilib.window import Coordinates
from babble.tuilib.window import Window


PIXELS_PER_STEP_DEFAULT = 1000

KEYHINTS = keyhints_repr(
    enter="add noise",
    space="random fill",
    s="sort",
    r="randomize",
    e="erase",
    i="switch immersive",
    q="quit",
    **{"shift+f5": "force refresh"},
)
GLOBAL_KEYHINTS = {
    "esc": "quit",
    "shift+f5": "force refresh",
    "i": "switch immersive",
}
FILLING_HINT = (
    "\x1b[35mFilling, please wait...\x1b[39m \x1b[2m(Ctrl+C to interrupt)\x1b[22m"
)

CONTEXT_MARGIN = 5


@dataclasses.dataclass(slots=True)
class App(typing.Generic[ContextSettingsT]):
    """
    TUI-based application.
    """

    name: str
    context_factory: type[Context[ContextSettingsT]]
    renderer: WindowRenderer = dataclasses.field(default_factory=WindowRenderer)

    immersive: bool = dataclasses.field(default=False)

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

    def draw_statusbar(self, context: Context[ContextSettingsT], height: int) -> None:
        """
        Draw the application status bar in the terminal.

        Side-effect: write to stdout.
        """

        message = coquille.sequences.erase_in_line(2)
        message += context.status_message

        if not self.immersive:
            offset_write(message, x=2, y=height - 2)

    def draw(self, context: Context[ContextSettingsT]) -> None:
        """
        Draw the app interface.
        """

        # We refresh the terminal size at every iteration
        width, height = shutil.get_terminal_size()

        # We draw bottom to top, this order is mandatory due to the
        # way it is done (it prints over previous lines)
        self.draw_statusbar(context, height)
        self.draw_windows(width, height)
        self.draw_header()

    def listen_key(self, context: Context[ContextSettingsT]) -> None:
        """
        Listen for a pressed key and act accordingly.
        """

        match outspin.get_key():
            case "esc":
                self.is_requesting_exit = True
                return
            case "shift+f5":
                coquille.apply(coquille.sequences.erase_in_display(2))
                self.draw(context)
                return
            case "i":
                self.immersive = not self.immersive
                coquille.apply(coquille.sequences.erase_in_display(2))
                return
            case key:
                channel = context.receive_key(key)

                # We let the Context run while it is blocking
                while (signal := next(channel)) is ContextSignal.BLOCK:
                    # We still draw in case of updates
                    self.draw(context)

                match signal:
                    case ContextSignal.ABORT:
                        self.is_requesting_exit = True
                    case ContextSignal.LISTEN:
                        return

    def run(self, settings: ContextSettingsT) -> None:
        """
        Run the app.
        """

        width, height = shutil.get_terminal_size()
        window_width = width - CONTEXT_MARGIN
        window_height = height - CONTEXT_MARGIN

        window = Window.empty(window_width, window_height)
        self.renderer.register(Coordinates(0, 0), window)

        context = self.context_factory(window, settings, GLOBAL_KEYHINTS)

        while True:
            self.draw(context)
            self.listen_key(context)

            if self.is_requesting_exit:
                # we don't use `return` because that's basically the same
                # thing in this context, but `break` allows us to add some
                # "at exit" stuff later if needed
                break
