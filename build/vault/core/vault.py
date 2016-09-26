'''Central point by which programs get executed'''

from vault.core import Parser, Interpreter


class Vault:

    def __init__(self, password):
        self.password = password
        # TODO instantiate database
        #self.datastore = DataStore()

    def run(self, program):
        print('running program')
        program = Parser().parse(program)
        result = Interpreter().execute(program)
        # TODO interpret results and determine status
        result = '{"status":"FAILURE"}'
        return result




