'''
This module allows for creating new Wunderlist task requests
'''

import argparse
import pika
import wunderpy2
import json
import sys

import datetime

import model as wj_model

class WunderlistQueueProducer:
    def __init__(self, rabbitmq_host, queue):
        '''
        Params:
        rabbitmq_host -- hostname of host running RabbitMQ message queue
        queue -- name of queue to send messages to
        '''
        self.rabbitmq_host = rabbitmq_host
        self.queue = queue

    def create_task(self, title, list_id, due_date=None, starred=None, note=None):
        ''' 
        Add a new Wunderlist action to the queue 

        Params:
        title -- title of new Wunderlist task
        '''
        title = title.strip()
        if len(title) == 0:
            raise ValueError('Task title cannot be empty')
        # TODO The API being used by both the queue_producer and queue_consumer ought to be the same for validation purposes
        api = wunderpy2.WunderApi()
        if len(title) > api.MAX_TASK_TITLE_LENGTH:
            raise ValueError('Task title cannot be longer than ' + str(api.MAX_TASK_TITLE_LENGTH) + ' characters')

        # TODO I probably want to pull out the probably-heavyweight connection-opening stuff into a separate method and have the user call a 'close()'
        #  method, but for now we'll leave it
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(self.rabbitmq_host))
        except pika.exceptions.AMQPConnectionError:
            print "Error: Couldn't connect to RabbitMQ server at '{}'".format(self.rabbitmq_host)
            sys.exit(1)
        channel = connection.channel()
        channel.queue_declare(queue=self.queue, durable=True)
        channel.confirm_delivery()
        message = {
                wj_model.MessageKeys.TYPE : wj_model.MessageTypes.CREATE_TASK,
                wj_model.MessageKeys.CREATION_TIMESTAMP : datetime.datetime.now().strftime(wj_model.TIMESTAMP_FORMAT),
                wj_model.MessageKeys.BODY : {
                    wj_model.CreateTaskKeys.TITLE : title,
                    wj_model.CreateTaskKeys.DUE_DATE : due_date,
                    wj_model.CreateTaskKeys.STARRED : starred,
                    wj_model.CreateTaskKeys.LIST_ID : int(list_id),
                    wj_model.CreateTaskKeys.NOTE : note,
                    }
                }
        try:
            publish_confirmed = channel.basic_publish(exchange='', 
                    routing_key=self.queue, 
                    body=json.dumps(message), 
                    properties=pika.BasicProperties(
                        delivery_mode = 2 # Persistent messages
                    ))
            if not publish_confirmed:
                print 'Error: Publish could not be confirmed'
        except pika.exceptions.AMQPConnectionError:
            print "Error: Couldn't connect to RabbitMQ server at '{}'".format(self.rabbitmq_host)
            sys.exit(1)
        finally:
            connection.close()
