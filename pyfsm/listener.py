"""
    PyFSM.listener

    Listeners module
"""

from abc import abstractmethod, ABCMeta
from dataclasses import dataclass
from typing import Any, Dict, Optional
from .entity import StatefulInterface
from .state import StateInterface


@dataclass()
class Event:
    """ Transition event """

    __context: StatefulInterface
    __state_from: StateInterface
    __state_to: StateInterface
    __signal: str
    __params: Dict[str, Any]

    @property
    def context(self) -> StatefulInterface:
        """ Gets target context """
        return self.__context

    @property
    def state_to(self) -> StateInterface:
        """ Gets final state """
        return self.__state_to

    @property
    def state_from(self) -> StateInterface:
        """ Gets initial state """
        return self.__state_from

    @property
    def signal(self) -> Optional[str]:
        """ Gets transition signal """
        return self.__signal

    @property
    def params(self) -> Dict[str, Any]:
        """ Gets extra parameters """
        return self.__params


class ListenerInterface(metaclass=ABCMeta):
    """ Listener interface """

    @abstractmethod
    def listen(self, event: Event):
        """ Processes transition event """


class ListenerManager:
    """ Listener manager """

    def __init__(self):
        self.__listeners = {}

    def get_listener(self, name: str) -> ListenerInterface:
        """ Gets listener by name """
        if name not in self.__listeners:
            message = "Listener '{0}' is not found".format(name)
            raise ListenerNotFoundException(message)

        return self.__listeners[name]

    def add_listener(self, listener: ListenerInterface):
        """ Adds listener """
        self.__listeners[type(listener).__name__] = listener


class ListenerNotFoundException(Exception):
    """ Error if listener is not found """
