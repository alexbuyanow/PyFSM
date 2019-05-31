"""
    PyFSM

    Listeners module tests

"""

import unittest
import mock
from pyfsm import (
    ListenerManager,
    ListenerInterface,
    ListenerNotFoundException
)


class TestListenerManager(unittest.TestCase):
    """ Listener manager tests """

    def setUp(self):
        """ Sets up tests environment """
        self.__manager = ListenerManager()

    def tearDown(self):
        """ Unsets tests environment """
        del self.__manager

    def test_add_listener(self):
        """ Tests listener adding """
        listener = mock.Mock(ListenerInterface)

        self.__manager.add_listener(listener)
        self.assertEqual(
            self.__manager.get_listener(type(listener).__name__),
            listener
        )

    def test_get_listener_not_found_exception(self):
        """ Tests error on absent listener getting """
        with self.assertRaisesRegex(
                ListenerNotFoundException,
                "Listener 'tests' is not found"
        ):
            self.__manager.get_listener('tests')


if __name__ == '__main__':
    unittest.main()
