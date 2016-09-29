'''Central point by which programs get executed'''
import simplejson as json

import vault
import vault.error


class Vault:

    def __init__(self, password):
        self.password = password
        self.datastore = vault.core.Datastore()

    def run(self, program):
        print('running program: ', program.src)

        print('parsing program:')
        try:
            program = vault.core.Parser().parse(program)
        except Exception as e:
            print("Parsing exception: " + str(e))
            # TODO add security and vaulterror
            return self.format_result(result='"status", "FAILED"')

        print('executing program')
        try:
            program_result = vault.core.Interpreter(self.datastore).execute(program)
        except vault.error.SecurityError as se:
            return self.format_result(result='"status", "DENIED"')
        except Exception as e:
            print("error running program:", str(e))
            return self.format_result(result='"status", "FAILED"')

        # TODO interpret results and determine status
        print('program complete')
        result_output = self.format_result(program=program_result)
        return result_output

    def format_result(self, program=None, result=None):
        if program:
            return json.dumps(program.result)
        else:
            return json.dumps(result)


if __name__ == '__main__':
    from vault.core import Vault, Parser, Program, Datastore
    vault = Vault("admin")
    # prog = Program('''as principal admin password "admin" do
    #     set x = "Success"
    #     change password admin "password"
    #     create principal bob "B0BPWxxd"
    #     return x
    #     ***
    #     ''')

    prog1 = Program('''as principal admin password "admin" do
        create principal bob "B0BPWxxd"
        set x = "my string"
        return x
        ***
        ''')
    prog2 = Program('''as principal bob password "B0BPWxxd" do
        return x
        ***
        ''')
    prog3 = Program('''as principal bob password "B0BPWxxd" do
        set x = "another string"
        return x
        ***
        ''')
    #set delegation x admin read -> bob
    result = vault.run(prog1)
    print(result)
    result = vault.run(prog2)
    print(result)
    result = vault.run(prog3)
    print(result)




