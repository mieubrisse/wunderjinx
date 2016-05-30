'''
This module defines a RabbitMQ consumer that listens for requests to create new
 Wunderlist tasks and then uploads them to Wunderlist when internet connection is
 available
'''

import pika
import wunderpy2
import sys
import json
import time
import argparse
import os.path
import requests

import config as wj_config
import model as wj_model
import list_resolver as wj_list_resolver

_FALLBACK_LIST_NAME = "Inbox" # Name of list to use if none of the user-defined lists works

HTTP_SUCCESS_STATUS_CODE = 200

class ListResolverConnectionError(Exception):
    pass

def _resolve_list_name(list_name):
    """
    Queries the list resolving service to get the ID for the given list

    Return:
    ID of list, or None if no ID was found
    """
    url = "http://{hostname}:{port}{endpoint}?{name_param}={list_name}".format(
            hostname=wj_config.RESOLVER_HOST, 
            port=wj_config.RESOLVER_PORT, 
            endpoint=wj_list_resolver.LIST_LOOKUP_ENDPOINT, 
            name_param=wj_list_resolver.LIST_LOOKUP_NAME_URL_PARAM, 
            list_name=list_name)

    try:
        response = requests.get(url, timeout=3)
    except requests.exceptions.RequestException as e:
        raise ListResolverConnectionError()

    if response.status_code != HTTP_SUCCESS_STATUS_CODE:
        return None
    return int(response.text)

def get_task_list_id(suggested_list_name):
    """
    Resolves the given list name to an ID, or returns the user-defined default list if that doesn't work, or returns
    Inbox ID if all that fails

    Return:
    The first match of: the ID for the given list, the ID for the user-defined default list, the ID for the fallback list, None
    """
    if suggested_list_name is not None and len(suggested_list_name.strip()) > 0:
        user_list_id = _resolve_list_name(suggested_list_name)
        if user_list_id is not None:
            return user_list_id
        print("Warning: Could not resolve list name '" + suggested_list_name + "' to an ID")
    if wj_config.DEFAULT_LIST_NAME is not None and len(wj_config.DEFAULT_LIST_NAME.strip()) > 0:
        default_list_id = _resolve_list_name(wj_config.DEFAULT_LIST_NAME)
        if default_list_id is not None:
            return default_list_id
    fallback_list_id = _resolve_list_name(_FALLBACK_LIST_NAME)
    if fallback_list_id is not None:
        return fallback_list_id
    return None

class WunderlistQueueConsumer:
    ''' 
    Pulls objects from a RabbitMQ queue containing Wunderlist actions and  executes the actions using the Wunderlist API 
    '''

    def __init__(self, rabbitmq_host, wunderlist_access_token, wunderlist_client_id, queue):
        ''' Create a new QueueConsumer connected to the given queue and Wunderlist account specified by the given access token and client iD '''
        self.queue = queue
        self.rabbitmq_host = rabbitmq_host
        self.wunderclient = wunderpy2.WunderApi().get_client(wunderlist_access_token, wunderlist_client_id)

    def _handle_create_task(self, body):
        ''' Helper method to do the gruntwork for creating a task '''
        # TODO Print thing
        list_name = body.get(wj_model.CreateTaskKeys.LIST_NAME)
        title = body.get(wj_model.CreateTaskKeys.TITLE)
        starred = body.get(wj_model.CreateTaskKeys.STARRED)
        due_date = body.get(wj_model.CreateTaskKeys.DUE_DATE)
        note = body.get(wj_model.CreateTaskKeys.NOTE)

        # TODO It may be that we'll need to do a list name resolve at both task production and task consumption
        #  time, in case the resolving doesn't work at consumption (and so we can show the user resolution errors
        #  at task production time)
        list_id = get_task_list_id(list_name)
        if list_id is None:
            raise ValueError("Could not resolve list with name '" + list_name + "' for task:" + json.dumps(body))

        new_task = self.wunderclient.create_task(list_id, title, starred=starred, due_date=due_date)
        # print "Created task: {}".format(str(new_task))
        # TODO If the connection is cut right here, we'll end up with duplicate tasks. It's a slim possibility, but there should be a better way of handling adding notes.
        if note:
            new_task_id = new_task[wunderpy2.model.Task.ID]
            # TODO Put in debugger logger level
            # print "Creating new note '{}' on task with ID: {}".format(note, new_task_id)
            new_note = self.wunderclient.create_note(new_task_id, note)

            # TODO Put in debug logs
            # print "Created note: {}".format(str(new_note))

    def _handle_message(self, channel, method, properties, body):
        ''' This function gets run on every Wunderlist task to be uploaded '''
        message = json.loads(body)
        # TODO Put this in a logger
        print "Handling message:"
        print message

        message_type = message[wj_model.MessageKeys.TYPE]
        message_timestamp = message[wj_model.MessageKeys.CREATION_TIMESTAMP]
        message_body = message[wj_model.MessageKeys.BODY]

        message_handled = False
        while not message_handled:
            try:
                if message_type == wj_model.MessageTypes.CREATE_TASK:
                    self._handle_create_task(message_body)
                    message_handled = True
                else:
                    print "Error: Unknown message type: {}".format(message_type)
            except (ListResolverConnectionError, wunderpy2.exceptions.ConnectionError, wunderpy2.exceptions.TimeoutError) as e:
                # TODO Put this in debug logger
                # print "Error: Unable to submit message to Wunderlist; trying again in 10 seconds: {}".format(str(e))
                # TODO Make this not a magic number
                self.connection.sleep(10)
            # TODO We need to have a better error than ValueError for failed responses
            except ValueError as e:
                raise ValueError("Error: Encountered error in handling message that needs human intervention: " + str(e))
        channel.basic_ack(delivery_tag = method.delivery_tag)

        # TODO Make this a logger
        print "Created new task:"
        print json.dumps(body)

    def consume(self):
        ''' Start continuously consuming queue actions '''
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.rabbitmq_host))
        channel = self.connection.channel()
        channel.queue_declare(queue=self.queue, durable=True)
        # We want an ack'd queue, so messages won't be deleted until they're successfully on the Wunderlist server
        # TODO basic_consume will call the callback as soon as the message is delivered, which means that you can't enforce ordering with it alone (as will be needed when this becomes a full-fledged offline client). Instead, I must write my own loop to consume messages one at a time: 
        # http://stackoverflow.com/questions/26977708/how-to-consume-rabbitmq-messages-via-pika-for-some-limited-time
        channel.basic_consume(self._handle_message, queue=self.queue)
        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            self.connection.close()


# ---------- Runtime things ------------------
CONFIG_FILEPATH_ARGVAR = "config_filepath"
script_dir = os.path.dirname(os.path.realpath(__file__))
default_config_filepath = os.path.join(script_dir, "config.yaml")

def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", dest=CONFIG_FILEPATH_ARGVAR, metavar="<config file>", default=default_config_filepath, help="YAML file to load configuration from")
    return vars(parser.parse_args())

def _validate_args(args):
    # TODO Validate that the config filepath is valid
    pass

if __name__ == "__main__":
    args = _parse_args()
    _validate_args(args)

    access_token = wj_config.ACCESS_TOKEN
    client_id = wj_config.CLIENT_ID
    queue = wj_config.QUEUE
    rabbitmq_host = wj_config.RABBITMQ_HOST
    consumer = WunderlistQueueConsumer(rabbitmq_host, access_token, client_id, queue)
    try:
        print "Queue consumer started (make sure your list-resolving service is up!)"
        consumer.consume()
    except (pika.exceptions.AMQPConnectionError, pika.exceptions.ConnectionClosed):
        sys.stderr.write("Error: Unable to open connection to RabbitMQ server at '{}'\n".format(rabbitmq_host))
