

class Principal():
    rights = []
    def __init__(self, user_id, password, rights = None):
        print('Principal constructor')
        self.user_id = user_id
        self.password = password
        self.rights = rights
    

    def authenticate(pwd):
        return password == pwd
    
    