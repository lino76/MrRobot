import argparse
import sys

from vault.network import server


class CmdError(Exception):
    def __init__(self, statusCode):
        self.statusCode


def handle_error(status):
    sys.exit(status)


def exit():
    sys.exit(0)


def validate_args(input):
    print('args: ', input)
    # port = input[0]
    # password = input[1]
    #
    # TODO check number of args, min/max values of port, length of string (default to admin)
    # TODO raise CmdException with the right status for each
    port = 1024
    password = "admin"
    return [port, password]


def handle_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', nargs="*")

    try:
        args = parser.parse_args()
    except SystemExit:
        raise CmdError(255)

    return args.input


# main app entry
def main():
    print("Welcome to the vault.")  # should probably remove this...
    try:
        input = handle_args()
        [port, password] = validate_args(input)
    except CmdError:  # TODO probably need more checking
        # exit path
        handle_error(CmdError)

    try:
        server.start(port, password)
    except Exception: # TODO replace with application exception
        print(Exception)
        exit()  # TODO handle server exit


if __name__ == '__main__':
    main()
