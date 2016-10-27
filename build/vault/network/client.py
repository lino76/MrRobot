#!/usr/bin/env python3
import argparse
import os.path
import os
#from pathlib import Path, PurePath
import socket
import json
import subprocess
host = ''
port = 1024
bibifi_path = '../../../bibifitests'
data_path = '../../../fixBreaks'
server_path = '../../../fix/code/build'

#UNIX only
#import signal
#signal.signal(signal.SIGALRM, handler)

def handler(signum, frame):
    print ("Forever is over!")
    raise Exception("end of time")



def clientSend(data):
    #signal.alarm(10)

    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.settimeout(5)
    conn.setblocking(True)

    conn.connect((socket.gethostname(), port))


    # Json file has mutiple parts, for now focus on the programs
    print('[*] Client sending program\n', data)

    conn.send(data.encode('utf-8'))


    result = ''
    try:
        while True:
            tmp = conn.recv(8)
            if tmp == b'':
                break
            result += tmp.decode()
    except Exception as e:
        print(e)
    print('[*] Client received response:', result)
    conn.close()
    return result

def compareResponses( server_response, expected_response):
    err_base = "Command "  + "| Responses don't match: "
    if len(server_response) != len(expected_response):
        print(err_base + "different line numbers")
        print('expected:', expected_response)
        print('received:', server_response)
        return False
    if server_response != expected_response:
        print('expected:', expected_response)
        print('received:', server_response)
        return False
    # for i in range(0, len(server_response)):
    #     if expected_response[i]['status'] != server_response[i]['status']:
    #         print(err_base + "statuses")
    #         print("Line " + str(i) + ". Got: "+ server_response[i]['status'] +
    #             " expected " + expected_response[i]['status'])
    #         return False
    #     if expected_response[i].status == "RETURNING":
    #         if expected_response[i].output != server_response[i].output:
    #             print(err_base + "output doesn't match")
    #             print("Got " + str(server_response[i]['output']) + " expected " +
    #                 str(expected_response[i]['output']))
    #             return False
    print("Responses match")
    return True


def sendFromFile(testfile):

    if os.path.isfile(testfile):
            #if Path.is_file(testfile):
        with open(testfile, "r") as jsonFile:
            data = jsonFile.read()

            try:
                #NOTE : here u can specify what exact part of test u want to run
                #just append [-1:] - will run last testcase from file
                programms = json.loads(data)['programs']
                for program in programms:
                    response = clientSend(program['program'])
                    response = response.split('\n')[:-1]
                    response_json = [json.loads(res) for res in response]
                    if 'output' not in program.keys():
                        print('No output key for this test')
                        return
                    if not compareResponses(response_json, program['output']):
                        print('NOT MATCH')
                        return
                    else:
                        continue
                return "MATCHED"
            except Exception as e:
                print('expect')
                print(e)
                return
    else:
        print('File does not exist: ', testfile)


if __name__ == '__main__':
    # Parse the command lines.  Expect a port followed by a data folder path
    cmd_parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    cmd_parser.add_argument('-p', type=int, dest="port", default=1024)
    cmd_parser.add_argument('-s', type=str, dest="server_path", default=server_path, required=False)
    cmd_parser.add_argument('-m', type=str, dest="manualprogram", required=False)
    cmd_parser.add_argument('-r', type=bool, dest="run_all", required=False)
    cmd_parser.add_argument('-b', type=bool, dest="bibifi", required=False)
    #cmd_parser.add_argument('-a', dest='run_all', action='store_true')
    args = cmd_parser.parse_args()

    port = args.port
    server_path = args.server_path
    manualprogram = args.manualprogram

    if manualprogram:
        manualprogram = manualprogram.replace("\\n", "\n")
    run_all = args.run_all
    bibifi = args.bibifi
    print('Using port %d with data path of: %s' % (port, data_path))
    if bibifi:
        server = os.path.join(os.path.dirname(__file__), server_path, 'main.py')
        root,_,files = list(os.walk(os.path.join(os.path.dirname(__file__), bibifi_path)))[0]
        all_tests = [x for x in files if all([x.lower().endswith(".json"), not any( y in x.lower() for y in ['perf', 'let', 'filter', 'timeout', 'func'])])]
        print('print running all tests', all_tests)
        matched, failed = [], []
        for select in all_tests:
            print(select)
            test_file = os.path.join(root, select)
            proc = subprocess.Popen(['c:\Python3\python', server, str(port)])
            #TODO: UNIX STYLE
            result = sendFromFile(test_file)
            if 'MATCHED' == result:
                matched.append(select.split('/')[-1])
            else:
                failed.append(select.split('/')[-1])
            proc.terminate()
            proc.wait(10)
        print('ALL Failed tests', failed)
        print('ALL matched tests', matched)
        exit()
    if run_all:
        server = os.path.join(os.path.dirname(__file__), server_path, 'main.py')
        all_tests = [x[0] for x in os.walk(os.path.join(os.path.dirname(__file__), data_path))]

        print('print running all tests')
        matched, failed = [], []
        for select in all_tests[1:]:
            print(select)
            test_file = os.path.join( select, 'full_test')
            test_file += ".json"
            argv = [str(port)]
            #TODO: WINDOWS STYLE
            with open(test_file, "r") as jsonFile:
                data = jsonFile.read()
                argv_file = json.loads(data)['arguments']['argv'][1:]
                argv.extend(argv_file)
            #TODO: WINDOWS STYLE
            proc = subprocess.Popen(['c:\Python3\python', server, *argv])
            #TODO: UNIX STYLE
            result = sendFromFile(test_file)
            if 'MATCHED' == result:
                matched.append(select.split('/')[-1])
            else:
                failed.append(select.split('/')[-1])
            proc.terminate()
            proc.wait(10)
        print('ALL Failed tests', failed)
        print('ALL matched tests', matched)

    if manualprogram is not None:
        print("sending manual program...")
        print("program: ", manualprogram)
        clientSend(manualprogram)
    else:
        print('test file mode..')
        while True:
            select = input('Enter File Name or type exit:')
            if select == 'exit':
                exit()
            print(select)
            test_file = os.path.join(os.path.dirname(__file__), data_path, select, 'full_test')
            if not test_file.endswith(".json"):
                test_file += ".json"
            sendFromFile(test_file)



