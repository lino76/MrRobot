This script will compile all source code for other teams and run properly formatted scripts against each teams ./server.  

To use this script place the other teams code in a subdirectory with the default directory being the teams directory, ie:
teams\team1\build
teams\team2\build
teams\team3\build

Do not check the team source into this github repository.
Break scripts are placed in a subdirectory with the default named break_scripts. 

Command Line Arguments
-p default 1024
-s break it script folder. default 'break_scripts'
-r  Rebuild all projects
-t  Path to team folders. default 'teams'

