"""
    PyFSM.entity

    Entities module

"""

from abc import abstractmethod, ABCMeta
from .state import StateInterface


class StatefulInterface(metaclass=ABCMeta):
    """ State aware interface """

    @property
    @abstractmethod
    def state(self) -> StateInterface:
        """ Gets state """

    @state.setter
    @abstractmethod
    def state(self, state: StateInterface):
        """ Sets state """
