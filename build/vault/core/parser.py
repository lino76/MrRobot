import re
import vault.program
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
		return re.fullmatch('[A-Za-z0-9_ ,;\.?!-]*', string) and len(string) < 65536

	def validate_identifier(self, string):
		return string not in self.reserved_words and re.fullmatch('[A-Za-z][A-Za-z0-9_ ]*', string) and len(string) < 256

	def parse_expression(self, splitted):
		if 



	def parse_command(self, line):
		line = line.split(" ")
		if line[0] == "exit":
			if len(line) != 1:
				raise VaultError(1, "Error parsing prog: exit should have no args")
			return program.Command('exit')
		if line[0] == "return":
			expressions = {'return_value': parse_expression(line[1:])}
			return program.Command('return', expressions)
		if line[0] == "create" and line[1] == "principal":
			expressions = parse_create_principal(line[2:])
			return program.Command('create_principal', expressions)
		return line[0]

	def parse_prog(self, line):
		#I'm thinking about doing this slowly and carefully, but we could just cram all the inequalities together
		line = line.split(" ")
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
		lines = program.src.split("\n")
		principal, password = self.parse_prog(lines.pop(0))
		program.principal = principal
		program.password = password
		program.commands = []
		for line in lines:
			program.commands.append(self.parse_command(line))
		return program