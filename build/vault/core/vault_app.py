'''Central point by which programs get executed'''

import vault

class Vault:

    def __init__(self, password):
        self.password = password
        # TODO instantiate database
        self.datastore = vault.core.Datastore()

    def run(self, program):
        print('running program')
        program = vault.core.Parser().parse(program)
        result = vault.core.Interpreter(self.datastore ).execute(program)
        # TODO interpret results and determine status
        result = '{"status":"FAILURE"}'
        return result




