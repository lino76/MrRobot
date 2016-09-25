#!/usr/bin/env python3
import argparse
import os.path
#from pathlib import Path, PurePath
import socket
import json

host = ''
port = 1024
data_path = '../../../bibifitests'

def clientSend(json_data):
    conn = socket.socket()
    conn.connect((host, port))
    # print('[*] Client sending data', data)

    # Json file has mutiple parts, for now focus on the programs
    for program in json_data['programs']:
        data = program['program']
        print('[*] Client sending program\n', data)

        conn.send(data)

        data = b""
        tmp = conn.recv(1024)
        while tmp:
            data += tmp
            tmp = conn.recv(1024)
        print('[*] Client received response', data)

    conn.close()


if __name__ == '__main__':
    # Parse the command lines.  Expect a port followed by a data folder path
    cmd_parser = argparse.ArgumentParser()
    cmd_parser.add_argument('input', nargs="*")        
    args = cmd_parser.parse_args().input
    
    # Check for default parameters
    if len(args) == 2:
        port = int(args[0])    
        data_path = args[1]        
       
    print('Using port %d with data path of: %s' % (port, data_path))

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

            clientSend(json.loads(data))
        else:
            print('File does not exist: ', testfile)