This script will compile all source code for other teams and run properly formatted 
scripts against each teams ./server. 

Note: This will only execute on linux systems, specifically targeted to run on the provided VM. 

To use this script place the other teams code in a subdirectory with the default directory 
being the 'teams' subdirectory, ie:
teams\team1\build
teams\team2\build
teams\team3\build

To stop processing on a team folder and exclude it place a .ignore in the root of that teams folder.

Break scripts are placed in a subdirectory with the default subdirectory being 'break_scripts'. 

Command Line Arguments
-p default 1024
-s break it script folder. default 'break_scripts'
-r Rebuild all projects
-s folder to use holding teams source code. Note this must be the parent folder of a team folder.
 
######  Command Line Execution ######
-m Manual Program name. If used this is executed from the command line and exits when finished. 
-t Teams to execute test against, only used in manual mode for executing tests from the command line. 

