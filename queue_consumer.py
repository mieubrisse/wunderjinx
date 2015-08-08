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
import config as wj_config

print sys.path

CONFIG_FILEPATH_ARGVAR = "config_filepath"
script_dir = os.path.dirname(os.path.realpath(__file__))
DEFAULT_CONFIG_FILEPATH = os.path.join(script_dir, "config.yaml")

class QueueConsumer:

    def __init__(self, wunderlist_access_token, wunderlist_client_id, queue):
        ''' Create a new QueueConsumer connected to the given queue and Wunderlist account specified by the given access token and client iD '''
        self.queue = queue
        self.wunderclient = wunderpy2.WunderClient(wunderlist_access_token, wunderlist_client_id)

    def _parse_args():
        parser = argparse.ArgumentParser()
        parser.add_argument("--config", dest=CONFIG_FILEPATH_ARGVAR, metavar="<config file>", default=DEFAULT_CONFIG_FILEPATH, help="YAML file to load configuration from")
        return vars(parser.parse_args())

    def _validate_args(args):
        # TODO Validate that the config filepath is valid
        pass

    def _handle_task(self, channel, method, properties, body):
        ''' This function gets run on every Wunderlist task to be uploaded '''
        task = json.loads(body)
        task_created = False
        while not task_created:
            try:
                self.wunderclient.create_task(task[wunderpy2.Task.list_id], task[wunderpy2.Task.title])
                task_created = True
            except (wunderpy2.exceptions.ConnectionError, wunderpy2.exceptions.TimeoutError) as e:
                print "Error: Couldn't upload task to Wunderlist; sleeping for 10s before retrying"
                time.sleep(10)
        channel.basic_ack(delivery_tag = method.delivery_tag)
        print "Task uploaded!"


    def consume(self, args):
        ''' Tells the consumer to continuously consume messages from the queue '''

        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        # We want an ack'd queue, so messages won't be deleted until they're successfully on the Wunderlist server
        channel.basic_consume(self._handle_task, queue=self.queue)
        channel.start_consuming()

if __name__ == "__main__":
    args = _parse_args()
    _validate_args(args)
    config_filepath = args[CONFIG_FILEPATH_ARGVAR]
        access_token = config[wj_config.ConfigKeys.access_token]
        client_id = config[wj_config.ConfigKeys.client_id]
    consumer = QueueConsumer(
