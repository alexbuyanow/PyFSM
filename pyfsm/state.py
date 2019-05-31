"""
    PyFSM.state

    State module

"""

from abc import abstractmethod, ABCMeta
from dataclasses import dataclass
from typing import Tuple, Dict


class StateInterface(metaclass=ABCMeta):
    """ State interface """

    TYPE_REGULAR: str = 'regular'

    @abstractmethod
    def name(self) -> str:
        """ Gets state ID """

    @abstractmethod
    def type(self) -> str:
        """ Gets state type """

    @abstractmethod
    def __str__(self) -> str:
        """ Converts state to string """


@dataclass
class State(StateInterface):
    """ State """

    __name: str
    __type: str = StateInterface.TYPE_REGULAR

    def __eq__(self, other: StateInterface) -> bool:
        return self.__name == other.name

    def __ne__(self, other: StateInterface) -> bool:
        return self.__name != other.name

    def __hash__(self):
        return self.name

    def __str__(self) -> str:
        """ Converts state to string """
        return self.name

    @property
    def name(self) -> str:
        """ Gets state ID """
        return self.__name

    @property
    def type(self) -> str:
        """ Gets state type """
        return self.__type


class StateFactory:
    """ States factory """

    KEY_TYPE: str = 'type'

    __available_types: Tuple = (
        State.TYPE_REGULAR
    )

    def __init__(self, config: Dict[str, Dict[str, str]]):
        self.__config = config

    def get_state(self, name: str) -> State:
        """ Gets state """
        if name not in self.__config:
            message = "State '{0}' is not found in config".format(name)
            raise IncorrectStateConfigException(message)

        state_config = self.__config[name]
        state_type = state_config[self.KEY_TYPE] \
            if self.KEY_TYPE in state_config \
            else State.TYPE_REGULAR

        if state_type not in self.__available_types:
            message = "Incorrect type '{0}' for state '{1}'".format(
                state_type,
                name
            )
            raise IncorrectStateTypeException(message)

        return State(name, state_type)


class StateManager:
    """ States manager """

    def __init__(self):
        self.__states = {}

    def get_state(self, name: str) -> StateInterface:
        """ Gets state by name """
        if name not in self.__states:
            message = "State '{0}' is not found".format(name)
            raise StateNotFoundException(message)

        return self.__states[name]

    def add_state(self, name: str, state: StateInterface):
        """ Adds state """
        self.__states[name] = state


class StateNotFoundException(Exception):
    """ Error if state is not found """


class IncorrectStateConfigException(Exception):
    """ Incorrect state config error """


class IncorrectStateTypeException(Exception):
    """ Incorrect state type error """
