#!/usr/bin/env python3
import os
import argparse
import os.path
import socket
import json
import subprocess
import time
import sys
import stat
from bs4 import BeautifulSoup

GS = '\033[32m'
RS = '\033[31m'
SRS = '\033[41m'
END = '\033[0m'
data_path = 'break_scripts'
teams_root = 'teams'
html_path = data_path
port = 22222

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
        self.__log_file = os.path.join(self.teams_root, "build.log")
        

        #check if a build has been executed already
        if force_rebuild or not os.path.isfile(os.path.join(self.teams_root, '.built')):
            self.__rebuild = True
            self.__remove(self.__log_file)
        
        #for folder in os.listdir(self.__team_path):
        for team in os.listdir(self.teams_root):
            team_folder = os.path.join(self.teams_root, team)
            
            if not os.path.isdir(team_folder):
                continue

            # if Folder contains .ignore skip the folder.
            try:
                if not os.path.isfile(os.path.join(team_folder, '.ignore')) or not os.path.isfile(os.path.join(self.teams_root, '.buildfail')):
                    if self.__rebuild:
                        print('Building team #: ', team)
                        self.__build(team, True)
                    # store the teamid and path to folder in dictionary.
                    self.__teams.append(team)                        
            except Exception as e:
                print(e)
        
        if self.__rebuild:
            self.__rebuilt = True # Flag to avoid double rebuilding the first time.
            file = os.path.join(self.teams_root, '.built')
            self.__create_file(file)

    def __iter__(self):
        return iter(self.__teams)            

    def build_all(self):
        if self.__rebuilt:
            return
        for folder in self.__folders:
            try:
                __build(team, True)
            except exception as e:
                print(e)

    def __build(self, team, force = False):
        
        build_folder = os.path.join(self.teams_root, team, 'build')
        server = os.path.join(build_folder, 'server')
        bf = os.path.join(self.teams_root, team, '.buildfail')        
        if force or not os.path.isfile(server):            
            try:                
                if team == '1007':
                    try:
                        os.chmod(os.path.join(build_folder, "../bin/nex"), 0o777)    
                    except: pass
                for r,d,files in os.walk(self.teams_root):
                    os.chmod(r, 0o777)
                try:
                    os.chmod(server, 0o777)
                except: pass
                # Clean up the build before we start. If it failed previous remove the .buildfail file           
                self.__remove(bf)
                ret = subprocess.Popen(['make'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=build_folder)                
                ret.wait(45) #wait up to 45 seconds for build to complete   
                if ret.returncode == 2: # return code 2 is an error, print the standard out.                    
                    print(ret.stdout.readlines())                    
                    print(ret.returncode)
                    raise Exception('Build Error returned 2')
                os.chmod(server, 0o777)
                self.__log(team + " - Built")            
            except Exception as e:
                self.__create_file(bf)
                self.__log(team + " - BUILD ERROR: " + str(e))
                print('Exception raised building {} : '.format(team), e)
                raise

    def __log(self, message):       
        self.__create_file(self.__log_file, message) 

    def __create_file(self, file, message = None):       
        if message:
            permissions = 'a'
        else:
            permissions = 'w'

        try:
            with open(file, permissions) as f:
                if message:
                    f.write(message + "\n")         
        except Exception as e:
            pass

    def __remove(self, file):
        try:    
            os.remove(file)
        except: 
            pass

class Server:
    host = ''
    port = 22222
    proc = None

    def __init__(self, build_folder):
        self.server = os.path.join(build_folder, 'build', 'server')       
        if not os.path.isfile(self.server):            
            raise Exception('Server not found')

    def start_server(self, port, password = None):        
        self.port = port
        print('using port: ', self.port)
        if password:            
            self.proc = subprocess.Popen([self.server, str(self.port), password], stdout=False, stderr=False)
        else:    
            self.proc = subprocess.Popen([self.server, str(self.port)], stdout=False, stderr=False)
        time.sleep(2)

        self.proc.poll()
	    # Port already busy, try next port
        if self.proc.returncode == 63:
            return self.start_server( port + 1)
        if self.proc.returncode is not None:
            print('proc code should be None, but received: ', self.proc.returncode)
            #raise Exception(self.proc.returncode)
        return self.port

    def stop_server(self):
        self.proc.terminate()
        self.proc.wait()
        print( "server exited with return code: " + str(self.proc.returncode))


class Client:
    host = ''
    port = 22222
    def __init__(self, port):
        self.port = port

    def clientSend(self, program):

        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.conn.settimeout(30)
        self.conn.setblocking(True)
        self.conn.connect((self.host, self.port))

        #print('[*] Client sending program\n', program)
        try:
            self.conn.send(program.encode('utf-8'))

            result = ''
            try:
                while True:
                    tmp = self.conn.recv(8)
                    if tmp == b'':
                        break
                    result += tmp.decode()
            except Exception as e:
                print(e)
            #print('[*] Client received response:', result)
        finally:
            try:
                self.conn.close()
            except:
                pass

        return result

class Log:
    def __init__(self, file):
        self.file = file
        try:
            os.remove(file)
        except: pass

    def log(self, message):
        try:
            with open(self.file, 'a') as f:
                f.write(message + "\n")         
        except Exception as e:
            pass        

def send(teams, team_list, script_name, break_data):
    log = os.path.splitext(script_name)[0] + '.log'
    logger = Log(log)
    # program is a json file in the oracle format. 
    #Parse the program and pull out the command line arguements
    args = break_data['arguments']['argv']

    if args[0] == '%PORT%':
        test_port = port
    else:
        test_port = args[0]

    password = None
    if len(args) == 2:
        password = args[1]

    print('\33[44m################### SCRIPT ' + script_name + ' ###################' + END)
    for team in teams:
        # only execute the tests on the specified teams.
        if team_list[0] == 'all' or team in team_list:
            print(GS + '****** Executing Team {} ******'.format(team) + END)
            logger.log('****** Executing Team {} ******'.format(team))
            try:
                server = Server(os.path.join(teams.teams_root, team))
                used_port = server.start_server(test_port, password)
                
                client = Client(used_port)

                for program in break_data.get('programs', []):                    
                    response = client.clientSend(program.get('program'))                    
                    compare_responses(response, program.get('output'))
                print(GS + "TEST PASS" + END)
                logger.log("TEST PASS")
            except Exception as e:
                # test for a returncode here
                
                if str(break_data.get('return_code', 0)) == str(e):
                    print(GS + "TEST PASS" + END)
                    logger.log("TEST PASS")
                else:
                    print(SRS + "TEST FAIL: " + str(e) + END)
                    logger.log("TEST FAIL")
            finally:
                try:                
                    server.stop_server()
                except: pass

def compare_responses(server_response, expected_response):  
    s_response = server_response.rstrip('\n').replace('\n', ',').strip("'")      
    s_response = '{{"output":[{}]}}'.format(s_response)
    s_response = json.loads(s_response)

    if s_response.get('output') != expected_response:
        print('EXPECTING: ')
        print(expected_response)
        print('RECEIVED: ')
        print(s_response.get('output'))
        raise Exception("TEST FAIL")
   #print('TEST PASS')

def generate_from_html(html_file):
    json_name = os.path.splitext(html_file)[0] + '.json'
    html_file = os.path.join(os.path.dirname(__file__), html_path, test_file)
    json_file = os.path.splitext(os.path.join(os.path.dirname(__file__), data_path, test_file))[0] + '.json'
    # check both files exist or throw
    if not os.path.isfile(html_file):
        raise Exception("HTML File does not exist: " + html_file)
    
    if os.path.isfile(json_file):
        raise Exception("Output file already exists: " + json_file)

    try:
        with open(html_file) as f:
            html = f.read()
        soup = BeautifulSoup(html, 'html.parser')
        input = soup.find('samp', {'class': 'form-control-static'}).string
        output = soup.find('pre', {'class': 'form-control-static'}).string     
        
        i_json = json.loads(output)    
        o_json = json.loads(input)

        # Update the input to include the output for each program.        
        for idx,prog in enumerate(o_json.get('programs')):
            new = '{{"output":{}, "program":"{}" }}'.format(json.dumps(i_json.get('output')[idx]), prog.replace('\n', '\\n').replace('\"', '\\\"'))
            t = json.loads(new)
            o_json['programs'][idx] = t


        # Append the return_code
        o_json['return_code'] = i_json.get('return_code')
        
        # Fix the arguments
        arg = json.loads('{{ "argv":{}}}'.format(o_json.get('arguments')).replace("\'", '\"'))
        o_json['arguments'] = arg 

        with open(json_file, 'w') as f:
            json.dump(o_json, f)
        
        #Once tested remove this.
        os.remove(html_file)

        return json_name

    except Exception as e:
        print(e)

if __name__ == '__main__':
    print(sys.version)
    # Parse the command lines.  Expect a port followed by a data folder path
    cmd_parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    cmd_parser.add_argument('-p', type=int, dest="port", required=False)        
    cmd_parser.add_argument('-s', '--source', type=str, dest='team_path', required=False, help='Path to folder containing the folders of each teams code.' )
    cmd_parser.add_argument('-d', type=str, dest="data_path", default=data_path, required=False)        
    cmd_parser.add_argument('-r', '--rebuild', action='store_true', help='Force all known team projects to rebuild.', required=False)
    cmd_parser.add_argument('-a', '--html', dest="html_path", default=html_path,  required=False)
    args = cmd_parser.parse_args()

    if args.port:
        port = args.port
    data_path = args.data_path
    team_path = args.team_path            
    
    # Get all the team folders and compile if required.    
    teams = TeamFolders(args.rebuild, team_path)
    # Force a recompile if flag is passed
    if args.rebuild:
        teams.build_all()

    test_file = None
    while True:
        print('available teams:\n', str.join(', ', teams))
        
        t_input = input('Enter team or teams (separated by comma), enter for all or type "r" to repeat: ')
            
        if t_input == '':
            t_input = 'all'
        
        if t_input == 'exit' or test_file == 'e':
            exit()

        if t_input == 'r' and test_file is None:
            print('Rerun is not available until a successful run')
            continue

        if t_input != 'r':
            # Return will shortcut rerun last selected test / teams and skip asking for inputs
            team_list = t_input.split(',')
            test_file = input('Enter File Name, type "r" to repeat or type "exit":')                
            
            if test_file == 'exit' or test_file == 'e':
                exit()

            try:  
                if test_file != 'r' or not (test_file == 'r' and not file_data): 
                    # Load an oracle created query, a file with the same name with .json gets created in the data_path and executed
                    if test_file.endswith(".html"):
                        test_file = generate_from_html(test_file)

                    test_file = os.path.join(os.path.dirname(__file__), data_path, test_file)

                    if not test_file.endswith(".json"):
                        test_file += ".json"
    
                    with open(test_file, "r") as f:
                        file_data = json.loads(f.read())
            except Exception as e:
                print(e)                
                continue

        send(teams, team_list, test_file, file_data)




