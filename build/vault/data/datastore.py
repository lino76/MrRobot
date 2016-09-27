from vault.data.principal import Principal
from vault.error.exceptions import SecurityError

class DataStore():           
        
    principals = {}
    data = {}

    def __init__(self, admin_password):        
        print('DataStore constructor')
        # Reset data
        data = {}

        # Reset principals
        self.principals = { 'admin': Principal('admin', admin_password), 'anyone' : Principal('anyone', None) }          
            
    def authenticate_principal(self, user_id, pwd):
        if user_id in self.principals:
            if self.principals[user_id].authenticate(pwd):
                return True

        raise SecurityError(255, "User not found")
