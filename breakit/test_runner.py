#!/usr/bin/env python3
import argparse
import os.path
import socket
import json
import subprocess
import time

data_path = 'break_scripts'
teams_root = 'teams'
port = 1024

class TeamFolders:    
    __team_path = 'teams' #Path to source code of all teams.    
    __folders = []
    __rebuild = False
    __rebuilt = False
    __current = 0

    def __init__(self, force_rebuild, teams_folder = None, target_teams = None):
        if teams_folder != None:
            self.__team_path = teams_folder
        
        self.__root = os.path.join(os.path.dirname(__file__), self.__team_path)
        
        #check if a build has been executed already
        if force_rebuild or not os.path.isfile(os.path.join(self.__root, '.built')):
            self.__rebuild = True
        
        #for folder in os.listdir(self.__team_path):
        for folder in os.listdir(self.__root):
            target_team = os.path.join(self.__root, folder)
            # if Folder contains .ignore skip the folder.
            if not os.path.isdir(target_team):
                continue

            try:
                if not os.path.isfile(os.path.join(target_team, '.ignore')):
                    self.__folders.append(target_team)
                    if self.__rebuild:
                        print('Building team #: ', folder)
                        self.__build(target_team, True)
            except Exception as e:
                print(e)
        
        if self.__rebuild:
            self.__rebuilt = True # Flag to avoid double rebuilding the first time.
            file = os.path.join(self.__root, '.built')
            with open(file, 'w') as f: pass 

    def __iter__(self):
        return iter(self.__folders)            

    def build_all(self):
        if self.__rebuilt:
            return
        for folder in self.__folders:
            __build(folder, True)

    def __build(self, folder, force = False):
        if force or not os.path.isfile(os.path.join(self.__root, folder, 'build', 'server')):
            try:
                make = os.path.join(self.__root, folder, 'build')
                ret = subprocess.Popen(['make'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=make)                
                ret.wait()               
                if ret.returncode == 2:
                    print(ret.stdout.readlines())
                    
                    print(ret.returncode)
            except Exception as e:
                print('Exception raised building {} : '.format(folder), e)

class Server:
    host = ''
    port = 1024

    def __init__(self, build_folder):

        self.server = os.path.join(build_folder, 'build', 'server')       
        if not os.path.isfile(self.server):            
            raise

    def runServer(self, port):
        self.port = port
        self.proc = subprocess.Popen( [self.server, str(self.port)])
        time.sleep(2)

        self.proc.poll()
	    # Port already busy, try next port
        if self.proc.returncode == 63:
            return self.runServer( port + 1)
        return self.port

    def stopServer(self):
        self.proc.terminate()
        self.proc.wait()
        print( "server exited with return code: " + str(self.proc.returncode))


class Client:
    host = ''
    port = 1024

    def clientSend(self, data):
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.settimeout(30)
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

    def compareResponses(self, server_response, expected_response):
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
        # for i in range(0, len(server_response)):77
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


    def sendFromFile(self, testfile):

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
                        if not compareResponses(response_json, program['output']):
                            print('NOT MATCH')
                            return
                except Exception as e:
                    print('expect')
                    print(e)
                    raise
        else:
            print('File does not exist: ', testfile)


def send(teams, program):
    for team in teams:
        try:
            server = Server(team)
            dicare = server.runServer(port)
            
            client = Client()
        except Exception as e:
            print(e)

if __name__ == '__main__':
    # Parse the command lines.  Expect a port followed by a data folder path
    cmd_parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    cmd_parser.add_argument('-p', type=int, dest="port", default=1024)
    cmd_parser.add_argument('-d', type=str, dest="data_path", default=data_path, required=False)
    cmd_parser.add_argument('-m', type=str, dest="manualprogram", required=False)
    cmd_parser.add_argument('-t', '--teams', type=str, help='List of teams separated by commas', required=False)
    cmd_parser.add_argument('-r', '--rebuild', action='store_true', help='Force all known team projects to rebuild.' )
    cmd_parser.add_argument('-s', '--source', type=str, dest='team_path', required=False, help='Path to folder containing the folders of each teams code.' )


    args = cmd_parser.parse_args()

    port = args.port
    data_path = args.data_path
    manualprogram = args.manualprogram
    team_path = args.team_path        

    if args.teams:
        target_teams = args.teams.split(',')
    else:
        target_teams = None
    
    # Get all the team folders and compile if required.    
    # TODO: Implement target teams to limit the execution to a few teams.
    teams = TeamFolders(args.rebuild, team_path, target_teams)
    if args.rebuild:
        teams.build_all()


    # If a manual program then execute a single script   
#    if manualprogram:
        
#        manualprogram = manualprogram.replace("\\n", "\n")
    #run_all = args.run_all
    print('Using port %d with data path of: %s' % (port, data_path))

    if manualprogram is not None:
        print("sending manual program...")
        print("program: ", manualprogram)
#        clientSend(manualprogram)
    else:
        print('test file mode..')
        while True:
            select = input('Enter File Name or type exit:')
            if select == 'exit':
                exit()
            print(select)
            test_file = os.path.join(os.path.dirname(__file__), data_path, select)
            if not test_file.endswith(".json"):
                test_file += ".json"
            send(teams, test_file)




