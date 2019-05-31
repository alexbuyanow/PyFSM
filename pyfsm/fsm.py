"""
    PyFSM.fsm

    Main module
"""

from abc import abstractmethod, ABCMeta
from typing import Any, Dict, List, Optional
from .entity import StatefulInterface
from .guard import GuardManager
from .listener import Event, ListenerManager
from .state import StateFactory, StateManager
from .transition import Transition, TransitionFactory, TransitionTable


class FSMInterface(metaclass=ABCMeta):
    """State Machine Interface"""

    @abstractmethod
    def refresh(self, context: StatefulInterface):
        """ Sets context to actually state """

    @abstractmethod
    def signal(self, context: StatefulInterface, signal: str, params=()):
        """ Sends signal """

    @abstractmethod
    def is_signal(self, context: StatefulInterface, signal: str) -> bool:
        """ Checks is signal transition possible """


class FSM(FSMInterface):
    """ State machine """

    def __init__(self, name: str, transition_table: TransitionTable):
        self.__name = name
        self.__transitions_table = transition_table

    def refresh(self, context: StatefulInterface):
        """ Sets context to actually state """
        transition = self.__get_transition(context)

        while transition:
            self.__perform_transition(context, transition)
            transition = self.__get_transition(context)

    def signal(
            self,
            context: StatefulInterface,
            signal: str,
            params: Optional[Dict[str, Any]] = ()
    ):
        """ Sends signal """
        self.refresh(context)

        transition = self.__get_transition(context, signal)

        if transition:
            self.__perform_transition(context, transition, params)
            self.refresh(context)

    def is_signal(self, context: StatefulInterface, signal: str) -> bool:
        """ Checks is signal transition possible """
        self.refresh(context)

        return bool(self.__get_transition(context, signal))

    def __get_transition(
            self,
            context: StatefulInterface,
            signal: Optional[str] = None
    ) -> Optional[Transition]:
        """ Get possible transition """
        return next(
            self.__transitions_table.find_transitions(context, signal),
            None
        )

    @classmethod
    def __perform_transition(
            cls,
            context: StatefulInterface,
            transition: Transition,
            params: Optional[Dict[str, Any]] = ()
    ):
        """ Makes transition """
        event = Event(
            context,
            transition.state_from,
            transition.state_to,
            transition.signal,
            params
        )

        for listener in transition.before:
            listener.listen(event)

        context.state = transition.state_to

        for listener in transition.after:
            listener.listen(event)


class FSMFactory:
    """ State Machines Factory """

    KEY_STATES: str = 'states'
    KEY_TRANSITIONS: str = 'transitions'

    def __init__(
            self,
            config: Dict[str, Dict[str, Any]],
            guard_manager: GuardManager,
            listener_manager: ListenerManager
    ):
        self.__config = config
        self.__guard_manager = guard_manager
        self.__listener_manager = listener_manager

    def get_fsm(self, context: StatefulInterface) -> FSMInterface:
        """ Gets FSM """
        name = type(context).__name__

        if name not in self.__config:
            message = "FSM with name '{0}' is not found in config".format(name)
            raise FSMNotFoundException(message)

        config = self.__config[name]

        return FSM(name, self.__get_transition_table(name, config))

    def __get_transition_table(self, name: str, config: Dict[str, Any]):
        """ Gets transitions table """
        return TransitionTable(
            self.__get_transition_factory(
                self.__get_states_config(name, config)
            ),
            self.__get_transitions_config(name, config)
        )

    def __get_transition_factory(self, config: Dict[str, Dict[str, str]]):
        """ Gets transition factory """
        state_factory = StateFactory(config)
        state_manager = StateManager()

        for name in config.keys():
            state_manager.add_state(name, state_factory.get_state(name))

        return TransitionFactory(
            state_manager,
            self.__guard_manager,
            self.__listener_manager
        )

    @classmethod
    def __get_sub_config(
            cls,
            name: str,
            config: Dict[str, Dict[str, Any]],
            key: str
    ) -> Any:
        """ Gets sub config by key """
        if key not in config:
            message = "There is no key '{0}' in config {1}".format(name,
                                                                   config)
            raise InvalidConfigException(message)

        return config[key]

    def __get_transitions_config(
            self,
            name: str,
            config: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """ Gets transitions config """
        return self.__get_sub_config(name, config, self.KEY_TRANSITIONS)

    def __get_states_config(
            self,
            name: str,
            config: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """ Gets states config """
        return self.__get_sub_config(name, config, self.KEY_STATES)


class FSMNotFoundException(Exception):
    """ Error if FSM config is not found """


class InvalidConfigException(Exception):
    """ Invalid config Error """
