from vault.data.datastore import DataStore
from vault.error.exceptions import *
import re

class Parser():
    datastore = None

    def __init__(self, program, datastore):
        print('Parser constructor')
        # Process and throw exception.
        self.datastore = datastore
        # Break into lines, one command per line
        commands = program.splitlines()
        # Starts with Principal
        print(commands)
        # Validate Principal exists and password matches Expected format as principal p password p do
        try:
            m = re.match("as principal .+ password .+ do", commands[0])
            if not m:
                raise Exception("Invalid Formated Message")

            user_id = commands[0].split()[2]
            password = commands[0].split()[4].replace('\"','')

            print(user_id, " " , password)
            self.datastore.authenticate_principal(user_id, password)
                
            for command in commands[1:]:
                print(command)
            # Validate user
        except SecurityError as e:
            raise
            
            #for match in matches:
            #    print(match)
        except Exception as e:
            print(e)
        
        print('end')
        # Process the rest of the commands

                

        

    

    
    
    
    