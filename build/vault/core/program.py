'''Represents the program to be executed'''


class Program:

    def __init__(self, src):
        self.status = None
        self.result = None
        self.src = src

    def get_status(self):
        return self.status

    def get_result(self):
        return self.result

    def get_src(self):
        return self.src
