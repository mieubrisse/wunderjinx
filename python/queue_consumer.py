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
import model as wj_model

class WunderlistQueueConsumer:
    ''' 
    Pulls objects from a RabbitMQ queue containing Wunderlist actions and  executes the actions using the Wunderlist API 
    '''

    def __init__(self, rabbitmq_host, wunderlist_access_token, wunderlist_client_id, queue):
        ''' Create a new QueueConsumer connected to the given queue and Wunderlist account specified by the given access token and client iD '''
        self.queue = queue
        self.rabbitmq_host = rabbitmq_host
        self.wunderclient = wunderpy2.WunderClient(wunderlist_access_token, wunderlist_client_id)

    def _handle_task(self, channel, method, properties, body):
        ''' This function gets run on every Wunderlist task to be uploaded '''
        task = json.loads(body)
        print "Task delivered:"
        print task
        sys.stdout.flush()
        task_created = False
        while not task_created:
            try:
                self.wunderclient.create_task(
                        task.get(wj_model.CreateTaskKeys.LIST_ID), 
                        task.get(wj_model.CreateTaskKeys.TITLE),
                        starred=task.get(wj_model.CreateTaskKeys.STARRED),
                        due_date=task.get(wj_model.CreateTaskKeys.DUE_DATE)
                        )
                task_created = True
            except (wunderpy2.exceptions.ConnectionError, wunderpy2.exceptions.TimeoutError) as e:
                self.connection.sleep(10)
        channel.basic_ack(delivery_tag = method.delivery_tag)
        print "Created new task:"
        print json.dumps(body)
        sys.stdout.flush()

    def consume(self):
        ''' Start continuously consuming queue actions '''
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.rabbitmq_host))
        channel = self.connection.channel()
        channel.queue_declare(queue=self.queue, durable=True)
        # We want an ack'd queue, so messages won't be deleted until they're successfully on the Wunderlist server
        # TODO basic_consume will call the callback as soon as the message is delivered, which means that you can't enforce ordering with it alone (as will be needed when this becomes a full-fledged offline client). Instead, I must write my own loop to consume messages one at a time: 
        # http://stackoverflow.com/questions/26977708/how-to-consume-rabbitmq-messages-via-pika-for-some-limited-time
        channel.basic_consume(self._handle_task, queue=self.queue)
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
    config_filepath = args[CONFIG_FILEPATH_ARGVAR]
    config = wj_config.load_config(config_filepath)
    access_token = config[wj_config.ConfigKeys.ACCESS_TOKEN]
    client_id = config[wj_config.ConfigKeys.CLIENT_ID]
    queue = config[wj_config.ConfigKeys.QUEUE]
    rabbitmq_host = config[wj_config.ConfigKeys.RABBITMQ_HOST]
    consumer = WunderlistQueueConsumer(rabbitmq_host, access_token, client_id, queue)
    consumer.consume()
