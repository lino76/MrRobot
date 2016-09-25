import argparse
import sys

from vault.network import server
from vault.error import CmdError
from vault.error import VaultError


def handle_app_error(error):
    exit(error.statusCode)


def handle_system_error(error):
    print("Unhandled error:", error)
    exit(1)


def exit(code=0):
    sys.exit(int(code))


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
    except VaultError as e:  #application errors
        # exit path
        handle_app_error(e)
    except Exception:   #everything else
        handle_system_error(Exception)

    try:
        server.start(port, password)
    except Exception: # TODO replace with application exception
        print(Exception)
        exit()  # TODO handle server exit


if __name__ == '__main__':
    main()
