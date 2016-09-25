from vault.data.principal import Principal

class DataStore():
    principals = {}
    data = {}

    def __init__(self):
        print('DataStore constructor')
        # Reset data
        data = {}

        # Reset principals
        principals = { 'admin': Principal('admin', 'admin'), 'anyone' : Principal('anyone', None) }

            
    def authenticate_principal(self, user_id, pwd):
        if user_id in self.principals:
            return self.principals[user_id].authenticate(pwd)

        return false