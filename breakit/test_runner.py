#!/usr/bin/env python3
import argparse
import os.path
import socket
import json
import subprocess
import time
import sys

data_path = 'break_scripts'
teams_root = 'teams'
port = 1024

class TeamFolders:    
    teams_root = 'teams' #Path to source code of all teams.    
    __teams = [] # folders of the teams is also used as the team id.
    __rebuild = False
    __rebuilt = False
    __current = 0

    def __init__(self, force_rebuild, teams_folder = None):
        if teams_folder != None:
            self.__team_path = teams_folder
        
        self.teams_root = os.path.join(os.path.dirname(__file__), self.teams_root)
        
        #check if a build has been executed already
        if force_rebuild or not os.path.isfile(os.path.join(self.teams_root, '.built')):
            self.__rebuild = True
        
        #for folder in os.listdir(self.__team_path):
        for team in os.listdir(self.teams_root):
            team_folder = os.path.join(self.teams_root, team)
            # if Folder contains .ignore skip the folder.
            if not os.path.isdir(team_folder):
                continue

            try:
                if not os.path.isfile(os.path.join(team_folder, '.ignore')):
                    # store the teamid and path to folder in dictionary.
                    self.__teams.append(team)
                    if self.__rebuild:
                        print('Building team #: ', team)
                        self.__build(team, True)
            except Exception as e:
                print(e)
        
        if self.__rebuild:
            self.__rebuilt = True # Flag to avoid double rebuilding the first time.
            file = os.path.join(self.teams_root, '.built')
            with open(file, 'w') as f: pass 

    def __iter__(self):
        return iter(self.__teams)            

    def build_all(self):
        if self.__rebuilt:
            return
        for folder in self.__folders:
            __build(team, True)

    def __build(self, team, force = False):
        build_folder = (os.path.join(self.teams_root, team, 'build'))
        if force or not os.path.isfile(os.path.join(build_folder, 'server')):
            try:
                ret = subprocess.Popen(['make'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=build_folder)                
                ret.wait()               
                if ret.returncode == 2: # return code 2 is an error, print the standard out.
                    print(ret.stdout.readlines())                    
                    print(ret.returncode)
            except Exception as e:
                print('Exception raised building {} : '.format(team), e)

class Server:
    host = ''
    port = 1024

    def __init__(self, build_folder):
        self.server = os.path.join(build_folder, 'build', 'server')       
        if not os.path.isfile(self.server):            
            raise Exception('Server not found')

    def start_server(self, port):
        self.port = port
        self.proc = subprocess.Popen([self.server, str(self.port)])
        time.sleep(2)

        self.proc.poll()
	    # Port already busy, try next port
        if self.proc.returncode == 63:
            return self.start_server( port + 1)
        return self.port

    def stop_server(self):
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

def send(teams, team_list, program):
    for team in teams:
        # only execute the tests on the specified teams.
        if team_list[0] == 'all' or team in team_list:
            try:
                server = Server(os.path.join(teams.teams_root, team))
                server.start_server(port)
                
                client = Client()
            except Exception as e:
                print(e)
            finally:
                if server is not None:
                    server.stop_server()

if __name__ == '__main__':
    print(sys.version)
    # Parse the command lines.  Expect a port followed by a data folder path
    cmd_parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    cmd_parser.add_argument('-p', type=int, dest="port", default=1024)        
    cmd_parser.add_argument('-s', '--source', type=str, dest='team_path', required=False, help='Path to folder containing the folders of each teams code.' )
    cmd_parser.add_argument('-d', type=str, dest="data_path", default=data_path, required=False)        
    cmd_parser.add_argument('-r', '--rebuild', action='store_true', help='Force all known team projects to rebuild.' )
    # These options are to run a test from the command line, -t is ignored without a -m but is optional, if not include all teams are run
    # Note these are not implemented yet.
    cmd_parser.add_argument('-m', type=str, dest="manualprogram", required=False)
    cmd_parser.add_argument('-t', '--teams', type=str, help='List of teams separated by commas', required=False)

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
    teams = TeamFolders(args.rebuild, team_path)
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
        test_file = None
        while True:
            print('available teams:\n', str.join(', ', teams))
            #t_input = input(' \n## Press Enter to run last team(s) / program selection ##\n or type exit:')
            t_input = input('Enter team or teams (separated by comma), enter for all or type "r" to repeat: ')
            
            if t_input == '':
                t_input = 'all'
            if t_input != 'r' or test_file is None:
                # Return will shortcut rerun last selected test / teams
                team_list = t_input.split(',')
                test_file = input('Enter File Name or type exit:')                

            if test_file == 'exit':
                exit()
            #print(select)
            
            test_file = os.path.join(os.path.dirname(__file__), data_path, test_file)
            if not test_file.endswith(".json"):
                test_file += ".json"
            send(teams, team_list, test_file)




