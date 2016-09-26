import argparse
import sys
import re

from vault.network import Server
from vault.error import CmdError
from vault.error import VaultError


def handle_app_error(error):
    exit(error.statusCode)


def handle_system_error(error):
    print("Unhandled error:", error)
    exit(1)


def exit(code=0):
    sys.exit(int(code))


def validate_args(input_args):
    # Validate the port
    try:
        port = str(input_args[0])
    except:
        raise CmdError(255, 'port not found')

    try:
        # test for leading 0
        if port[0] is not '0':
            port = int(port)
        else:
            raise CmdError(255, 'port not decimal1')
    except CmdError as e:
        raise e
    except:
        raise CmdError(255, 'port is not decimal2')

    if port < 1024 or port > 65535:
        raise CmdError(255, 'port not in range 1024-65535')

    # Validate the password
    try:
        password = str(input_args[1])
    except IndexError:
        password = 'admin'
    if not re.fullmatch('[A-Za-z0-9_ ,;\.?!-]*', password) or len(password) > 65535:
        raise CmdError(255, 'invalid password')
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
    # Fetch and validate command line args
    try:
        arg_input = handle_args()
        [port, password] = validate_args(arg_input)
    except VaultError as e:  #application errors
        handle_app_error(e)
    except Exception:  #everything else
        handle_system_error(Exception)

    # Start Server
    try:
        Server(password).start(port)
    except Exception as e: # TODO replace with application exception
        print(e)
        exit()  # TODO handle server exit

if __name__ == '__main__':
    main()
