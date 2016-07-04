'''
Script to handle all actions the user might want to take with Wunderjinx
'''
import argparse
import datetime
import os
import sys
from parsedatetime import Calendar

import queue_producer as wj_queue_producer

# TODO We could speed things up if we had a server running that would feed the config so this doesn't have to read it every time, perhaps?
import config as wj_config

CONFIG_FILEPATH_ARGVAR = 'config_filepath'

ADD_TASK_STARRED_ARGVAR = 'add_task_starred'
ADD_TASK_DUE_DATE_ARGVAR = 'add_task_due_date'
ADD_TASK_TITLE_ARGVAR = 'add_task_title'
ADD_TASK_NOTE_ARGVAR = 'add_task_note'
ADD_TASK_LIST_ARGVAR = 'add_task_list'

# TODO Should this go in a config file? Or maybe it should be pulled from wunderpy2, since that's the final destination
DATE_FORMAT = '%Y-%m-%d'

def _parse_args(args):
    ''' Parses command line arguments with argparse '''
    parser = argparse.ArgumentParser()

    # TODO This is disabled for now until I get a better way to do config files that lets me set the filepaths
    # parser.add_argument('--config', dest=CONFIG_FILEPATH_ARGVAR, default=default_config_filepath, metavar="<config file>", help="YAML config file to use")

    parser.add_argument('-s', '--starred', action='store_true', dest=ADD_TASK_STARRED_ARGVAR, default=None, help="whether the task is starred or not")
    parser.add_argument('-d', '--due-date', metavar='<due date>', dest=ADD_TASK_DUE_DATE_ARGVAR, nargs='+', help="set task's due date")
    parser.add_argument('-t', '--today', action='store_const', const=["today"], dest=ADD_TASK_DUE_DATE_ARGVAR, help="set the task's due date to today")
    parser.add_argument('-m', '--tomorrow', action='store_const', const=["tomorrow"], dest=ADD_TASK_DUE_DATE_ARGVAR, help="set the task's due date to today")
    parser.add_argument('-l', '--list', dest=ADD_TASK_LIST_ARGVAR, metavar='<list>', nargs='+', help='task note')
    parser.add_argument('-n', '--note', nargs='+', dest=ADD_TASK_NOTE_ARGVAR, metavar='note', help='task note')
    parser.add_argument(ADD_TASK_TITLE_ARGVAR, nargs='+', metavar='title', help='task title')
    return vars(parser.parse_args(args))

def _validate_args(args):
    ''' 
    Validates argparse-parsed command-line arguments 
    
    Returns:
    Exit code if one ought to be sent, or None if everything is fine
    '''
    title = ' '.join(args[ADD_TASK_TITLE_ARGVAR])
    if len(title.strip()) == 0:
        # TODO This should really be a logger
        print 'Error: Title cannot be empty'
        return 1

def _parse_date(date_str):
    ''' 
    Uses parsedatetime to do smart parsing for due dates 

    
    Returns:
    String formatted    
    '''
    result = Calendar().parse(date_str)
    # See https://bear.im/code/parsedatetime/docs/index.html
    parse_type = result[1]
    if parse_type == 0 or parse_type == 2:
        # The parse failed to get a date
        return None
    parsed_date = result[0]
    try:
        year = parsed_date.tm_year
        month = parsed_date.tm_mon
        day = parsed_date.tm_mday
    # Unsure why some inputs (e.g. "next year", "oct 28") get parsed as time.tm_struct and some get parsed as tuples
    except AttributeError:
        year = parsed_date[0]
        month = parsed_date[1]
        day = parsed_date[2]
    return datetime.date(year, month, day)

def main(input_args):
    ''' 
    Main driver for script, and entry point for pip package

    Return:
    Zero if all was successful, non-zero integer otherwise
    '''
    args = _parse_args(input_args)
    error_code = _validate_args(args)
    if error_code:
        return error_code

    # TODO Reimplement customizable config filepath
    # config_filepath = args[CONFIG_FILEPATH_ARGVAR]
    rabbitmq_host = wj_config.RABBITMQ_HOST
    queue = wj_config.QUEUE
    access_token = wj_config.ACCESS_TOKEN
    client_id = wj_config.CLIENT_ID

    producer = wj_queue_producer.WunderlistQueueProducer(rabbitmq_host, queue)

    title = ' '.join(args[ADD_TASK_TITLE_ARGVAR])
    note_fragments = args[ADD_TASK_NOTE_ARGVAR]
    note = ' '.join(note_fragments) if note_fragments else None
    starred = args[ADD_TASK_STARRED_ARGVAR]
    due_date_fragments = args[ADD_TASK_DUE_DATE_ARGVAR]
    input_due_date = ' '.join(due_date_fragments) if due_date_fragments else None
    due_date_iso_str = None
    if input_due_date:
        parsed_due_date = _parse_date(input_due_date)
        if not parsed_due_date:
            sys.stderr.write("Error: Unable to extract date from due date: {}\n".format(due_date))
            sys.exit(1)

        # Automatically starring tasks due today, because I want it
        # TODO Automatically star any tasks due this week (how do we define week, though?)
        if parsed_due_date == datetime.date.today():
            starred = True

        due_date_iso_str = parsed_due_date.strftime(DATE_FORMAT)

    # TODO Perform trial list name resolution so we can flag an error to the user
    list_name_fragments = args[ADD_TASK_LIST_ARGVAR]
    list_name = ' '.join(list_name_fragments) if list_name_fragments else None

    producer.create_task(title, list_name=list_name, due_date=due_date_iso_str, starred=starred, note=note)

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
