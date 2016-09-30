'''The runtime for the program'''

import vault.util
import vault.error
from vault.core.program import *


class Interpreter:

    def __init__(self, datastore):
        self.datastore = datastore
        self.log = []
        self.local = {}
        self.cache = {}
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
                try:
                    status = self.command_handlers[cmd.name](cmd)
                except Exception as e:
                    self.reset()
                    raise  # we're done here
                if status is not None:
                    self.log.append(status)
        datastore_result = self.datastore.commit()
        program.result = self.log
        self.reset()
        return program

    def reset(self):
        self.datastore.cancel()
        self.log = []
        self.local = {}
        self.cache = {}

    ''' Long list of handlers  '''
    def handle_set(self, cmd):
        log = {"status": "SET"}
        output = None
        key = cmd.expressions["key"]
        value = cmd.expressions["value"]
        self.datastore.set(key, value)  # this will de facto check for permission (fail fast)
        self.cache[key] = value  # this reduces the complexity of the database transaction checks
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
        principal = vault.util.Principal(cmd.expressions['principal'], cmd.expressions['password'])
        self.datastore.create_principal(principal)
        return log

    def handle_change_password(self, cmd):
        log = {"status": "CHANGE_PASSWORD"}
        expressions = cmd.expressions
        principal = vault.util.Principal(expressions['principal'], expressions['password'])
        self.datastore.change_password(principal)
        return log

    def handle_append_to(self, cmd):
        log = {"status": "APPEND"}
        key = cmd.expressions['key']
        value_to_append = cmd.expressions['value']
        # see if the value exists and if we can access it
        if self.is_local(key):
            pass

        key_value = self.find_value(key)
        if Type(key_value.expr_type) is not Type.list:
            raise vault.error.VaultError
        # append
        self.datastore.append(key, key)
        return log

    def handle_local(self, cmd):
        log = {"status": "LOCAL"}
        expressions = cmd.expressions
        key = expressions['key']
        # check for existing key
        if self.is_local(key) or self.is_global(key):
            raise vault.error.VaultError(100, "cannot create local variable of existing variable")
        self.local[key] = expressions['value']
        return log

    def handle_foreach(self, cmd):
        log = {"status": "FOREACH"}
        return log

    def handle_set_delegation(self, cmd):
        log = {"status": "SET_DELEGATION"}
        expressions = cmd.expressions
        src_principal = vault.util.Principal(expressions['source_principal'])
        target_principal = vault.util.Principal(expressions['target_principal'])
        role = expressions['right']
        key = expressions['variable']
        self.datastore.set_delegation(src_principal, target_principal, key, role)
        return log

    def handle_delete_delegation(self, cmd):
        log = {"status": "DELETE_DELEGATION"}
        return log

    def handle_default_delegator(self, cmd):
        log = {"status": "DEFAULT_DELEGATOR"}
        return log

    def is_local(self, key):
        if key in self.local:
            return True
        else:
            return False

    # This requires no permission to check unlike find_value
    def is_global(self, key):
        return self.datastore.exists(key)

    def find_value(self, key):
        if key in self.local:
            return self.local[key]
        if key in self.cache:
            return self.cache[key]
        if self.datastore.exists(key):
            return self.datastore.get(key)
        else:
            raise Exception(101, "no key found in database")



if __name__ == '__main__':
    from vault.util import Principal
    from vault.core import Datastore, Program
    interpreter = Interpreter(Datastore())
    program = interpreter.execute(Program(interpreter.fakeTokens))
