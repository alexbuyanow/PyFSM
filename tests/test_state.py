"""
    PyFSM

    States module tests

"""

import unittest2 as unittest
from pyfsm import (
    State,
    StateInterface,
    IncorrectStateTypeException,
    IncorrectStateConfigException,
    StateNotFoundException
)
from pyfsm.state import StateFactory, StateManager


class TestStateFactory(unittest.TestCase):
    """ State factory tests """

    def setUp(self):
        """ Sets up tests environment """
        config = {
            'correct': {StateFactory.KEY_TYPE: StateInterface.TYPE_REGULAR},
            'incorrect': {StateFactory.KEY_TYPE: 'tests'},
            'absent': {}
        }
        self.__factory = StateFactory(config)

    def tearDown(self):
        """ Unsets tests environment """
        del self.__factory

    def test_get_state(self):
        """ Tests state getting """
        state_name = 'correct'
        state = self.__factory.get_state(state_name)

        self.assertIsInstance(state, StateInterface)
        self.assertEqual(state_name, state.name)
        self.assertEqual(StateInterface.TYPE_REGULAR, state.type)
        self.assertEqual(state_name, str(state))

    def test_get_state_with_absent_type(self):
        """ Tests state with absent type getting """
        state_name = 'absent'
        state = self.__factory.get_state(state_name)

        self.assertIsInstance(state, StateInterface)
        self.assertEqual(state_name, state.name)
        self.assertEqual(StateInterface.TYPE_REGULAR, state.type)
        self.assertEqual(state_name, str(state))

    def test_get_state_with_incorrect_type(self):
        """ Tests state with incorrect type getting """
        with self.assertRaisesRegex(
                IncorrectStateTypeException,
                "Incorrect type 'tests' for state 'incorrect'"
        ):
            self.__factory.get_state('incorrect')

    def test_get_state_absent(self):
        """ Tests absent state getting """
        with self.assertRaisesRegex(
                IncorrectStateConfigException,
                "State 'none' is not found in config"
        ):
            self.__factory.get_state('none')


class TestStateManager(unittest.TestCase):
    """ States manager tests"""

    def setUp(self):
        """ Sets up tests environment """
        self.__manager = StateManager()

    def tearDown(self):
        """ Unsets tests environment """
        del self.__manager

    def test_add_state(self):
        """ Tests state adding """
        state_name = 'state'
        state = State(state_name)

        self.__manager.add_state(state_name, state)
        self.assertEqual(self.__manager.get_state(state_name), state)

    def test_get_state_not_found_exception(self):
        """ Tests error on absent state getting """
        with self.assertRaisesRegex(
                StateNotFoundException,
                "State 'tests' is not found"
        ):
            self.__manager.get_state('tests')


if __name__ == '__main__':
    unittest.main()
