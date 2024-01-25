import abc
import collections.abc
import dataclasses
import enum
import typing

from babble.tuilib.window import Window

ContextSettingsT = typing.TypeVar("ContextSettingsT", bound=typing.TypedDict)


class ContextSignal(enum.Enum):
    """
    Signals sent by a context to the application.
    """

    LISTEN = enum.auto()
    """The context listens to the input (e.g. key pressed by user)"""

    BLOCK = enum.auto()
    """The context is executing something, blocking external queries"""

    ABORT = enum.auto()
    """The context requests the application to close"""


@dataclasses.dataclass(slots=True)
class Context(typing.Generic[ContextSettingsT], abc.ABC):
    """
    Base class used to define a context that can be run inside an application.
    """

    window: Window
    settings: ContextSettingsT
    global_keyhints: dict[str, str]

    status_message: str = dataclasses.field(init=False)
    default_status_message: str = dataclasses.field(init=False)

    def restore_status_message(self) -> None:
        self.status_message = self.default_status_message

    @abc.abstractmethod
    def receive_key(self, key: str) -> collections.abc.Iterator[ContextSignal]:
        """
        Receive the pressed key from the application and act in consequence.
        """
