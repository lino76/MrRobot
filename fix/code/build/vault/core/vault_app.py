'''Central point by which programs get executed'''
import simplejson as json
from string import Template

import vault
import vault.error


class Vault:

    def __init__(self, password):
        self.password = password
        self.datastore = vault.core.Datastore(password)

    def run(self, program):
        if len(program.src) > 1000000:
            return self.format_result([{"status": "FAILED"}]), False

        try:
            program = vault.core.Parser().parse(program)
        except Exception as e:
            return self.format_result([{"status": "FAILED"}]), False

        try:
            program_result = vault.core.Interpreter(self.datastore).execute(program)
        except vault.error.SecurityError as se:
            return self.format_result([{"status": "DENIED"}]), False
        except Exception as e:
            return self.format_result([{"status": "FAILED"}]), False

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

    prog1 = Program('''"
        ''')

    result, exiting = vault.run(prog1)
    print("output:")
    print(result)





