"""
    PyFSM.transition

    Transitions module

"""

from dataclasses import dataclass
from functools import reduce
from typing import Any, Dict, Iterator, List, Optional
from .entity import StatefulInterface
from .state import StateInterface, StateManager
from .guard import GuardInterface, GuardManager
from .listener import ListenerInterface, ListenerManager


@dataclass
class Transition:
    """ Transition """

    __state_from: StateInterface
    __state_to: StateInterface
    __signal: str or None = None
    __guards: List[GuardInterface] = ()
    __before: List[ListenerInterface] = ()
    __after: List[ListenerInterface] = ()

    @property
    def state_from(self) -> StateInterface:
        """ Gets original state """
        return self.__state_from

    @property
    def state_to(self) -> StateInterface:
        """ Gets final state """
        return self.__state_to

    @property
    def signal(self) -> str or None:
        """ Get signal """
        return self.__signal

    @property
    def guards(self) -> List[GuardInterface]:
        """ Get guards list """
        return self.__guards

    @property
    def before(self) -> List[ListenerInterface]:
        """ Gets before transition listeners list """
        return self.__before

    @property
    def after(self) -> List[ListenerInterface]:
        """ Gets after transition listeners list """
        return self.__after


class TransitionFactory:
    """ Transitions factory """

    KEY_STATE_FROM: str = 'from'
    KEY_STATE_TO: str = 'to'
    KEY_SIGNAL: str = 'signal'
    KEY_GUARD: str = 'guards'
    KEY_BEFORE: str = 'before'
    KEY_AFTER: str = 'after'

    def __init__(
            self,
            state_manager: StateManager,
            guard_manager: GuardManager,
            listener_manager: ListenerManager
    ):
        self.__state_manager = state_manager
        self.__guard_manager = guard_manager
        self.__listener_manager = listener_manager

    def get_transition(self, config: Dict[str, Any]) -> Transition:
        """ Gets transition """
        if self.KEY_STATE_FROM not in config:
            message = "Initial state not found in config {0}".format(config)
            raise InvalidTransitionConfig(message)

        if self.KEY_STATE_TO not in config:
            message = "Final state not found in config {0}".format(config)
            raise InvalidTransitionConfig(message)

        return Transition(
            self.__state_manager.get_state(config[self.KEY_STATE_FROM]),
            self.__state_manager.get_state(config[self.KEY_STATE_TO]),
            config.get(self.KEY_SIGNAL, None),
            self.__get_guards(config.get(self.KEY_GUARD, [])),
            self.__get_listeners(config.get(self.KEY_BEFORE, [])),
            self.__get_listeners(config.get(self.KEY_AFTER, []))
        )

    def __get_guards(self, config: List[str]) -> List[GuardInterface]:
        """ Gets guards """
        return [self.__guard_manager.get_guard(name) for name in config]

    def __get_listeners(
            self,
            config: List[str]
    ) -> List[ListenerInterface]:
        """ Gets listeners """
        return [self.__listener_manager.get_listener(name) for name in config]


class TransitionTable:
    """ Transitions table """

    def __init__(
            self,
            transition_factory: TransitionFactory,
            transition_config: List[Dict[str, str]]
    ):
        self.__transitions = []
        self.__position = 0

        for transition in transition_config:
            self.add_transition(transition_factory.get_transition(transition))

    def __iter__(self) -> Iterator[Transition]:
        return self

    def __next__(self):
        self.__position += 1
        try:
            return self.__transitions[self.__position - 1]
        except IndexError:
            self.__position = 0
            raise StopIteration

    def find_transitions(
            self,
            context: StatefulInterface,
            signal: Optional[str] = None
    ) -> Iterator[Transition]:
        """ Finds possible transitions """
        return filter(
            lambda transition:
            transition.state_from == context.state and
            transition.signal == signal and
            reduce(
                lambda result, guard: result and guard.is_satisfied(context),
                transition.guards,
                True
            ),
            self.__transitions
        )

    def add_transition(self, transition: Transition):
        """ Adds transition to table """
        self.__transitions.append(transition)


class InvalidTransitionConfig(Exception):
    """ Incorrect transition config error """
