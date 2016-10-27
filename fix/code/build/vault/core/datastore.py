from enum import Enum

from vault.util import Context, Principal, Role, Vividict
import vault.error


class Transaction:
    def __init__(self, op=None, key=None, value=None, principal=None, roles=None, source_principal=None):
        self.op = op
        self.key = key
        self.value = value
        self.principal = principal
        self.roles = roles
        self.source_principal = source_principal


class TxnTypes(Enum):
    set = "SET"
    change_password = "CHANGE_PASSWORD"
    create_principal = "CREATE_PRINCIPAL"
    grant = "GRANT"
    delegate_add = "ADD_DELEGATE"
    delegate_remove = "REMOVE_DELEGATE"
    append = "APPEND"
    default_delegator = "DEFAULT_DELEGATOR"


class Datastore:

    def __init__(self, password):
        self.authentication = {"admin": Principal(name="admin", password=password),
                               "anyone": Principal(name="admin")}
        self.authorization = Vividict()
        self.delegation = Vividict({"anyone": Vividict()})
        self.local = {"default_delegate": "anyone"}
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
            if not self.check_role(key, Role.write, principal):
                raise vault.error.SecurityError(100, "DENIED")
            else:
                self.add_transaction(Transaction(op=TxnTypes.set, key=key, value=value))
        else:
            # init roles list
            self.authorization[key][principal.name] = []
            # add data
            self.add_transaction(Transaction(op=TxnTypes.set, key=key, value=value))
            # add delegation from admin -> current
            self.add_transaction(Transaction(op=TxnTypes.delegate_add, key=key, principal=principal,
                                             source_principal="admin",
                                             roles=[Role.read, Role.write, Role.append, Role.delegate]))
            # add roles to admin
            self.add_transaction(Transaction(op=TxnTypes.grant, key=key, principal=Principal("admin"),
                                             roles=[Role.read, Role.write, Role.append, Role.delegate]))

    @require_context()
    def append(self, key, value):
        # check for the right permissions (write and append)
        principal = self.context.principal
        if self.exists(key):
            # grants = self.authorization[key][principal.name]
            # if Role.write not in grants and Role.append not in grants and not self.is_admin():

            if not self.check_role(key, Role.append, principal):
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
            # grants = self.authorization[key][principal.name]
            # if Role.read not in grants and not self.is_admin():
            if not self.check_role(key, [Role.read], principal):
                raise vault.error.SecurityError(100, "DENIED")
            # return data
            return self.datatable[key]
        else:
            raise vault.error.VaultError(101, "key does not exist")

    @require_context()
    def get_noperm(self, key):
        # There is no spoon.
        principal = self.context.principal
        # grants = self.authorization[key][principal.name]
        # if Role.write not in grants and Role.append not in grants and not self.is_admin():
        if not self.check_role(key, [Role.append, Role.write], principal):
            raise vault.error.SecurityError(100, "DENIED")
        else:
            if key in self.datatable:
                return self.datatable[key]
            else:
                #it must be in the queue
                pass


    '''Authorization API'''
    @require_context()
    def change_password(self, principal):
        if self.is_admin() or principal.name == self.context.principal.name:
            self.add_transaction(Transaction(op=TxnTypes.change_password, key=principal.name, value=principal))
        else:
            raise vault.error.SecurityError(100, "cannot change someone else's password")

    @require_context()
    def create_principal(self, principal):
        if self.is_admin():
            if principal.name not in self.authentication:
                self.add_transaction(Transaction(op=TxnTypes.create_principal, key=principal.name, value=principal))
            else:
                raise vault.SecurityError(101, "principal already exists")

    @require_context()
    def set_delegation(self, source_principal, target_principal, key, role):
        # First check if source and target principals exist
        if self.principle_exists(source_principal) and self.principle_exists(target_principal):
            # check if current is admin or source
            if self.is_admin() or self.is_current(source_principal):
                # check if q has permission to delegate for key
                if self.is_admin() or self.check_role(key, [Role.delegate], source_principal):
                    # they are good to go
                    self.add_transaction(Transaction(op=TxnTypes.delegate_add,
                                                     key=key,
                                                     source_principal=source_principal,
                                                     principal=target_principal,
                                                     roles=Role(role)))
                else:
                    raise vault.error.SecurityError(100, "principal requires delegate permission")
            else:
                raise vault.error.SecurityError(100, "can only delegate for yourself")
        else:
            raise vault.error.VaultError(100, "principal does not exist")


    @require_context()
    def delete_delegation(self, source_principal, target_principal, key, role):
        if self.is_admin():
            if self.principle_exists(source_principal):
                self.add_transaction(Transaction(op=TxnTypes.delegate_remove,
                                                 key=key,
                                                 source_principal=source_principal,
                                                 principal=target_principal,
                                                 roles=Role(role)))
            else:
                raise vault.error.VaultError(100, "principal does not exist")
        else:
            raise vault.error.SecurityError(100, "only admin can set the default delegator")

    @require_context()
    def default_delegator(self, principal):
        if self.is_admin():
            if self.principle_exists(principal):
                self.add_transaction(Transaction(op=TxnTypes.default_delegator, principal=principal))
            else:
                raise vault.error.VaultError(100, "principal does not exist")
        else:
            raise vault.error.SecurityError(100, "only admin can set the default delegator")

    def create_context(self, principal):
        if principal.name in self.authentication:
            if principal.password != self.authentication[principal.name].password:
                raise vault.error.SecurityError(1, "Invalid Password")
        self.context = Context(principal)
        self.context.authenticated = True
        self.authentication[principal.name] = principal
        return self.context

    ''' This is where we actually persist the data'''

    def commit(self):
        for i in range(0, len(self.context.queue)):
            txn = self.context.queue[i]

            if txn.op is TxnTypes.set:
                self.datatable[txn.key] = txn.value

            elif txn.op is TxnTypes.change_password:
                self.authentication[txn.key] = txn.value

            elif txn.op is TxnTypes.create_principal:
                self.add_principal(txn.value)

            elif txn.op is TxnTypes.grant:
                self.add_role(key=txn.key, principal=txn.principal, roles=txn.roles)

            elif txn.op is TxnTypes.delegate_add:
                self.add_delegate(key=txn.key, principal=txn.principal,
                                  source_principal=txn.source_principal,  roles=txn.roles)

            elif txn.op is TxnTypes.delegate_remove:
                self.remove_delegate(key=txn.key, principal=txn.principal,
                                     source_principal=txn.source_principal, roles=txn.roles)

            elif txn.op is TxnTypes.append:
                existing_value = self.datatable[txn.key]
                appended_value = existing_value.concat_children()
                existing_value.content = appended_value
                existing_value.children = []

            elif txn.op is TxnTypes.default_delegator:
                self.add_default_delegate(txn.principal.name)

            else:
                raise vault.error.VaultError(100, "Unsupported operation")
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

    def check_role(self, key=None, role=None, principal=None):
        if not isinstance(role, list):
            role = [role]
        existing_roles = self.get_current_roles(key, principal)
        for target_role in role:
            # first just check and see if we already have any of these roles
            if target_role in existing_roles:
                return True
            else:
                for delegate in self.delegation[principal.name][key]:
                    # for delegates that allow 'target_role'
                    delegated_roles = self.delegation[principal.name][key][delegate]
                    if target_role in delegated_roles:
                        return True
                        # if self.check_role(key, target_role, Principal(delegate)):
                        #     return True
        return False

    def get_current_roles(self, key=None, principal=None):
        try:
            merged = []
            existing = self.authorization[key][principal.name]
            if isinstance(existing, Vividict):
                existing = [existing.items()]
            if existing:
                for role in existing:
                    merged.append(role)
            for txn in self.context.queue:
                if txn.op is TxnTypes.grant and txn.principal.name == principal.name and txn.key == key:
                    merged += txn.roles
        except:
            raise vault.error.VaultError(100, "unable to find existing roles")
        return merged

    def add_role(self, key=None, roles=None, principal=None):
        for role in roles:
            existing = self.authorization[key][principal.name]
            try:
                if role not in existing:
                    existing.append(role)
            except:
                raise vault.error.VaultError(100, "unable to commit roles")

    def remove_delegate(self, key=None, roles=None, principal=None, source_principal=None):
        if isinstance(principal, Principal):
            pname = principal.name
        else:
            pname = principal
        if isinstance(source_principal, Principal):
            sname = source_principal.name
        else:
            sname = source_principal

        if not isinstance(roles, list):
            roles = [roles]

        # existing_roles = self.delegation[pname][key][sname]
        existing_delegates = self.delegation[pname][key]
        if sname in existing_delegates:
            # TODO FIX THIS
            existing_roles = existing_delegates[sname]
            if isinstance(existing_roles, Vividict):
                existing = [existing_roles.items()]
            if not isinstance(existing_roles, list):
                count = len(existing_roles.items())
            else:
                count = len(existing_roles)
            # Remove the roles
            if count != 0:
                new_roles = [_ for _ in existing_roles if _ not in roles]
                self.delegation[pname][key][sname] = new_roles
            else:
                #roles are empty
                pass

    def add_delegate(self, key=None, roles=None, principal=None, source_principal=None):
        if isinstance(principal, Principal):
            pname = principal.name
        else:
            pname = principal
        if isinstance(source_principal, Principal):
            sname = source_principal.name
        else:
            sname = source_principal

        if not isinstance(roles, list):
            roles = [roles]

        existing_roles = self.delegation[pname][key][sname]
        if not isinstance(existing_roles, list):
            count = len(existing_roles.items())
        else:
            count = len(existing_roles)
        # Add the roles
        if count == 0:
            self.delegation[pname][key][sname] = roles
        else:
            for role in roles:
                try:
                    if role not in existing_roles:
                        existing_roles.append(role)
                except:
                    raise vault.error.VaultError(100, "unable to add delegate roles")
            self.delegation[pname][key][sname] = existing_roles

    def add_principal(self, principal):
        # add users credentials
        self.authentication[principal.name] = principal
        # add default delegation
        default_delegates = self.delegation[self.get_default_delegate()]
        self.delegation[principal.name] = Vividict(default_delegates)

    def delete_delegate(self, key=None, role=None, delegate=None):
        pass

    def add_default_delegate(self, principal=None):
        self.local["default_delegate"] = principal

    def get_default_delegate(self):
        return self.local["default_delegate"]

    def add_transaction(self, txn):
        self.context.queue.append(txn)

    def is_admin(self):
        return self.context.principal.name == "admin"


