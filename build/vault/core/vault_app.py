'''Central point by which programs get executed'''
import simplejson as json

import vault


class Vault:

    def __init__(self, password):
        self.password = password
        self.datastore = vault.core.Datastore()

    def run(self, program):
        print('running program: ', program.src)
        try:
            program = vault.core.Parser().parse(program)
        except Exception as e:
            # TODO add security and vaulterror
            return self.format_result(["status", "FAILED"])
        status_log = vault.core.Interpreter(self.datastore).execute(program)
        # TODO interpret results and determine status
        result_output = self.format_result(status_log)
        return result_output

    def format_result(self, result):
        return json.dumps(result.result)


if __name__ == '__main__':
    from vault.core import Vault, Parser, Program, Datastore
    vault = Vault("admin")
    prog = Program('''as principal admin password "admin" do
        set x = "Success"
        return x
        ***
        ''')
    result = vault.run(prog)
    print(result)




