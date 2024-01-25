import abc
import collections.abc
import dataclasses
import enum
import typing

from babble.window import Window

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

    @abc.abstractmethod
    def receive_key(self, key: str) -> collections.abc.Iterator[ContextSignal]:
        """
        Receive the pressed key from the application and act in consequence.
        """
