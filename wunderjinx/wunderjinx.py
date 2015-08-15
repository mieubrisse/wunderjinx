'''
Script to handle all actions the user might want to take with Wunderjinx
'''
import argparse
import datetime
import os
import sys

import list_resolver as wj_resolver
import queue_producer
import config as wj_config

CONFIG_FILEPATH_ARGVAR = 'config_filepath'

ADD_TASK_STARRED_ARGVAR = 'add_task_starred'
ADD_TASK_DUE_DATE_ARGVAR = 'add_task_due_date'
ADD_TASK_TITLE_ARGVAR = 'add_task_title'
ADD_TASK_NOTE_ARGVAR = 'add_task_note'
ADD_TASK_LIST_ARGVAR = 'add_task_list'

today = datetime.datetime.now().date()
tomorrow = today + datetime.timedelta(days=1)
today_str = today.strftime('%Y-%m-%d')
tomorrow_str = tomorrow.strftime('%Y-%m-%d')

script_dir = os.path.dirname(os.path.realpath(__file__))
default_config_filepath = os.path.join(script_dir, "config.yaml")

def _parse_args():
    ''' Parses command line arguments with argparse '''
    parser = argparse.ArgumentParser()

    # TODO This is disabled for now until I get a better way to do config files that lets me set the filepaths
    # parser.add_argument('--config', dest=CONFIG_FILEPATH_ARGVAR, default=default_config_filepath, metavar="<config file>", help="YAML config file to use")

    parser.add_argument('-s', '--starred', action='store_true', dest=ADD_TASK_STARRED_ARGVAR, default=None, help="whether the task is starred or not")
    parser.add_argument('-d', '--due-date', metavar='<due date>', dest=ADD_TASK_DUE_DATE_ARGVAR, help="set task's due date")
    parser.add_argument('-t', '--today', action='store_const', const=today_str, dest=ADD_TASK_DUE_DATE_ARGVAR, help="set the task's due date to today")
    parser.add_argument('-m', '--tomorrow', action='store_const', const=tomorrow_str, dest=ADD_TASK_DUE_DATE_ARGVAR, help="set the task's due date to today")
    parser.add_argument('-l', '--list', dest=ADD_TASK_LIST_ARGVAR, metavar='<list>', default=['inbox'], nargs='+', help='task note')
    parser.add_argument('-n', '--note', nargs='+', dest=ADD_TASK_NOTE_ARGVAR, metavar='note', help='task note')
    parser.add_argument(ADD_TASK_TITLE_ARGVAR, nargs='+', metavar='title', help='task title')
    return vars(parser.parse_args())

def _validate_args(args):
    ''' 
    Validates argparse-parsed command-line arguments 
    
    Returns:
    Exit code if one ought to be sent, or None if everything is fine
    '''
    title = ' '.join(args[ADD_TASK_TITLE_ARGVAR])
    dest_list = ' '.join(args[ADD_TASK_LIST_ARGVAR])
    if len(title.strip()) == 0:
        # TODO This should really be a logger
        print 'Error: Title cannot be empty'
        return 1
    if len(dest_list.strip()) == 0:
        # TODO This should really be a logger
        print 'Error: Destination list cannot be empty'
        return 1

def main(argv=sys.argv):
    ''' 
    Main driver for script, and entry point for pip package

    Return:
    Zero if all was successful, non-zero integer otherwise
    '''
    args = _parse_args()
    error_code = _validate_args(args)
    if error_code:
        return error_code

    # TODO Reimplement customizable config filepath
    # config_filepath = args[CONFIG_FILEPATH_ARGVAR]
    rabbitmq_host = wj_config.RABBITMQ_HOST
    queue = wj_config.QUEUE
    access_token = wj_config.ACCESS_TOKEN
    client_id = wj_config.CLIENT_ID

    producer = queue_producer.WunderlistQueueProducer(rabbitmq_host, queue)

    title = ' '.join(args[ADD_TASK_TITLE_ARGVAR])
    note_fragments = args[ADD_TASK_NOTE_ARGVAR]
    note = ' '.join(args[ADD_TASK_NOTE_ARGVAR]) if note_fragments else None
    starred = args[ADD_TASK_STARRED_ARGVAR]
    due_date = args[ADD_TASK_DUE_DATE_ARGVAR]
    list_name = args[ADD_TASK_LIST_ARGVAR]

    list_resolver = wj_resolver.WunderlistListResolver(access_token, client_id)
    list_id = list_resolver.resolve(list_name)

    producer.create_task(title, list_id, due_date=due_date, starred=starred, note=note)

    return 0

if __name__ == "__main__":
    sys.exit(main())
