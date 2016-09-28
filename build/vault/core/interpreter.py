'''The runtime for the program'''

import vault.util
import vault.error


class Interpreter:

    def __init__(self, datastore):
        self.datastore = datastore
        self.local = {}
        self.context = None
        self.command_handlers = {
            'GET': self.handle_get,
            'SET': self.handle_set,
            'APPEND': None,
            # and one for all the other operations incluging SET_LOCAL
        }
        self.fakeTokens = {"program": {"name": "bob", "password": "password"},
                           "cmds": [{"cmd": "SET", "key": "x", "value": "2"}]
                          }

    def execute(self, program):
        program_tree = program.get_src()
        name, password = program_tree['programs']
        context = self.datastore.create_context(Principal(name, password))
        if context is not None:
            for cmd in program_tree['cmds']:
                self.command_handlers[cmd['cmd']](cmd)
        program.result = self.datastore.commit()
        return program

    ''' Long list of handlers  '''
    def handle_set(self, cmd):
        cmd, key, value = cmd
        self.datastore.set(key, value)

    def handle_get(self, cmd):
        cmd, key = cmd
        self.datastore.set(key)


if __name__ == '__main__':
    from vault.util import Principal
    from vault.core import Datastore, Program
    interpreter = Interpreter(Datastore())
    program = interpreter.execute(Program(interpreter.fakeTokens))
    print(program.result)
