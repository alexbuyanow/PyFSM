"""
    PyFSM

    State machine module tests

"""

from typing import Any, List
import unittest
import mock
from pyfsm import (
    GuardManager,
    ListenerManager,
    FSMFactory,
    FSMInterface,
    FSMNotFoundException,
    State
)
from pyfsm.fsm import FSM
from pyfsm.transition import Transition, TransitionTable
from tests import TestContext


class TestFSM(unittest.TestCase):
    """ State machine tests """

    __TEST_SIGNAL = 'go'
    __TEST_FROM = 'from'
    __TEST_TO = 'from'

    def setUp(self):
        self.__transition_table = mock.Mock(TransitionTable)
        self.__context = TestContext()
        self.__transition = Transition(
            State(self.__TEST_FROM),
            State(self.__TEST_TO)
        )

    def tearDown(self):
        del self.__transition
        del self.__context
        del self.__transition_table

    def test_refresh(self):
        """ Tests direct transition on refresh """
        self.__transition_table.find_transitions.side_effect = (
            iter([self.__transition]),
            iter([])
        )

        self.__assert_state(self.__TEST_FROM)

        fsm = FSM(type(self.__context).__name__, self.__transition_table)
        fsm.refresh(self.__context)

        self.__assert_state(self.__TEST_TO)
        self.__assert_find_transition_calling(
            [mock.call(self.__context, None)] * 2,
        )

    def test_refresh_no(self):
        """ Tests fails direct transition on refresh """
        self.__transition_table.find_transitions.return_value = iter([])

        self.__assert_state(self.__TEST_FROM)

        fsm = FSM(type(self.__context).__name__, self.__transition_table)
        fsm.refresh(self.__context)

        self.__assert_state(self.__TEST_FROM)
        self.__assert_find_transition_calling(
            [mock.call(self.__context, None)],
        )

    def test_signal(self):
        """ Tests signal transition """
        self.__transition_table.find_transitions.side_effect = (
            iter([]),
            iter([self.__transition]),
            iter([])
        )

        self.__assert_state(self.__TEST_FROM)

        fsm = FSM(type(self.__context).__name__, self.__transition_table)
        fsm.signal(self.__context, self.__TEST_SIGNAL)

        self.__assert_state(self.__TEST_TO)
        self.__assert_find_transition_calling(
            [
                mock.call(self.__context, None),
                mock.call(self.__context, self.__TEST_SIGNAL),
                mock.call(self.__context, None)
            ],
        )

    def test_signal_no(self):
        """ Tests fails signal transition """
        self.__transition_table.find_transitions.side_effect = (
            iter([]),
            iter([])
        )

        self.__assert_state(self.__TEST_FROM)

        fsm = FSM(type(self.__context).__name__, self.__transition_table)
        fsm.signal(self.__context, self.__TEST_SIGNAL)

        self.__assert_state(self.__TEST_FROM)
        self.__assert_find_transition_calling(
            [
                mock.call(self.__context, None),
                mock.call(self.__context, self.__TEST_SIGNAL),
            ],
        )

    def test_is_signal(self):
        """ Tests is signal transition possible """
        self.__transition_table.find_transitions.side_effect = (
            iter([]),
            iter([self.__transition])
        )

        self.__assert_state(self.__TEST_FROM)

        fsm = FSM(type(self.__context).__name__, self.__transition_table)

        self.assertTrue(fsm.is_signal(self.__context, self.__TEST_SIGNAL))
        self.__assert_find_transition_calling(
            [
                mock.call(self.__context, None),
                mock.call(self.__context, self.__TEST_SIGNAL)
            ],
        )

    def test_is_signal_no(self):
        """ Tests is signal transition impossible """
        self.__transition_table.find_transitions.side_effect = (
            iter([]),
            iter([])
        )

        self.__assert_state(self.__TEST_FROM)

        fsm = FSM(type(self.__context).__name__, self.__transition_table)

        self.assertFalse(fsm.is_signal(self.__context, self.__TEST_SIGNAL))
        self.__assert_find_transition_calling(
            [
                mock.call(self.__context, None),
                mock.call(self.__context, self.__TEST_SIGNAL)
            ],
        )

    def __assert_state(self, state: str):
        """ Checks state assertion """
        self.assertEqual(state, self.__context.state.name)

    def __assert_find_transition_calling(self, calls: List[Any]):
        """ Checks 'find_transition' calls """
        self.__transition_table.find_transitions.assert_has_calls(calls)
        self.assertEqual(
            len(calls),
            self.__transition_table.find_transitions.call_count
        )


class TestFSMFactory(unittest.TestCase):
    """ State machine factory tests"""

    def setUp(self):
        """ Sets up test environment """
        self.__context = TestContext()
        self.__guard_manager = mock.Mock(GuardManager)
        self.__listener_manager = mock.Mock(ListenerManager)

    def tearDown(self):
        """ Unsets test environment """
        del self.__guard_manager
        del self.__listener_manager
        del self.__context

    def test_get_fsm(self):
        """ Tests state machine creating """
        config = {
            'TestContext': {
                'states': {
                    'from': {},
                    'to': {}
                },
                'transitions': [
                    {
                        'from': 'from',
                        'to': 'to'
                    }
                ]
            }
        }

        factory = FSMFactory(
            config,
            self.__guard_manager,
            self.__listener_manager
        )
        fsm = factory.get_fsm(self.__context)

        self.assertIsInstance(fsm, FSMInterface)

    def test_get_fsm_not_found(self):
        """ Tests getting of absent state machine """
        factory = FSMFactory({}, self.__guard_manager, self.__listener_manager)

        with self.assertRaisesRegex(
                FSMNotFoundException,
                "FSM with name 'TestContext' is not found in config"
        ):
            factory.get_fsm(self.__context)


if __name__ == '__main__':
    unittest.main()
