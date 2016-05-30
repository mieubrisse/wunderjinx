# Wunderjinx
## Aim
Wunderjinx aims to create an interactive client for Wunderlist in the terminal (because jinxes are like curses... it's backed by curses...)

NOTE: This is not even close to complete right now

## Design Goals
* Curses interface
* Vim-like keybindings
* Full offline functionality

## Setup
1. Install RabbitMQ with Homebrew
2. Configure RabbitMQ to start on launch (e.g. use launchctl to load the .plist file in ~/Library/LaunchAgents)
3. Copy config.yaml.template to create config.yaml **in the same directory as config.yaml.template** (config.py looks for a config.yaml in the same directory as itself... this should be changed one day to be better)
4. Fill in the new config.yaml with your Wunderlist client ID and access token
5. Copy queue_consumer.plist.template to create queue_consumer.plist
6. Fill in the new queue_consumer.plist with the appropriate paths
7. Configure that, too, to start on launch by symlinking to ~/Library/LaunchAgents and running `launchctl load <plist file>`
8. Create a PyEnv virtualenv for Wunderjinx and install its dependencies:

    pip install wunderpy2 parsedatetime pyyaml pika flask requests

8. Modify the Alfred workflow script to point to the appropriate Python and point to the appropriate alfred_workflow.py file:

    /path/to/your/python /path/to/your/alfred_workflow.py "{query}" 2>&1
