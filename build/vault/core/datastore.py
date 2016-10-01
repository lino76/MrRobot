from enum import Enum
from copy import deepcopy

from vault.util import Context, Principal, Role, Vividict
import vault.error


class Transaction:
    def __init__(self, op=None, key=None, value=None, principal=None, roles=None):
        self.op = op
        self.key = key
        self.value = value
        self.principal = principal
        self.roles = roles


class TxnTypes(Enum):
    set = "SET"
    change_password = "CHANGE_PASSWORD"
    create_principal = "CREATE_PRINCIPAL"
    grant = "GRANT"
    delegate_add = "ADD_DELEGATE"
    append = "APPEND"


class Datastore:

    def __init__(self):
        self.authentication = {"admin": Principal(name="admin", password="admin"),
                               "anyone": Principal(name="admin")}
        self.authorization = Vividict()
        self.datatable = Vividict()
        self.context = None

    def require_context():
        def wrapper(func):
            def check_context(*args, **kwargs):
                self = args[0]
                if self.context is not None:
                    return func(*args, **kwargs)
                else:
                    raise Exception("DENIED")
            return check_context
        return wrapper

    '''Authorization API'''
    @require_context()
    def set(self, key, value):
        principal = self.context.principal
        if self.exists(key):
            # check rights
            if not self.has_role(key, Role.write, principal):
                raise vault.error.SecurityError(100, "DENIED")
            else:
                self.add_transaction(Transaction(op=TxnTypes.set, key=key, value=value))
        else:
            # check rights
            grants = self.authorization[key][principal.name]
            if Role.write not in grants and not self.is_admin():
                raise vault.error.SecurityError(100, "DENIED")
            else:
                # init roles list
                self.authorization[key][principal.name] = []
                # add data and new roles
                self.add_transaction(Transaction(op=TxnTypes.set, key=key, value=value))
                self.add_transaction(Transaction(op=TxnTypes.grant, key=key, principal=principal,
                                                 roles=[Role.read, Role.write, Role.append, Role.delegate]))
                # add roles to admin
                if not self.is_admin():
                    self.add_transaction(Transaction(op=TxnTypes.grant, key=key, principal=Principal("admin"),
                                                     roles=[Role.read, Role.write, Role.append, Role.delegate]))

    @require_context()
    def append(self, key, value):
        # check for the right permissions (write and append)
        principal = self.context.principal
        if self.exists(key):
            grants = self.authorization[key][principal.name]
            if Role.write not in grants and Role.append not in grants and not self.is_admin():
                raise vault.error.SecurityError(100, "DENIED")
            else:
                self.add_transaction(Transaction(op=TxnTypes.append, key=key, value=value))
        else:
            raise vault.error.VaultError(100, "cant append to missing value")

    @require_context()
    def get(self, key):
        principal = self.context.principal
        if self.exists(key):
            # check rights
            grants = self.authorization[key][principal.name]
            if Role.read not in grants and not self.is_admin():
                raise vault.error.SecurityError(100, "DENIED")
            # return data
            return self.datatable[key]
        else:
            raise vault.error.VaultError(101, "key does not exist")

    @require_context()
    def get_noperm(self, key):
        # This is a convenience method for APPEND_TO that lets a value be read if the user has WRITE and APPEND perms
        # but not READ
        principal = self.context.principal
        grants = self.authorization[key][principal.name]
        if Role.write not in grants and Role.append not in grants and not self.is_admin():
            raise vault.error.SecurityError(100, "DENIED")
        else:
            if key in self.datatable:
                return self.datastore['key']
            else:
                #it must be in the queue
                pass


    '''Authorization API'''
    @require_context()
    def change_password(self, principal):
        if self.is_admin() or principal.name == self.context.principal.name:
            self.add_transaction(Transaction(op=TxnTypes.change_password, key=principal.name, value=principal))

    @require_context()
    def create_principal(self, principal):
        if self.is_admin():
            if principal.name not in self.authentication:
                self.add_transaction(Transaction(op=TxnTypes.create_principal, key=principal.name, value=principal))
            else:
                raise Exception(101, "principal already exists")

    @require_context()
    def set_delegation(self, source_principal, target_principal, key, role):
        # First check if source and target principals exist
        if self.principle_exists(source_principal) and self.principle_exists(target_principal):
            # check if current is admin or source
            if self.is_admin() or self.is_current(source_principal):
                # check if q has permission to delegate for key
                if self.has_role(key, Role.delegate, source_principal):
                    # they are good to go
                    self.add_transaction(Transaction(op=TxnTypes.delegate_add, key=key,
                                                     principal=target_principal, roles=Role(role)))
                else:
                    raise vault.error.SecurityError(100, "principal requires delegate permission")
            else:
                raise vault.error.SecurityError(100, "can only delegate for yourself")
        else:
            raise vault.error.VaultError(100, "principals do not exist")


    @require_context()
    def delete_delegation(self, source_principal, target_principal, role):
        pass

    @require_context()
    def default_delegator(self, principal):
        pass

    def create_context(self, principal):
        if principal.name in self.authentication:
            if principal.password != self.authentication[principal.name].password:
                raise Exception(1, "Invalid Password")
        self.context = Context(principal)
        self.context.authenticated = True
        self.authentication[principal.name] = principal
        return self.context

    ''' This is where we actually persist the data'''
    def commit(self):
        for txn in self.context.queue:

            if txn.op is TxnTypes.set:
                self.datatable[txn.key] = txn.value

            elif txn.op is TxnTypes.change_password:
                self.authentication[txn.key] = txn.value

            elif txn.op is TxnTypes.create_principal:
                self.authentication[txn.key] = txn.value

            elif txn.op is TxnTypes.grant:
                # TODO there's probably a better way to merge into a unique list
                existing = self.authorization[txn.key][txn.principal.name]
                merged = list(set(existing + txn.roles))
                self.authorization[txn.key][txn.principal.name] = merged

            elif txn.op is TxnTypes.delegate_add:
                existing_roles = self.authorization[txn.key][txn.principal.name]
                if not isinstance(existing_roles, list):
                    existing_roles = []
                if txn.roles not in existing_roles:
                    existing_roles.append(txn.roles)
                    self.authorization[txn.key][txn.principal.name] = existing_roles

            elif txn.op is TxnTypes.append:
                # this was a nice idea but I'm not sure it's going to fly.
                existing_value = self.datatable[txn.key]
                appended_value = existing_value.concat_children()
                existing_value.content = appended_value
                existing_value.children = []
                #self.datatable[txn.key] = deepcopy(txn.value)

            else:
                raise Exception(100, "Unsupported operation")
        return "success"

    def cancel(self):
        self.context = None

    def principle_exists(self, principal):
        # check for stored users
        if principal.name in self.authentication:
            return True
        # check for pending users
        for txn in self.context.queue:
            if txn.op is TxnTypes.create_principal and txn.value.name == principal.name:
                return True
        # None found
        return False

    def exists(self, key):
        if key in self.datatable:
            return True
        else:
            for txn in self.context.queue:
                # TODO add append
                if txn.op is TxnTypes.set and txn.key == key:
                    return True
        return False

    def is_current(self, principal):
        if self.context.principal.name == principal.name:
            return True
        else:
            return False

    def has_role(self, key, role, principal):
        existing = self.authorization[key][principal.name]
        pending = []
        for txn in self.context.queue:
            if txn.op is TxnTypes.grant and txn.principal.name == principal.name and txn.key == key:
                pending += txn.roles
        merged = list(set(existing + pending))
        if role in merged:
            return True
        else:
            return False

    def add_transaction(self, txn):
        self.context.queue.append(txn)

    @require_context()
    def is_admin(self):
        return self.context.principal.name == "admin"


if __name__ == '__main__':
    datastore = Datastore()
    context = datastore.create_context(Principal("bob", "password"))
    datastore.set("x", 2)
    datastore.get("x")
    results = datastore.commit()
    print(results)


