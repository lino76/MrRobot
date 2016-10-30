import re
from vault.core.program import *
from vault.error import VaultError

'''Parse the program'''


class Parser:
    def __init__(self):
        self.placeholder = None
        self.reserved_words = ["all", "append", "as", "change", "concat", "create", "default",
                               "delegate", "delegation", "delegator", "delete", "do", "exit", "equal",
                               "filtereach", "foreach", "in", "let", "local", "notequal", "password", "principal",
                               "read", "replacewith", "return", "set", "split", "to", "tolower",  "with", "write",
                               "***"]

    def is_quoted(self, s):
        return s[0] == s[-1] and s.startswith("'")

    def dequote(self, s):
        if self.is_quoted(s):
            raise VaultError(1, "This string should have been quoted: " + s)
        return s[1:-1]

    def validate_terminator(self, lines):
        for indx, line in enumerate(lines):
            l = line.strip()
            try:
                l.index('***')
                return lines[:indx]
            except:
                pass
        raise Exception(101, "invalid program, missing terminator")

    def validate_line_content(self, lines):
        for line in lines:
            if line == "":
                raise Exception(101, "invalid program, empty lines are invalid")
        return lines

    # maybe move this outside or make a static func
    def validate_string_constant(self, string):
        string = self.dequote(string)
        return re.fullmatch('[A-Za-z0-9_ ,;\.?!-]*', string) and \
               len(string) < 65536

    def validate_identifier(self, string):
        return string not in self.reserved_words and \
               re.fullmatch('[A-Za-z][A-Za-z0-9_]*', string) and len(string) < 256

    def validate_comment(self, string):
        return re.fullmatch('[\/][\/][[A-Za-z0-9_,;\.?!\s-]*', string)

    def validate_right(self, string):
        return string == "read" or string == "write" or string == "append" or string == "delegate"

    def validate_tgt(self, string):
        return string == "all" or self.validate_identifier(string)

    def remove_comments(self, string):
        string = string.lstrip()
        line_comment = False
        if string.startswith("//"):
            if not self.validate_comment(string):
                raise VaultError(1, "Comment not valid: " + string)
            else:
                line_comment = True
                return "", line_comment
        if "//" in string:
            uncommented = string.split("//")[0]
            comment = string[len(uncommented):]
            if not self.validate_comment(comment):
                raise VaultError(1, "Comment not valid: " + string)
            else:
                return uncommented, line_comment
        return string, line_comment

    def parse_value(self, string):
        # values can be either identifiers, record.field or string literals

        # test for string literal
        string = string.strip()

        if '"' in string:
            if not (string.startswith('"') and string.endswith('"')):
                raise VaultError(1, "Value not valid, quotes misplaced ?" + string)
            if not self.validate_string_constant(string):
                raise VaultError(1, "String literal not matching re: " + string)
            return FieldType(self.dequote(string), Type.literal)  # TODO CHANGE SO THIS RETURNS AN SPECIAL TYPE
        # test for record.field
        if "." in string:
            splitted = string.split(".")
            if len(splitted) != 2:
                raise VaultError(1, "Record contains wrong number of dots (.): " + string)
            if not self.validate_identifier(splitted[0]) or not self.validate_identifier(splitted[1]):
                raise VaultError(1, "One of the record fields are not valid: " + string)
            return FieldType(string, Type.record)  # TODO CHANGE SO THIS RETURNS AN SPECIAL TYPE

        # now only value posible
        if not self.validate_identifier(string):
            raise VaultError(1, "Single identifier not valid: " + string)
        return FieldType(string, Type.field)  # TODO CHANGE SO THIS RETURNS AN SPECIAL TYPE

    def parse_expression(self, splitted):
        # an expression is either a value, an empty list or a fieldval
        s = ''.join(splitted)
        # test for empty list
        if s == "[]":
            return Expression(Type.list, [])

        # test for record

        if s.startswith("{") and s.endswith("}"):
            try:
                content = {}
                identifiers = []
                fieldvals = s[1:-1].split(",")  # remove braces and split fieldvals
                for fieldval in fieldvals:
                    fieldval = fieldval.split("=")

                    if len(fieldval) != 2:
                        raise VaultError(1, "Fieldval had more than one equal sign: " + s)
                    fieldval[0] = fieldval[0].strip()
                    fieldval[1] = fieldval[1].strip()
                    if not self.validate_identifier(fieldval[0]):
                        raise VaultError(1, "Fieldval identifier not valid: '" + fieldval[0] + "'")
                    identifier = fieldval[0]
                    if identifier not in identifiers:
                        identifiers.append(identifier)
                    else:
                        raise VaultError(1, "Fieldval duplicate identifier: '" + fieldval[0] + "'")
                    value = self.parse_value(fieldval[1])
                    content[identifier] = value
                return Expression(Type.record, content)
            except Exception as e:
                if type(e) is VaultError:
                    raise e
                raise VaultError(1, "Malformed expression: " + s + "got exception: " + str(e))

        # test for string literal
        elif s.startswith('"') and s != splitted:
            s = ' '.join(splitted)

        # Now it can only be a value
        value = self.parse_value(s)
        return Expression(Type.value, value)

    def parse_create_principal(self, splitted):
        expressions = {}
        # arg 0 must be a identifier, it is the principal we want to create and it must be a valid identifier
        if not self.validate_identifier(splitted[0]):
            raise VaultError(1, "create principal got an invalid identifier: " + str(splitted))
        expressions['principal'] = splitted[0]

        # arg 1 must be a string, it's the password we want to set for the principal
        constant = " ".join(splitted[1:])

        if not self.validate_string_constant(constant):
            raise VaultError(1, "create principal got an invalid string: " + str(splitted))
        expressions['password'] = self.dequote(constant)
        return expressions

    def parse_change_password(self, splitted):
        expressions = {}
        try:
            expressions = self.parse_create_principal(splitted)
        except VaultError as e:
            raise VaultError(1, str(e).replace("create principal", "change password"), 1)
        return expressions

    def parse_set(self, splitted):
        expressions = {}
        # we could have "x=y", "x= y", "x = y" or "x =y" and then some crap
        line = " ".join(splitted)
        if not "=" in line[:len(splitted[0]) + 2]:
            raise VaultError(1, "Equal sign not found at the beginning of set: " + line)
        line = line.replace("=", " ", 1)  # replace only the first occurence
        splitted = line.split(" ")
        while '' in splitted:
            splitted.remove('')  # remove empty entries in list due to consecutive spaces

        if not self.validate_identifier(splitted[0]):
            raise VaultError(1, "set got an invalid identifier: " + str(splitted))

        expressions['key'] = splitted[0]
        # this is just a test. given this expression:
        # { f="hello", g="there", h="my", f="friend" }
        # in a dict: f="hello" will get overwritten by f="friend
        # this should return an error
        tmp = "".join(splitted)

        expressions['value'] = self.parse_expression(" ".join(splitted[1:]))
        return expressions

    def parse_append_to(self, splitted):
        expressions = {}

        if not self.validate_identifier(splitted[0]):
            raise VaultError(1, "append to got an invalid identifier: " + str(splitted))
        expressions['key'] = splitted[0]

        if splitted[1] != "with":
            raise VaultError(1, "append to missing the with word: " + str(splitted))

        expressions['value'] = self.parse_expression(" ".join(splitted[2:]))

        return expressions

    def parse_local(self, splitted):
        expressions = {}
        try:
            expressions = self.parse_set(splitted)
        except VaultError as e:
            raise VaultError(1, str(e).replace("set", "set local"), 1)
        return expressions

    def parse_foreach(self, splitted):
        expressions = {}

        if not self.validate_identifier(splitted[0]):
            raise VaultError(1, "foreach first arg not valid  identifier: " + str(splitted))
        expressions['item'] = splitted[0]

        if splitted[1] != "in":
            raise VaultError(1, "foreach missing the in word: " + str(splitted))

        if not self.validate_identifier(splitted[2]):
            raise VaultError(1, "foreach second arg not valid  identifier: " + str(splitted))
        expressions['list'] = splitted[2]

        if splitted[3] != "replacewith":
            raise VaultError(1, "foreach missing the replacewith word: " + str(splitted))

        expressions['replacer'] = self.parse_expression(" ".join(splitted[4:]))
        return expressions

    def parse_set_delegation(self, splitted):
        expressions = {}
        # first remove -> can it be - > ?
        line = " ".join(splitted)
        if not "->" in line:
            raise VaultError(1, "set delegation missing ->: " + line)
        line = line.replace("->", "", 1)
        splitted = line.split(" ")
        while '' in splitted:
            splitted.remove('')  # remove empty entries in list due to consecutive spaces

        if not self.validate_tgt(splitted[0]):
            raise VaultError(1, "set delegation first arg not a valid tgt: " + str(splitted))
        expressions['variable'] = splitted[0]

        if not self.validate_identifier(splitted[1]):
            raise VaultError(1, "set delegation second arg not a valid identifier: " + str(splitted))
        expressions['source_principal'] = splitted[1]

        if not self.validate_right(splitted[2]):
            raise VaultError(1, "set delegation right not valid: " + str(splitted))
        expressions['right'] = splitted[2]

        if not self.validate_identifier(splitted[3]):
            raise VaultError(1, "set delegation third arg not a valid identifier: " + str(splitted))
        expressions['target_principal'] = splitted[3]

        return expressions

    def parse_delete_delegation(self, splitted):
        expressions = {}
        try:
            expressions = self.parse_set_delegation(splitted)
        except VaultError as e:
            raise VaultError(1, str(e).replace("set", "delete", 1))
        return expressions

    def parse_default_delegator(self, splitted):
        expressions = {}
        # this one is easy, we either have "=p" or "= p"
        line = "".join(splitted)
        if line[0] != "=":
            raise VaultError(1, "default delegator missing =: " + str(splitted))
        line = line[1:]
        if not self.validate_identifier(line):
            raise VaultError(1, "default delegator identifier not valid: " + line)
        expressions['delegator'] = line
        return expressions

    def parse_command(self, line):
        line = line.strip().split(" ")
        while '' in line:
            line.remove('')
        if line[0] == "exit":
            if len(line) != 1:
                raise VaultError(1, "Error parsing prog: exit should have no args")
            return Command('exit')

        if line[0] == "return":
            expressions = {'return_value': self.parse_expression(line[1:])}
            return Command('return', expressions)

        if line[0] == "create" and line[1] == "principal":
            expressions = self.parse_create_principal(line[2:])
            return Command('create_principal', expressions)
        if line[0] == "change" and line[1] == "password":
            expressions = self.parse_change_password(line[2:])
            return Command('change_password', expressions)
        if line[0] == "set" and line[1] != "delegation":
            expressions = self.parse_set(line[1:])
            return Command('set', expressions)
        if line[0] == "append" and line[1] == "to":
            expressions = self.parse_append_to(line[2:])
            return Command('append_to', expressions)
        if line[0] == "local":
            expressions = self.parse_local(line[1:])
            return Command('local', expressions)
        if line[0] == "foreach":
            expressions = self.parse_foreach(line[1:])
            return Command('foreach', expressions)
        if line[0] == "set" and line[1] == "delegation":
            expressions = self.parse_set_delegation(line[2:])
            return Command('set_delegation', expressions)
        if line[0] == "delete" and line[1] == "delegation":
            expressions = self.parse_delete_delegation(line[2:])
            return Command('delete_delegation', expressions)
        if line[0] == "default" and line[1] == "delegator":
            expressions = self.parse_default_delegator(line[2:])
            return Command('default_delegator', expressions)
        raise VaultError(1, "parse command not a valid program: " + line)

    def parse_prog(self, line):
        # I'm thinking about doing this slowly and carefully, but we could just cram all the inequalities together

        line = line.strip().split(" ")  # remove spaces at beginning and end, then split
        while '' in line:
            line.remove('')  # remove empty entries in list due to multiple spaces together

        if line[0] != "as" and line[1] != "principal":
            raise VaultError(1, "Error parsing prog, first line missing as or principal")
        if not self.validate_identifier(line[2]):
            raise VaultError(1, "Identifier not valid, principal identifier")

        if line[3] != "password":
            raise VaultError(1, "Error parsing prog, missing password")
        if not self.validate_string_constant(line[4]): #oh shit
            raise VaultError(1, "String not valid: " + line[4])


        if line[5] != "do":
            raise VaultError(1, "Error parsing prog, missing do")

        return (line[2], self.dequote(line[4]))

    def parse(self, program):
        '''
            NOTE: when running this program via the client->server:

                as principal admin password "admin" do\nreturn "success"\n***\n

            at some point up to here the source goes from:

                as principal admin password admin do\nreturn success\n***\n

            to this:

                as principal admin password admin do\\nreturn success\\n***\\n
        '''

        lines_tmp = program.src.split("\n")
        lines = []
        for line in lines_tmp:
            line, line_comment = self.remove_comments(line)
            if not line_comment:
                lines.append(line)
        # validate the terminator and remove it (or fail)
        lines = self.validate_terminator(lines)
        lines = self.validate_line_content(lines)
        principal, password = self.parse_prog(lines.pop(0))

        program.principal = principal
        program.password = password
        program.commands = []

        for line in lines:
            program.commands.append(self.parse_command(line))

        # for command in program.commands:
        #     print(str(command))

        return program
