'''Represents the transient state of the program'''


class Transaction:

    def __init__(self, src):
        self.src = src
        self.state = []

    def add_data(self, data):
        self.state.append(data)






