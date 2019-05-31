"""
    PyFSM

    Guards module tests

"""

import unittest2 as unittest
from parameterized import parameterized
import mock
from pyfsm import StatefulInterface, GuardInterface, GuardManager
from pyfsm.guard import ReverseGuard, NullGuard


class TestReverseGuard(unittest.TestCase):
    """ Reverse guard tests """

    @parameterized.expand([
        (True, False),
        (False, True)
    ])
    def test_is_satisfied(self, reversed_value, result):
        """ Tests guard condition """
        context_mock = mock.Mock(StatefulInterface)
        reversed_mock = mock.Mock(GuardInterface)
        reversed_mock.is_satisfied.return_value = reversed_value

        guard = ReverseGuard(reversed_mock)

        self.assertEqual(guard.is_satisfied(context_mock), result)
        reversed_mock.is_satisfied.assert_called_once_with(context_mock)


class TestGuardManager(unittest.TestCase):
    """ Guard manager tests """

    def setUp(self):
        """ Sets up tests environment """
        self.__manager = GuardManager()

    def tearDown(self):
        """ Unsets tests environment """
        del self.__manager

    def test_add_guard(self):
        """ Tests guard adding """
        guard = mock.Mock(GuardInterface)

        self.__manager.add_guard(guard)
        self.assertEqual(
            self.__manager.get_guard(type(guard).__name__),
            guard
        )

    def test_get_absent_guard(self):
        """ Tests getting of absent guard """
        self.assertEqual(
            self.__manager.get_guard('tests'),
            NullGuard
        )


if __name__ == '__main__':
    unittest.main()
