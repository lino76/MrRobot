'''Central point by which programs get executed'''
import simplejson as json
from string import Template

import vault
import vault.error


class Vault:

    def __init__(self, password):
        self.password = password
        self.datastore = vault.core.Datastore()

    def run(self, program):
        print('running program: ', program.src)

        print('parsing program..')
        try:
            program = vault.core.Parser().parse(program)
        except Exception as e:
            print("Parsing exception: " + str(e))
            # TODO add security and vaulterror
            return self.format_result([{"status": "FAILED"}])

        print('executing program..')
        try:
            program_result = vault.core.Interpreter(self.datastore).execute(program)
        except vault.error.SecurityError as se:
            return self.format_result([{"status": "DENIED"}])
        except Exception as e:
            print("error running program:", str(e))
            return self.format_result([{"status": "FAILED"}])

        # TODO interpret results and determine status
        print('program complete')
        result_output = self.format_result(program_result.result)
        return result_output

    def format_result(self, result_log):
        output = ""
        returning = Template('{"status": "$status", "output": "$output"}\n')
        operation = Template('{"status": "$status"}\n')
        for entry in result_log:
            status = entry['status']
            if status == "RETURNING":
                output += returning.substitute(status=entry['status'], output=entry['output'])
            else:
                output += operation.substitute(status=entry['status'])
        return output


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

# Test 1
#     prog1 = Program('''as principal admin password "admin" do
#         create principal bob "B0BPWxxd"
#         set x = "my string"
#         set delegation x admin read -> bob
#         return x
#         ***
#         ''')
#     prog2 = Program('''as principal bob password "B0BPWxxd" do
#         return x
#         ***
#         ''')
#     prog3 = Program('''as principal bob password "B0BPWxxd" do
#         set x = "another string"
#         return x
#         ***
#         ''')

# Test 2

    prog1 = Program('''"as principal admin password "admin" do
        local x = "2"
        return x
        ***
        ''')

        # set records = []
        # append to records with { name = "mike", date = "1-1-90" }
        # append to records with { name = "dave", date = "1-1-85" }
        # local names = records
        # foreach rec in names replacewith rec.name
        # local rec = ""
        # return names
        # ***
        # ''')
    #
    result = vault.run(prog1)
    print("output:")
    print(result)
    # result = vault.run(prog2)
    # print("output:")
    # print(result)
    # result = vault.run(prog3)
    # print("output:")
    # print(result)




