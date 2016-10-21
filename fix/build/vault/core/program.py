'''Represents each of the expressions that can appear in a command'''
from copy import deepcopy

class Expression:

    def __init__(self, type, content):
        self.type = type #'value', 'list' (or '[]'), 'record'
        self.content = content
        # to nest (e.g. concat) expressions and retain their metadata we'll push them into here
        self.children = []

    def __str__(self):
        return self.type.name + ": " + str(self.content)

    def __repr__(self):
        return str(self)

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result

    def get_type(self):
        return

    def get(self, field=None):
        if self.type is Type.value:
            return self.content #maybe this is not that simple, since values can either be literals or have and identifier
        if self.type is Type.list:
            return self.content
        if self.type is Type.record:
            return self.content

    def get_value(self):
        if self.type is Type.value:
            return self.content  # maybe this is not that simple, since values can either be literals or have and identifier
        if self.type is Type.list:
            return self.content
        if self.type is Type.record:
            return self.content

    def set(self, value, field=None):
        if self.type is Type.value:
            self.content = value
        elif self.type is Type.list:
            self.content[int(field)] == value
        elif self.type is Type.record:
            self.content[int(field)] == value

    def is_appended(self):
        return len(self.children) > 0

    # The idea here is than given an expression and it's concat'd children
    # It could iterate and mash them all together producing the final value
    def concat_children_values(self):
        result = self.content
        for child in self.children:
            child_val = None
            if child.type is Type.record:
                val = {}
                for key in child.content.keys():
                    val[key] = child.content[key].value
                child_val = val
            elif child.type is Type.value:
                if child.content.type is Type.literal:
                    child_val = child.content
            else:
                child_val = child.content
            result.append(child_val)
        return result

    def concat_children(self):
        result = self.content
        for child in self.children:
            if isinstance(child, Expression):
                result.append(child.content)
            else:
                result.append(child)
        return result

    # extract all values from this whole content graph
    def value(self):
        content = deepcopy(self.content)
        # Dict
        if isinstance(content, dict):
            return self.depopulate_dict(content)
        # List
        elif isinstance(content, list):
            return self.depopulate_list(content)
        # FieldType
        elif isinstance(content, FieldType):
            return self.depopulate_field(content)
        # Expression
        elif isinstance(content, Expression):
            return self.depopulate_expression(content)
        # String
        elif isinstance(content, str):
            return content
        else:
            pass

    def depopulate_expression(self, obj):
        return obj.value()

    def depopulate_field(self, obj):
        # TODO this is a mess
        if isinstance(obj, str):
            return obj
        elif isinstance(obj, dict):
            return self.depopulate_dict(obj.value)
        elif isinstance(obj.value, dict):
            return self.depopulate_dict(obj.value)
        elif isinstance(obj.value, Expression):
            return self.depopulate_expression(obj.value)
        elif isinstance(obj, Expression):
            if isinstance(obj.content, dict):
                return self.depopulate_dict(obj.content)
        elif obj.type is Type.literal:
            return obj.value
        elif obj.type is Type.list:
            return obj.value
        elif obj.type is Type.value:
            return obj.value
        elif obj.type is Type.field:
            if isinstance(obj.value, Expression):
                return self.depopulate_expression(obj.value)
            else:
                return self.depopulate_field(obj.value)
        elif obj.type is Type.record:
            if isinstance(obj, dict):
                return self.depopulate_dict(obj)
            else:
                return obj.value

    def depopulate_list(self, obj):
        val = []
        for item in obj:
            if isinstance(item, Expression):
                val.append(self.depopulate_expression(item.value))
            elif isinstance(item, FieldType):
                val.append(self.depopulate_field(item.value))
            elif isinstance(item, dict):
                val.append(self.depopulate_dict(item))
            elif isinstance(item, str):
                val.append(item)
            elif isinstance(item, list):
                # skip empty lists
                lst = self.depopulate_list(item)
                if lst:
                    val.append(lst)
        return val


    def depopulate_dict(self, obj):
        val = {}
        # For every value in the dict, extract the values from that too
        for k, v in obj.items():
            if isinstance(v, Expression):
                val[k] = self.depopulate_expression(v)
            elif isinstance(v, FieldType):
                val[k] = self.depopulate_field(v.value)
            elif isinstance(v, dict):
                val[k] = self.depopulate_dict(v)
            elif isinstance(v, str):
                val[k] = v
        return val

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

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result


from enum import Enum


class Type(Enum):
    literal = 'literal'
    field = 'field'
    record = 'record'
    list = 'list'
    value = 'value'


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
        self.exit = False

    def get_status(self):
        return self.status

    def get_result(self):
        return self.result

    def get_src(self):
        return self.src

