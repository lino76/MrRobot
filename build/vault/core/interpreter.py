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
        expression = cmd.expressions["value"]
        populated_value = self.populate_expression(expression)
        self.datastore.set(key, populated_value)  # this will de facto check for permission (fail fast)
        self.cache[key] = populated_value
        return log

    def populate_expression(self, expression):
        # traverse the object graph of expression and evaluate all fields with whatever data is available
        expression = deepcopy(expression)
        if isinstance(expression, Expression):
            content = expression.get()
            if expression.type is Type.value:
                self.populate_field(expression, content)
            elif expression.type is Type.record:
                self.populate_field(expression, content)
            elif expression.type is Type.list:
                if expression.is_appended():
                    expression.concat_children()
                for child in content:
                    self.populate_field(expression, child)

        return expression

    def populate_field(self, parent, field):
        if isinstance(field, dict):
            for k, v in field.items():
                self.populate_field(field, v)
        elif isinstance(field, list):
            pass
        elif isinstance(field, str):
            pass
        elif field.type is Type.literal:
            pass  # literals are ignored
        elif field.type is Type.record:
            if isinstance(field, Expression):
                self.populate_field(field, field.content)
            else:
                if isinstance(field.value, FieldType):
                    return self.populate_field(field, field.value)
                elif isinstance(field.value, str):
                    field_path = self.tokenize_field(field.value)
                    val = self.find_value_by_path(field_path)
                    self.validate_insert(parent, field, val)
                    # update the field with the new value
                    field.value = self.populate_field(field, val)
                else:
                    pass
        elif field.type is Type.field:
            if isinstance(field.value, str):
                field_path = self.tokenize_field(field.value)
                val = self.find_value_by_path(field_path)
                self.validate_insert(parent, field, val)
                if isinstance(val, Expression):
                    if val.is_appended():
                        val = deepcopy(val)
                        val.concat_children()
                        val.children = []
                field.value = self.populate_field(field, val)
            else:
                pass
        elif field.type is Type.value:
            if isinstance(field, Expression):
                return self.populate_field(field, field.content)
        elif field.type is Type.list:
            for item in field.content:
                self.populate_field(field, item)
        return field

    def validate_insert(self, parent, field, val):
        if val is None:
            raise vault.error.VaultError(100, "expression cannot be evaluated (no value found")
        if val.type is Type.record and isinstance(val, Expression) and isinstance(val.content, dict):
            if isinstance(parent, dict):
                raise vault.error.VaultError(100, 'cannot insert a record')

    def handle_return(self, cmd):
        log = {"status": "RETURNING"}
        expression = cmd.expressions["return_value"]
        # Find the value
        output = None
        # Here we basically have to convert our internal repr of the object graph
        # with the values to be output. we also make copies because these
        # are generally references and it's the datastore that will actually persist them on commit.
        # Our typing is inconsistent so it's messy.
        expression = self.populate_expression(expression)
        # if expression.is_appended():
        #     expression.concat_children()
        output = expression.value()

        # Format the results
        if output is not None:
            # quite a few results will already be converted already. this is a crude conversion below
            if isinstance(output, Expression):
                if isinstance(output.content, list):
                    log["output"] = output.value()
                elif isinstance(output.content, dict):
                    log["output"] = output.value()
                else:
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
        if value_to_append.type is Type.value:
            field_val = value_to_append.get()
            if field_val.type is Type.field:
                value_to_append = self.find_value(field_val.value)

        # value_to_append = deepcopy(value_to_append)  # TODO not working right
        # TODO this has to be populated with the data that exists now or it maybe overwritten
        value_to_append = self.populate_expression(value_to_append)  # TODO not working quite right

        # see if the value exists and if we can access it
        if self.is_local(key):
            # if local we have to do it all here
            # the big difference is that local fields seem to have no permissions TODO (verify this)
            key_value = self.local[key]
            if key_value.type is Type.list:
                key_value.children.append(value_to_append)
        elif self.is_global(key):
            # here we have to push it down to the datastore because this user might not have READ permission
            self.datastore.append(key, value_to_append)
            # The idea here is I might be able to build the append value without getting it from the database
            # this might work because a value has to be created in a program before it can be appended to
            # so it's reference should be in the cache
            if self.is_cached(key):
                root_val = self.cache[key]
            else:
                root_val = self.datastore.get_noperm(key)
            if value_to_append.type is Type.list:
                for item in value_to_append.get():
                    root_val.children.append(item)
            else:
                root_val.children.append(value_to_append)
            self.cache[key] = root_val
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
        if value_key.type is Type.value:
            field_val = value_key.get()
            if field_val.type is Type.literal:
                pass
            elif field_val.type is Type.field:
                value_key = self.find_value(field_val.value)

        self.local[key] = deepcopy(value_key)
        return log

    def handle_foreach(self, cmd):
        log = {"status": "FOREACH"}
        target = cmd.expressions['item']
        list_name = cmd.expressions['list']
        replacer = cmd.expressions['replacer']
        list = self.find_value(list_name)
        if list.type is not Type.list:
            return vault.error.VaultError(100, "can only foreach on a list")
        else:
            new_list_content = []
            for item in list.concat_children():
                new_list_content.append(self.build_replacement(target, item, replacer))
            new_list = deepcopy(list)
            new_list.children = []
            new_list.content = new_list_content
            if self.is_global(list_name):
                self.datastore.set(list_name, new_list)
                self.cache[list_name] = new_list
            else:
                self.local[list_name] = new_list
        return log

    def build_replacement(self, target, item, replacer):
        # add to search path (might want to test first)
        self.local[target] = item

        # replacment
        if replacer.type is Type.value:
            field_val = replacer.get()
            if field_val.type is Type.record:
                path = field_val.value
                keys = path.split('.')
                r_val = self.find_value_by_path(keys)
            else:
                # todo other types
                r_val = field_val.value
        elif replacer.type is Type.record:
            r_val = {}
            field_val = replacer.get()
            if isinstance(field_val, dict):
                for k in field_val.keys():
                    val = field_val[k]
                    if val.type is Type.literal:
                        r_val[k] = val.value
                    elif val.type is Type.field:
                        keys = val.value.split('.')
                        found_val = self.find_value_by_path(keys)
                        if found_val is not None:
                            r_val[k] = found_val.value
                        else:
                            raise vault.error.VaultError(100, 'replacewith expression not found')
                    else:
                        #TODO other types
                        pass
        else:
            pass

        del self.local[target]
        return r_val

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
        expressions = cmd.expressions
        src_principal = vault.util.Principal(expressions['source_principal'])
        target_principal = vault.util.Principal(expressions['target_principal'])
        role = expressions['right']
        key = expressions['variable']
        if self.is_global(key):
            self.datastore.delete_delegation(src_principal, target_principal, key, role)
        else:
            raise vault.error.VaultError(100, "cannot delegate nonexistant or local variables")
        return log

    def handle_default_delegator(self, cmd):
        log = {"status": "DEFAULT_DELEGATOR"}
        expressions = cmd.expressions
        principal = vault.util.Principal(expressions['delegator'])
        self.datastore.default_delegator(principal)
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

    def tokenize_field(self, field_val):
        return field_val.split('.')

    def find_value(self, key):
        if key in self.cache:
            return self.cache[key]
        if key in self.local:
            return self.local[key]
        if self.datastore.exists(key):
            return self.datastore.get(key)
        else:
            raise Exception(101, "no key found in database")

    def find_value_by_path(self, keys):
        root_key = keys.pop(0)
        obj = self.find_value(root_key)
        while len(keys) > 0:
            key = keys.pop(0)
            try:
                if isinstance(obj, Expression):
                    if obj.type is Type.record:
                        obj = obj.get()[key]
                else:
                    obj = obj[key]
            except:
             return None
        return obj





if __name__ == '__main__':
    pass
