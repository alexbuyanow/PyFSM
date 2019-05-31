"""
    PyFSM

    Tests
"""

from pyfsm import StatefulInterface, StateInterface, State


class TestContext(StatefulInterface):
    """ Test context """

    def __init__(self):
        self.__state = State('from')

    @property
    def state(self) -> StateInterface:
        """ Gets state """
        return self.__state

    @state.setter
    def state(self, state: StateInterface):
        """ Sets state """
        self.__state = state
