from vault.error.exceptions import SecurityError

class Principal():
    rights = []
    def __init__(self, user_id, password, rights = None):
        print('Principal constructor')
        self.user_id = user_id
        self.password = password
        self.rights = rights
    

    def authenticate(self, pwd):
        if self.password == pwd:
            return True
        raise SecurityError(255, "Invalid Password")
    
    