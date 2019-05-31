"""
    PyFSM

    Transitions module tests

"""

import unittest2 as unittest
import mock
from pyfsm import (
    GuardManager,
    GuardInterface,
    ListenerManager,
    ListenerInterface,
    State,
    InvalidTransitionConfig
)
from pyfsm.guard import NullGuard, ReverseGuard
from pyfsm.state import StateManager
from pyfsm.transition import TransitionFactory, Transition, TransitionTable
from tests import TestContext


class TestTransitionFactory(unittest.TestCase):
    """ Transition factory tests """

    def setUp(self):
        """ Sets up tests environment """
        self.__states = {
            'from': State('from'),
            'to': State('to')
        }
        self.__guard = mock.Mock(GuardInterface)
        self.__listeners = {
            'before': mock.Mock(ListenerInterface),
            'after': mock.Mock(ListenerInterface)
        }

        self.__state_manager = StateManager()
        self.__state_manager.get_state = mock.Mock(
            side_effect=self.__states.values()
        )

        self.__guard_manager = GuardManager()
        self.__guard_manager.get_guard = mock.Mock(return_value=self.__guard)

        self.__listener_manager = ListenerManager()
        self.__listener_manager.get_listener = mock.Mock(
            side_effect=self.__listeners.values()
        )

        self.__factory = TransitionFactory(
            self.__state_manager,
            self.__guard_manager,
            self.__listener_manager
        )

    def tearDown(self):
        """ Unsets tests environment """
        del self.__factory
        del self.__listener_manager
        del self.__guard_manager
        del self.__state_manager
        del self.__listeners
        del self.__guard
        del self.__states

    def test_get_transition(self):
        """ Tests transition getting """

        config = {
            'from': 'from',
            'to': 'to',
            'signal': 'signal',
            'guards': (self.__guard,),
            'before': (self.__listeners['before'],),
            'after': (self.__listeners['after'],)
        }
        transition = self.__factory.get_transition(config)

        self.assertIsInstance(transition, Transition)
        self.assertIs(transition.state_from, self.__states['from'])
        self.assertIs(transition.state_to, self.__states['to'])
        self.assertEqual(len(transition.guards), 1)
        self.assertEqual(transition.guards[0], self.__guard)
        self.assertEqual(len(transition.before), 1)
        self.assertEqual(transition.before[0], self.__listeners['before'])
        self.assertEqual(len(transition.after), 1)
        self.assertEqual(transition.after[0], self.__listeners['after'])

    def test_get_transition_without_from_state(self):
        """ Tests transition with absent initial state creation"""
        with self.assertRaisesRegex(
                InvalidTransitionConfig,
                "Initial state not found in config {}"
        ):
            self.__factory.get_transition({})

    def test_get_transition_without_to_state(self):
        """ Tests transition with absent final state creation"""
        with self.assertRaisesRegex(
                InvalidTransitionConfig,
                "Final state not found in config {'from': 'from'}"
        ):
            self.__factory.get_transition({'from': 'from'})


class TestTransitionTable(unittest.TestCase):
    """ Transitions table tests """

    def setUp(self):
        """ Sets up tests environment """
        self.__context = TestContext()

        factory = mock.Mock(TransitionFactory)
        self.__table = TransitionTable(factory, [])

    def tearDown(self):
        """ Unsets tests environment """
        del self.__table
        del self.__context

    def test_add_transition_without_signal(self):
        """ Tests without signal """
        with self.assertRaises(StopIteration):
            next(self.__table.find_transitions(self.__context))

        transition = Transition(State('from'), State('to'))
        self.__table.add_transition(transition)

        found = self.__table.find_transitions(self.__context)

        self.assertIs(transition, next(found))
        with self.assertRaises(StopIteration):
            next(found)

    def test_add_transition_with_signal(self):
        """ Tests with signal """
        with self.assertRaises(StopIteration):
            next(self.__table.find_transitions(self.__context))

        transition = Transition(State('from'), State('to'), 'signal')
        self.__table.add_transition(transition)

        with self.assertRaises(StopIteration):
            next(self.__table.find_transitions(self.__context))

        found = self.__table.find_transitions(self.__context, 'signal')

        self.assertIs(transition, next(found))
        with self.assertRaises(StopIteration):
            next(found)

    def test_find_transitions_with_true_guard(self):
        """ Tests with guard """
        with self.assertRaises(StopIteration):
            next(self.__table.find_transitions(self.__context))

        transition = Transition(
            State('from'),
            State('to'),
            'signal',
            [NullGuard()]
        )
        self.__table.add_transition(transition)

        with self.assertRaises(StopIteration):
            next(self.__table.find_transitions(self.__context))

        found = self.__table.find_transitions(self.__context, 'signal')

        self.assertIs(transition, next(found))
        with self.assertRaises(StopIteration):
            next(found)

    def test_find_transitions_with_false_guard(self):
        """ Tests with guard """
        with self.assertRaises(StopIteration):
            next(self.__table.find_transitions(self.__context))

        transition = Transition(
            State('from'),
            State('to'),
            'signal',
            [ReverseGuard(NullGuard())]
        )
        self.__table.add_transition(transition)

        with self.assertRaises(StopIteration):
            next(self.__table.find_transitions(self.__context))

        found = self.__table.find_transitions(self.__context, 'signal')

        with self.assertRaises(StopIteration):
            next(found)


if __name__ == '__main__':
    unittest.main()
