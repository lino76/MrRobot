
class Context:
    def __init__(self, principal):
        self.principal = principal
        self.authenticated = False
        self.queue = []

    def get_queue(self):
        return self.queue

    def keys(self):
        return [_[1] for _ in self.queue]

    def get_principal(self):
        return self.principal
