"""
    PyFSM

    Simple FSM example
"""

import pyfsm


class SimpleContext(pyfsm.StatefulInterface):
    """ Example stateful entity """

    state = pyfsm.State('init')
    is_valid = True


class ValidGuard(pyfsm.GuardInterface):
    """ Context is valid guard """

    def is_satisfied(self, target: SimpleContext) -> bool:
        """ Checks guard condition """
        return target.is_valid


class EchoListener(pyfsm.ListenerInterface):
    """ Echo text listener """

    def listen(self, event: pyfsm.Event):
        """ Processes transition event """
        print('Transition from "%s" to "%s" by "%s" (params: %s)' %
              (event.state_from, event.state_to, event.signal, event.params))


def main():
    """ Executing """
    config = {
        'SimpleContext': {
            'states': {
                'init': {'type': pyfsm.StateInterface.TYPE_REGULAR},
                'created': {'type': pyfsm.StateInterface.TYPE_REGULAR},
                'valid': {'type': pyfsm.StateInterface.TYPE_REGULAR},
                'invalid': {'type': pyfsm.StateInterface.TYPE_REGULAR},
                'finish': {'type': pyfsm.StateInterface.TYPE_REGULAR},
            },
            'transitions': [
                {
                    'from': 'init',
                    'to': 'created'
                },
                {
                    'from': 'created',
                    'to': 'valid',
                    'guards': ('ValidGuard',)
                },
                {
                    'from': 'created',
                    'to': 'invalid',
                    'guards': ('!ValidGuard',)
                },
                {
                    'from': 'valid',
                    'to': 'finish',
                    'signal': 'finish',
                    'before': ('EchoListener',),
                    'after': ('EchoListener',)
                }
            ]
        }
    }

    guard_manager = pyfsm.GuardManager()
    guard_manager.add_guard(ValidGuard())
    listener_manager = pyfsm.ListenerManager()
    listener_manager.add_listener(EchoListener())

    factory = pyfsm.FSMFactory(config, guard_manager, listener_manager)
    context = SimpleContext()
    fsm = factory.get_fsm(context)

    print(context.state)
    fsm.refresh(context)
    print(context.state)
    print('Is "finish" signal possible?', fsm.is_signal(context, 'finish'))
    fsm.signal(context, 'finish', {'tests': 'tests'})
    print(context.state)


if __name__ == '__main__':
    main()
