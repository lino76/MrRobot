This script will compile all source code for other teams and run properly formatted 
scripts against each teams ./server. 

Note: This will only execute on linux systems, specifically targeted to run on the provided VM. 

NOTE2: oracle support requires BeautifulSoup4 support.  pip3 install bs4

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
-s folder to use holding teams source code. Note this must be the parent folder of a team folder.
-r Rebuild all projects 

Input file is expected in the Oracle provided format, ie:
{
    "arguments: {
        "argv": [ "port", "password" ]
    },
    "programs": [],
    "return_code": 255,
    "output": [
        { "status" : "SET" },
        {
            "status": "Returning",
            "output": "my string"
        }
    ]
}

