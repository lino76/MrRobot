
from vault.util import Context, Principal, Role, Vividict
import vault.error

class Datastore:

    def __init__(self):
        self.authentication = {"admin": Principal(name="admin", password="admin")}
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

    '''authorization decoration (because it's kinda cool)'''
    def authorize(role):
        def wrapper(func):
            def authorize_role_wrapper(*args, **kwargs):
                # TODO clean this all up
                if len(args) == 3:
                    self, key, value = args
                else:
                    self, key = args

                if self.is_authorized(self.context.principal, role, key):
                    return func(*args, **kwargs)
                else:
                    raise vault.error.SecurityError(100, "DENIED")
            return authorize_role_wrapper
        return wrapper

    '''authorization decoration impl'''
    def is_authorized(self, principal, role, key):
        if principal.name == 'admin':
            return True
        elif principal.name == 'anyone':  # TODO is this true?
            return False
        else:
            if role == Role.write:
                if key not in self.authorization:
                    # if key does not exist then apply all perms to this key/user and return true
                    #  TODO make mutations to the authorizations also transactional
                    self.authorization[key][principal.name] = [Role.read, Role.write, Role.append, Role.delegate]
                    return True
                # else check the existing key for the proper role
                elif role in self.authorization[key][principal.name]:
                    # they have it
                    return True
                else:
                    # they don't
                    return False
            elif role == Role.read:
                if key not in self.authorization:
                    return False
                elif role in self.authorization[key][principal.name]:
                    return True
            else:
                pass


    '''Authorization API'''
    @authorize(Role.write)
    def set(self, key, value):
        #  TODO validate params or is the parser enough?
        self.context.queue.append(['SET', key, value, None])

    @authorize(Role.read)
    def get(self, key):
        if self.exists(key):
            return self.datatable[key]
        else:
            raise Exception(101, "key does not exist")

    '''Authorization API'''
    @require_context()
    def change_password(self, principal):
        if self.is_admin() or principal.name == self.context.principal.name:
            self.context.queue.append(['CHANGE_PASSWORD', principal.name, principal, None])

    @require_context()
    def create_principal(self, principal):
        if self.is_admin():
            if principal.name not in self.authentication:
                self.context.queue.append(['CREATE_PRINCIPLE', principal.name, principal, None])
            else:
                raise Exception(101, "principal already exists")

    def set_delegation(self, source_principal, target_principal, role):
        pass

    def delete_delegation(self, source_principal, target_principal, role):
        pass


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
        result = []
        for op, key, value, type in self.context.queue:
            if op is "SET":
                self.datatable[key] = value
                result.append({"SET"})
            elif op is "CHANGE_PASSWORD":
                self.authentication[key] = value
                result.append({"CHANGE_PASSWORD"})
            elif op is "CREATE_PRINCIPLE":
                self.authentication[key] = value
                result.append({"CREATE_PRINCIPLE"})
            else:
                raise Exception(100, "Unsupported operation")
        return result

    def cancel(self):
        self.context = None

    def exists(self, key):
        if key in self.datatable:
            return True
        return False

    def is_admin(self):
        return self.context.principal.name == "admin"


if __name__ == '__main__':
    datastore = Datastore()
    context = datastore.create_context(Principal("bob", "password"))
    datastore.set("x", 2)
    datastore.get("x")
    results = datastore.commit()
    print(results)


