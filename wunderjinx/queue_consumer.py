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
from dateutil import parser as date_parser

import config as wj_config
import model as wj_model

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
        list_id = body.get(wj_model.CreateTaskKeys.LIST_ID)
        title = body.get(wj_model.CreateTaskKeys.TITLE)
        starred = body.get(wj_model.CreateTaskKeys.STARRED)
        due_date = body.get(wj_model.CreateTaskKeys.DUE_DATE)
        note = body.get(wj_model.CreateTaskKeys.NOTE)

        new_task = self.wunderclient.create_task(list_id, title, starred=starred, due_date=due_date)
        # TODO If the connection is cut right here, we'll end up with duplicate tasks. It's a slim possibility, but there should be a better way of handling adding notes.
        if note:
            new_task_id = new_task[wunderpy2.model.Task.id]
            self.wunderclient.create_note(new_task_id, note)

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
            except (wunderpy2.exceptions.ConnectionError, wunderpy2.exceptions.TimeoutError) as e:
                self.connection.sleep(10)
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
    while True:
        try:
            consumer.consume()
        except (pika.exceptions.AMQPConnectionError, pika.exceptions.ConnectionClosed):
            print "Could not connect to RabbitMQ server at '{}'; trying again in 10 seconds".format(rabbitmq_host)
            time.sleep(10)
