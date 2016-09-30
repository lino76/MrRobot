

class Principal:
    def __init__(self, name, password=None):
        self.name = name
        self.password = password
        # delegated are users we've inherited
        if self.name is not 'anyone':
            self.delegated = ["anyone"]
        else:
            self.delegated = []

