"""
This is the Python script that we call from Aflred, which will in turn call the necessary Python modules to add the task to Wunderlist
"""

import sys
import wunderjinx

# Because we don't want to deal with quoting and escaping in Alfred, we'll pass all of the Alfred params as a single string and let the spliting happen here instead of at the Bash level
if len(sys.argv) != 2:
    sys.stderr.write("Error: No arguments passed\n")
    sys.exit(1)
args = sys.argv[1].split()
wunderjinx.main(args)
