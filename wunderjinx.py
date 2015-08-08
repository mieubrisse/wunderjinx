'''
Script to handle all actions the user might want to take with Wunderjinx
'''

import argparse

ADD_CMD_TITLE_ARGVAR="new_task_title"
ADD_CMD_LIST_ARGVAR="new_task_title"

def _parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help="subcommand help")

    # parser for adding new task
    add_cmd_parser = subparsers.add_parser('add', help="TODO add help goes here")
    add_cmd_parser.add_argument(ADD_CMD_TITLE_ARGVAR, help="title of new task to add")
    add_cmd_parser.add_argument("-l", "--list", ADD_CMD_LIST_ARGVAR, help="list to add new task to")

    parser.parse_args()


def _validate_args(args):
    pass

def _do_stuff(args):
    print "Did stuff"
    pass

if __name__ == "__main__":
    args = _parse_args()
    _validate_args(args)
    _do_stuff(args)
