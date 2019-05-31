"""
    PyFSM.guard

    Guards module
"""

from abc import abstractmethod, ABCMeta
from .entity import StatefulInterface


class GuardInterface(metaclass=ABCMeta):
    """ Guard interface """

    @abstractmethod
    def is_satisfied(self, target: StatefulInterface) -> bool:
        """ Checks guard condition """


class NullGuard(GuardInterface):
    """ True condition guard """

    def is_satisfied(self, target: StatefulInterface) -> bool:
        """ Checks guard condition """
        return True


class ReverseGuard(GuardInterface):
    """ Revers condition guard """

    def __init__(self, guard: GuardInterface):
        self.__guard = guard

    def is_satisfied(self, target: StatefulInterface) -> bool:
        """ Checks guard condition """
        return not self.__guard.is_satisfied(target)


class GuardManager:
    """ Guard manager """

    def __init__(self):
        self.__guards = {}

    def get_guard(self, name: str) -> GuardInterface:
        """ Gets guard by name """
        return self.__guards[name] if name in self.__guards else NullGuard

    def add_guard(self, guard: GuardInterface):
        """ Adds guard """
        name = type(guard).__name__

        self.__guards[name] = guard
        self.__guards['!' + name] = ReverseGuard(guard)
