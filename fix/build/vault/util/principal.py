

class Principal:
    def __init__(self, name, password=None):
        self.name = name
        self.password = password
        # delegated are users we've inherited
        self.delegated = []

    def add_delegate(self, principal):
        self.delegated.append(principal.name)
