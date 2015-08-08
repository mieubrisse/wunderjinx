'''
This module allows for creating new Wunderlist task requests
'''

import pika
import wunderpy2
import json

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='wunderlist_tasks', durable=True)

wunderlist_obj = {
        wunderpy2.Task.title : "Test RabbitMQ task",
        wunderpy2.Task.list_id : 103574383,
        }
channel.confirm_delivery()
publish_confirmed = channel.basic_publish(exchange='', 
        routing_key='wunderlist_tasks', 
        body=json.dumps(wunderlist_obj), 
        properties=pika.BasicProperties(
            delivery_mode = 2 # Persistent messages
        ))
if not publish_confirmed:
    print "Error: Publish could not be confirmed"
connection.close()
