'''Represents each of the expressions that can appear in a command'''
class Expression:

    def __init__(self, expr_type, content):
        self.expr_type = expr_type #'value', 'list' (or '[]'), 'record'
        self.content = content
        # to nest (e.g. concat) expressions and retain their metadata we'll push them into here
        self.children = []

    def __str__(self):
        return self.expr_type + ": " + str(self.content)

    def __repr__(self):
        return str(self)

    def get(self, field=None):
        if self.type == 'value':
            return self.content #maybe this is not that simple, since values can either be literals or have and identifier
        if self.type == 'list':
            return self.content[int(field)]
        if self.type == 'record':
            return self.content[str(field)]

    def set(self, value, field=None):
        if self.type == 'value':
            self.content = value
        elif self.type == 'list':
            self.content[int(field)] == value
        elif self.type == 'record':
            self.content[int(field)] == value

    def append(self, other):
        pass

    # The idea here is than given an expression and it's concat'd children
    # It could iterate and mash them all together producing the final value
    def concat_children(self):
        result = self.content
        for child in self.children:
            result.append(child.content)
        return result




#TOOD REST OF STUFF

''' DRAFT object to hold field metadata '''
class FieldType:

    def __init__(self, value, type):
        self.type = type
        self.value = value

    def __str__(self):
        return str(self.type) + " " + str(self.value)

    def __repr__(self):
        return str(self)


from enum import Enum


class Type(Enum):
    literal = 'literal'
    field = 'field'
    record = 'record'
    list = 'list'


'''Represents each of the commands executed by a program'''


class Command:

    def __init__(self, name, expressions = {}):
        self.name = name #This would be something like 'exit', 'return', 'foreach'... or NOP (?)
        self.expressions = expressions #This would be a dict of expressions {'return_value': 'x'}, {'create_principal_name': 'bob', 'create_principal_pass': 'password'}

    def __str__(self):
        s = self.name + "("
        for exp_k in self.expressions.keys():   
            s += exp_k + ": " + str(self.expressions[exp_k]) + ", "
        s = s[:-2] + ")" #remove comma and space and add parenthesis
        return s

    def __repr__(self):
        return str(self)


'''Represents the program to be executed'''


class Program:

    def __init__(self, src):
        self.status = None
        self.result = None
        self.src = src

    def get_status(self):
        return self.status

    def get_result(self):
        return self.result

    def get_src(self):
        return self.src

