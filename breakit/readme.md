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

To execute a test from the oracle follow these steps:
4) run the program and input the filename testfile.html
6) The file is converted to testfile.json and run against the selected teams.

The latest versions now include a 'gb' feature to generate break files in the break folder.

1) submit an oracle query: https://builditbreakit.org/participation/837/oraclesubmissions (or use existing)
2) open the result page, ie: https://builditbreakit.org/participation/837/oraclesubmission/5047
3) right click and save the page as a webpage html in the break_scripts folder ie break_scripts/testfile.html
4) run test_runner.
a) select team(s), ie 100
b) select foo.html (This gets autoconverted to foo.json, html is deleted and test is run)
c) if (only only if) teams come back with bugs select those teams you feel are bugs
d) type 'gb' at file prompt
e) folder MrRobot/break/100_foo/test.json is created using the program run
f) Open new folder, fill in description.txt
g) Open the test.json file and populate the type: ie security or correctness
h) commit and push the files to git, sit back and wait for the points to roll in.


