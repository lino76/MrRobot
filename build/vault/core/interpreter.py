'''The runtime for the program'''

import vault.util
import vault.error
from vault.core.program import *


class Interpreter:

    def __init__(self, datastore):
        self.datastore = datastore
        self.log = []
        self.local = {}
        self.context = None
        self.command_handlers = {
            'get': self.handle_get,
            'set': self.handle_set,
            'return': self.handle_return,
            'exit': None,
            'create_principal': None,
            'change_password': None,
            'append_to': None,
            'local': None,
            'foreach': None,
            'set_delegation': None,
            'delete_delegation': None,
            'default_delegator': None
        }

    def execute(self, program):
        context = self.datastore.create_context(vault.util.Principal(program.principal, program.password))
        if context is not None:
            for cmd in program.commands:
                status = self.command_handlers[cmd.name](cmd)
                if status is not None:
                    self.log.append(status)

        datastore_result = self.datastore.commit()
        # TODO create result log
        # TODO clear global
        program.result = self.log
        self.reset()
        return program

    def reset(self):
        self.log = []
        self.local = {}

    ''' Long list of handlers  '''
    def handle_set(self, cmd):
        log = {"status": "SET"}
        output = None
        key = cmd.expressions["key"]
        value = cmd.expressions["value"]
        self.local[key] = value  # keep it around for future use
        self.datastore.set(key, value)  # this will de facto check for permission (fail fast)
        return log

    def handle_get(self, cmd):
        cmd, key = cmd
        self.datastore.set(key)

    def handle_return(self, cmd):
        log = {"status": "RETURNING"}
        output = None
        expression = cmd.expressions["return_value"]
        # figure out what the type is e.g. literal, variable, etc
        # figure out if it's in local or global
        # fetch it from where ever it is
        if expression.expr_type is not Type.literal:
            output = self.find_value(expression.content.value)
        elif expression.expr_type == Type.literal:
            output = expression.content
        # Return
        if output is not None:
            log["output"] = output.content.value
        return log

    def find_value(self, key):
        if key in self.local:
            return self.local[key]
        if self.datastore.exists(key):
            return self.datastore(key)
        else:
            raise Exception(101, "no key found in database")



if __name__ == '__main__':
    from vault.util import Principal
    from vault.core import Datastore, Program
    interpreter = Interpreter(Datastore())
    program = interpreter.execute(Program(interpreter.fakeTokens))
    print(program.result)
