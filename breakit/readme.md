This script will compile all source code for other teams and run properly formatted 
scripts against each teams ./server. 

Note: This will only execute on linux systems, specifically targeted to run on the provided VM. 

To use this script place the other teams code in a subdirectory with the default directory 
being the 'teams' subdirectory, ie:
teams\team1\build
teams\team2\build
teams\team3\build

Break scripts are placed in a subdirectory with the default subdirectory being 'break_scripts'. 

Command Line Arguments
-p default 1024
-s break it script folder. default 'break_scripts'
-r  Rebuild all projects
-t  Path to team folders. default 'teams'

