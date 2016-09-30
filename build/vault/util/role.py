from enum import Enum


class Role(Enum):
    write = 'write'
    read = 'read'
    append = 'append'
    delegate = 'delegate'

