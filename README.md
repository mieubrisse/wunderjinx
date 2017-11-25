# Wunderjinx
## Aim
Wunderjinx aims to create an interactive client for Wunderlist in the terminal (because jinxes are like curses... it's backed by curses...)

NOTE: This is not even close to complete right now

## Design Goals
* Curses interface
* Vim-like keybindings
* Full offline functionality

## Setup (with pyenv-virtualenv)
1. Install pyenv: `brew install pyenv`
1. Install pyenv-virtualenv: `brew install pyenv-virtualenv`
1. Install the latest Python 2 version: `pyenv install $LATEST_PYTHON_2`
1. Create a new virtualenv for running wunderjinx: `pyenv virtualenv $LATEST_PYTHON_2 wunderjinx`
1. Activate the virtualenv: `pyenv activate wunderjinx`
1. Install Wunderjinx's dependencies: `pip install wunderpy2 parsedatetime pika`
1. Install RabbitMQ with Homebrew: `brew install rabbitmq`
1. Configure RabbitMQ to start on launch using the directions from Homebrew (use launchctl to load the .plist file in ~/Library/LaunchAgents)
1. Create a config directory somewhere on your filesystem to house Wunderjinx config
1. Copy `wunderjinx_config.py.template` to your config directory, renaming it to `wunderjinx_config.py`
1. Fill in all missing fields in your new `wunderjinx_config.py`
1. Copy `queue_consumer.plist.template` to your config directory, renaming it to `queue_consumer.plist`
1. Fill in all fields with "CHANGEME" in your new `queue_consumer.plist`
1. Configure the queue_consumer to start on launch by symlinking the `queue_consumer.plist` file into `~/Library/LaunchAgents` and running `launchctl load <plist file>`
1. Make the Bash code called in your Alfred workflow look like so, filling in the appropriate values:

    PYENV_VERSION=wunderjinx PYTHONPATH=/your/config/directory:${PYTHONPATH} ~/.pyenv/shims/python /your/path/to/alfred_workflow.py "{query}" 2>&1
