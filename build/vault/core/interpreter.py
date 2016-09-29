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
            'set': self.handle_set,
            'return': self.handle_return,
            'exit': self.handle_exit,
            'create_principal': self.handle_create_principal,
            'change_password': self.handle_change_password,
            'append_to': self.handle_append_to,
            'local': self.handle_local,
            'foreach': self.handle_foreach,
            'set_delegation': self.handle_set_delegation,
            'delete_delegation': self.handle_delete_delegation,
            'default_delegator': self.handle_default_delegator
        }

    def execute(self, program):
        context = self.datastore.create_context(vault.util.Principal(program.principal, program.password))
        if context is not None:
            for cmd in program.commands:
                status = self.command_handlers[cmd.name](cmd)
                if status is not None:
                    self.log.append(status)

        datastore_result = self.datastore.commit()
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

    def handle_exit(self, cmd):
        # TODO to exit we finish the current program and tell the server to shutdown not sure how yet
        pass

    def handle_create_principal(self, cmd):
        log = {"status": "CREATE_PRINCIPAL"}
        return log

    def handle_change_password(self, cmd):
        log = {"status": "CHANGE_PASSWORD"}
        expressions = cmd.expressions
        principal = vault.util.Principal(expressions['principal'], expressions['password'])
        self.datastore.change_password(principal)
        return log

    def handle_append_to(self, cmd):
        log = {"status": "APPEND"}
        return log

    def handle_local(self, cmd):
        log = {"status": "LOCAL"}
        return log

    def handle_foreach(self, cmd):
        log = {"status": "FOREACH"}
        return log

    def handle_set_delegation(self, cmd):
        log = {"status": "SET_DELEGATION"}
        return log

    def handle_delete_delegation(self, cmd):
        log = {"status": "DELETE_DELEGATION"}
        return log

    def handle_default_delegator(self, cmd):
        log = {"status": "DEFAULT_DELEGATOR"}
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
