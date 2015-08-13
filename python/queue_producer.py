'''
This module allows for creating new Wunderlist task requests
'''

import argparse
import pika
import wunderpy2
import json

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
        if len(title.strip()) == 0:
            raise ValueError('Task title cannot be empty')

        print 'Creating a task!'

        # TODO I probably want to pull out the probably-heavyweight connection-opening stuff into a separate method and have the user call a 'close()'
        #  method, but for now we'll leave it
        connection = pika.BlockingConnection(pika.ConnectionParameters(self.rabbitmq_host))
        channel = connection.channel()
        channel.queue_declare(queue=self.queue, durable=True)
        channel.confirm_delivery()
        wunderlist_obj = {
                wunderpy2.Task.title : title,
                wunderpy2.Task.due_date : due_date,
                wunderpy2.Task.starred : starred,
                wunderpy2.Task.list_id : int(list_id),
                }
        publish_confirmed = channel.basic_publish(exchange='', 
                routing_key=self.queue, 
                body=json.dumps(wunderlist_obj), 
                properties=pika.BasicProperties(
                    delivery_mode = 2 # Persistent messages
                ))
        if not publish_confirmed:
            print 'Error: Publish could not be confirmed'
        connection.close()
