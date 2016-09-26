#!/usr/bin/env python3
import argparse
import os.path
#from pathlib import Path, PurePath
import socket
import json

host = ''
port = 1024
data_path = '../../../bibifitests'

def clientSend(data):
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.settimeout(30)
    conn.setblocking(True)

    conn.connect((socket.gethostname(), port))

    # print('[*] Client sending data', data)

    # Json file has mutiple parts, for now focus on the programs
    print('[*] Client sending program\n', data)

    conn.send(data.encode('utf-8'))

    result = conn.recv(1024)
    #while tmp:
    #    data += tmp
    #    tmp = conn.recv(1024)
    print('[*] Client received response:', result.decode())

    conn.close()


if __name__ == '__main__':
    # Parse the command lines.  Expect a port followed by a data folder path
    cmd_parser = argparse.ArgumentParser()
    cmd_parser.add_argument('-p', type=int, dest="port", default=1024)
    cmd_parser.add_argument('-d', type=str, dest="data_path", default=data_path, required=False)
    cmd_parser.add_argument('-m', type=str, dest="manualprogram", required=False)
    args = cmd_parser.parse_args()

    port = args.port
    data_path = args.data_path
    manualprogram = args.manualprogram

    print('Using port %d with data path of: %s' % (port, data_path))

    if manualprogram is not None:
        print("sending manual program...")
        clientSend(manualprogram)
    else:
        print('test file mode..')
        while True:
            select = input('Enter File Name or type exit:')
            print(select)
            if select == 'exit':
                exit()

            testfile = os.path.join(os.path.dirname(__file__), data_path, select)

            if os.path.isfile(testfile):
            #if Path.is_file(testfile):
                with open(testfile, "r") as jsonFile:
                    data = jsonFile.read()

                try:
                    for program in json.loads(data)['programs']:
                        clientSend(program['program'])
                except Exception as e:
                    print('network error')
                    print(e)
            else:
                print('File does not exist: ', testfile)


