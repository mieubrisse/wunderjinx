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
3. Create a queue in RabbitMQ called "wunderjinx"
4. Copy config.yaml.template to create config.yaml **in the same directory as config.yaml.template** (config.py looks for a config.yaml in the same directory as itself... this should be changed one day to be better)
5. Fill in the new config.yaml with your Wunderlist client ID and access token
6. Copy queue_consumer.plist.template to create queue_consumer.plist
7. Fill in the new queue_consumer.plist with the appropriate paths
8. Configure that, too, to start on launch by symlinking to ~/Library/LaunchAgents and running `launchctl load <plist file>`
9. Modify the Alfred workflow to point to use the appropriate Python and point to the appropriate alfred_workflow.py file
