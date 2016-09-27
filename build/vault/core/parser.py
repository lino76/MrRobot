import re
from vault.core.program import *
from vault.error import VaultError
'''Parse the program'''


class Parser:

	def __init__(self):
		self.placeholder = None
		self.reserved_words = ["all", "append", "as", "change", "create", "default",
		 "delegate", "delegation", "delegator", "delete", "do", "exit", "foreach", 
		 "in", "local", "password", "principal", "read", "replacewith", "return", 
		 "set", "to", "write", "***"]

	def is_quoted(self, s):
		return s[0] == s[-1] and s.startswith("'")

	def dequote(self, s):
		if self.is_quoted(s):
			raise VaultError(1, "This string should have been quoted: " + s )
		return s[1:-1]
    
	#maybe move this outside or make a static func
	def validate_string_constant(self, string):
		string = self.dequote(string)
		return re.fullmatch('[A-Za-z0-9_ ,;\.?!-]*', string) and  \
		   len(string) < 65536

	def validate_identifier(self, string):
		return string not in self.reserved_words and \
		   re.fullmatch('[A-Za-z][A-Za-z0-9_]*', string) and len(string) < 256

	def validate_comment(self, string):
		return re.fullmatch('[\/][\/][A-Za-z][A-Za-z0-9_ ]*', string)

	def remove_comments(self, string):

		if string.startswith("//"):
			if not self.validate_comment(string):
				raise VaultError(1, "Comment not valid: " + string)
			else:
				return ""	
		if "//" in string:
			uncommented = string.split("//")[0]
			comment = string[len(uncommented): ]
			print("COMMENT IS: '"+ comment + "'")
			if not self.validate_comment(comment):
				raise VaultError(1, "Comment not valid: " + string)
			else:
				return uncommented
		return string
			

	def parse_value(self, string):
		#values can be either identifiers, record.field or string literals

		#test for string literal
		if '"' in string:
			if not (string.startswith('"') and string.endswith('"')):
				raise VaultError(1, "Value not valid, quotes misplaced ?" + string)
			if not self.validate_string_constant(string):
				raise VaultError(1, "String literal not matching re: " + string)
			return string #TODO CHANGE SO THIS RETURNS AN SPECIAL TYPE
		#test for record.field
		if "." in string:
			splitted = string.split(".")
			if len(splitted) != 2:
				raise VaultError(1, "Record contains wrong number of dots (.): " + string)
			if not self.validate_identifier(splitted[0]) or not self.validate_identifier(splitted[1]):
				raise VaultError(1, "One of the record fields are not valid: " + string)
			return string #TODO CHANGE SO THIS RETURNS AN SPECIAL TYPE

		#now only value posible
		if not self.validate_identifier(string):
			raise VaultError(1, "Single identifier not valid: " + string)
		return string #TODO CHANGE SO THIS RETURNS AN SPECIAL TYPE


	def parse_expression(self, splitted):
		#an expression is either a value, an empty list or a fieldval
		s = ''.join(splitted)
		#test for empty list
		if s == "[]": 
			return Expression("list", [])

		#test for record

		if s.startswith("{") and s.endswith("}"):
			try:
				content = {}
				fieldvals = s[1:-1].split(",") # remove braces and split fieldvals
				for fieldval in fieldvals:
					fieldval = fieldval.split("=")
					if len(fieldval) != 2:
						raise VaultError(1, "Fieldval had more than one equal sign: " + s)
					identifier = fieldval[0]
					value = selfparse_value(fieldval[1])
					content['id'] = value
				return Expression('record', content)
			except Exception as e:
				if type(e) is VaultError:
					raise e
				raise VaultError(1, "Malformed expression: " + s)

		#Now it can only be a value		
		value = self.parse_value(s)
		return Expression('value', value)


		
	def parse_create_principal(self, splitted):
		expressions = {}
		if len(splitted) != 2: #only 2 args expected
			raise VaultError(1, "create principal got more than 2 args: " + splitted)
		#arg 0 must be a identifier, it is the principal we want to create and it must be a valid identifier
		if not self.validate_identifier(splitted[0]):
			raise VaultError(1, "create principal got a invalid identifier: " + splitted)
		expressions['principal_to_create'] = splitted[0]

		#arg 1 must be a string, it's the password we want to set for the principal
		if not self.validate_string_constant(splitted[1]):
			raise VaultError(1, "create principal got a invalid string: " + splitted)
		expressions['password_to_set'] = self.dequote(splitted[1])
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

		#TODO
		return line[0]

	def parse_prog(self, line):
		#I'm thinking about doing this slowly and carefully, but we could just cram all the inequalities together

		line = line.strip().split(" ") #remove spaces at beginning and end, then split
		while '' in line: 
			line.remove('') #remove empty entries in list due to multiple spaces together
		if line[0] != "as" and line[1] != "principal":
			raise VaultError(1, "Error parsing prog")
		if not self.validate_identifier(line[2]):
			raise VaultError(1, "Identifier not valid")
		if line[3] != "password":
			raise VaultError(1, "Error parsing prog")
		if not self.validate_string_constant(line[4]):
			raise VaultError(1, "String not valid: " + line[4])
		if line[5] != "do":
			raise VaultError(1, "Error parsing prog")
		return (line[2], self.dequote(line[4]))


	def parse(self, program):
		lines_tmp = program.src.split("\n")
		lines = []
		for line in lines_tmp:
			line = self.remove_comments(line)
			if line != "":
				lines.append(line)

		principal, password = self.parse_prog(lines.pop(0))
		program.principal = principal
		program.password = password
		program.commands = []

		for line in lines:
			program.commands.append(self.parse_command(line))

		for command in program.commands:
			print(str(command))

		return program