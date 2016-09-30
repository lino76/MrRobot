'''The runtime for the program'''
from copy import deepcopy

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
        self.program = None
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
            self.program = program
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
        self.program = None
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
        if expression.expr_type is not Type.literal:
            output = self.find_value(expression.content.value)
            if output.expr_type == Type.list.value and len(output.children) > 0:
                output = output.concat_children_values()
        elif expression.expr_type == Type.literal:
            output = expression.content
        if output is not None:
            # TODO there are probably other types
            if isinstance(output, Expression):
                log["output"] = output.content.value
            else:
                log["output"] = output
        return log

    def handle_exit(self, cmd):
        log = {"status": "EXITING"}
        if self.datastore.is_admin():
            self.program.exit = True
        else:
            raise vault.error.SecurityError(100, "unauthorized to shutdown the server")
        return log

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
            # if local we have to do it all here
            # the big difference is that local fields seem to have no permissions TODO (verify this)
            key_value = self.local[key]
            if Type(key_value.expr_type) is Type.list:
                key_value.children.append(value_to_append)
        elif self.is_global(key):
            # here we have to push it down to the datastore because this user might not have READ permission
            self.datastore.append(key, value_to_append)
            # The idea here is I might be able to build the append value without getting it from the database
            # this might work because a value has to be created in a program before it can be appended to
            # so it's reference should be in the cache
            if self.is_cached(key):
                self.cache[key].children.append(value_to_append)
        return log

    def handle_local(self, cmd):
        log = {"status": "LOCAL"}
        expressions = cmd.expressions
        key = expressions['key']
        # check for existing key
        if self.is_local(key) or self.is_global(key):
            raise vault.error.VaultError(100, "cannot create local variable of existing variable")
        # get value of expression
        value_key = expressions['value']
        if value_key.content.type is Type.literal:
            value = value_key.content.value
        else:
            value = self.find_value(value_key.content.value)
        self.local[key] = deepcopy(value)
        return log

    def handle_foreach(self, cmd):
        log = {"status": "FOREACH"}
        target = expressions['item']
        list_name = expressions['list']
        replacer = expressions['replacer']

        return log

    def handle_set_delegation(self, cmd):
        log = {"status": "SET_DELEGATION"}
        expressions = cmd.expressions
        src_principal = vault.util.Principal(expressions['source_principal'])
        target_principal = vault.util.Principal(expressions['target_principal'])
        role = expressions['right']
        key = expressions['variable']
        if self.is_global(key):
            self.datastore.set_delegation(src_principal, target_principal, key, role)
        else:
            raise vault.error.VaultError(100, "cannot delegate nonexistant or local variables")
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
        return False

    # This requires no permission to check unlike find_value
    def is_global(self, key):
        return self.datastore.exists(key)

    def is_cached(self, key):
        if key in self.cache:
            return True
        return False

    def find_value(self, key):
        if key in self.cache:
            return self.cache[key]
        if key in self.local:
            return self.local[key]
        if self.datastore.exists(key):
            return self.datastore.get(key)
        else:
            raise Exception(101, "no key found in database")


if __name__ == '__main__':
    pass
