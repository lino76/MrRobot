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
        if len(program.src) > 1000000:
            return self.format_result([{"status": "FAILED"}]), False

        print('running program: ', program.src)

        print('parsing program..')
        try:
            program = vault.core.Parser().parse(program)
        except Exception as e:
            print("Parsing exception: " + str(e))
            # TODO add security and vaulterror
            return self.format_result([{"status": "FAILED"}]), False

        print('executing program..')
        try:
            program_result = vault.core.Interpreter(self.datastore).execute(program)
        except vault.error.SecurityError as se:
            return self.format_result([{"status": "DENIED"}]), False
        except Exception as e:
            print("error running program:", str(e))
            return self.format_result([{"status": "FAILED"}]), False

        # TODO interpret results and determine status
        print('program complete')
        result_output = self.format_result(program_result.result)
        return result_output, program_result.exit

    def format_result(self, result_log):
        output = ""
        returning = Template('{"status": "$status", "output": $output}\n')
        operation = Template('{"status": "$status"}\n')
        for entry in result_log:
            status = entry['status']
            if status == "RETURNING":
                if isinstance(entry["output"], list) or isinstance(entry["output"], dict):
                    out = json.dumps(entry["output"], sort_keys=True)
                else:
                    out = '"' + entry["output"] + '"'
                output += returning.substitute(status=entry['status'], output=out)
            else:
                output += operation.substitute(status=entry['status'])
        return output


if __name__ == '__main__':
    from vault.core import Vault, Parser, Program, Datastore
    vault = Vault("admin")

    # prog1 = Program('''as principal admin password "admin" do
    #     set x = "Success"
    #     change password admin "password"
    #     create principal bob "B0BPWxxd"
    #     return x
    #     ***
    #     ''')

    # prog1 = Program('''as principal admin password "admin" do
    #     return "Success"
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

    # prog1 = Program('''"as principal admin password "admin" do
    #     set records = []
    #     append to records with { name = "mike", date = "1-1-90" }
    #     append to records with { name = "dave", date = "1-1-85" }
    #     local names = records
    #     foreach rec in names replacewith rec.name
    #     local rec = ""
    #     return names
    #     ***
    #     ''')
    #
    # prog2 = Program('''as principal admin password "admin" do
    #     set records = []
    #     append to records with { name = "mike", date = "1-1-90" }
    #     append to records with { name = "dave", date = "1-1-85" }
    #     append to records with { date = "1-1-85" }
    #     foreach rec in records replacewith rec.date
    #     foreach rec in records replacewith { a="hum",b=rec }
    #     set rec = ""
    #     return records
    #     ***
    #     ''')

    # test 6
    # prog1 = Program('''as principal admin password "admin" do
    #     local x = { field1="joe" }
    #     set y = []
    #     append to y with x
    #     return y
    #     ***
    #     ''')
    #
    # prog2 = Program('''as principal admin password "admin" do
    #     return y
    #     ***
    #     ''')

    # Test 3
    # prog1 = Program('''as principal admin password "admin" do
    #     set records = []
    #     append to records with { dude="yes" }
    #     append to records with "no"
    #     set var = "a variable"
    #     return var
    #     ***
    #     ''')
    # #
    # prog2 = Program('''as principal admin password "admin" do
    #     foreach y in records replacewith "boring"
    #     set var = { well="three" }
    #     set newvar = ""
    #     local var = ""
    #     return "hi"
    #     ***
    #     ''')
    # #
    # prog3 = Program('''as principal admin password "admin" do
    #     append to records with var
    #     return records
    #     ***
    #     ''')

    # Test 4
    # prog1 = Program('''as principal admin password "admin" do
    #     set x = { f="alice", g="bob" }
    #     set y = "another string"
    #     set z = { f=x.f, g=y, h=x.g, i="constant" }
    #     return z
    #     ***
    #     ''')
    #
    # prog2 = Program('''as principal admin password "admin" do
    #     set z = { f="hi", g="there" }
    #     set x = { f=z, g="hello" }
    #     return x
    #     ***
    #     ''')

    # prog1 = Program('''as principal admin password "admin" do
    #     set x = { f="hello", g="there", h="my", f="friend" }
    #     return x
    #     ***''')

    # prog1 = Program('''as principal admin password "admin" do
    #     set z = { f="hi", g="there" }
    #     return z.h
    #     ***
    #     ''')

    # Test 5
    prog1 = Program('''as principal admin password "admin" do
        set records = []
        set y = { jim="beam" }
        append to records with { name = "mike", date = "1-1-90" }
        append to records with "dave"
        append to records with records
        append to records with []
        append to records with y.jim
        set y = []
        return records
        ***
        ''')

    # prog2 = Program('''as principal admin password "admin" do
    #     set y = { jim="beam" }
    #     append to y with "hi" // should fail since y is not a table
    #     return y
    #     ***
    #     ''')

    result, exiting = vault.run(prog1)
    print("output:")
    print(result)
    # result, exiting = vault.run(prog2)
    # print("output:")
    # print(result)
    # result, exiting = vault.run(prog3)
    # print("output:")
    # print(result)





