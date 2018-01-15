#!/usr/bin/env python3

import pika
import sys


USAGE_MSG = "Usage: ./consumer.py <exchange> <queue>"


class Consumer:

	def __init__(self, host, port, exchange, queue, routing_key):

		params = pika.ConnectionParameters(host=host, port=port)
		self.connection = pika.BlockingConnection(params)
		self.channel = self.connection.channel()

		self.channel.exchange_declare(exchange=exchange, 
									  exchange_type='direct', 
									  durable=True)
		self.channel.queue_declare(queue=queue, 
								   durable=True)
		self.channel.queue_bind(queue=queue, 
								exchange=exchange, 
								routing_key=routing_key)

		self.queue = queue


	def consume(self, on_message, no_ack=True):

		self.channel.basic_consume(consumer_callback=on_message,
                      		  queue=self.queue,
                      		  no_ack=no_ack)
		self.channel.start_consuming()


def on_message(channel, method, properties, body):

	delivery_tag = method.delivery_tag
	# print delivery_tag, body
	channel.basic_ack(delivery_tag=delivery_tag)


def run(consumer):

	consumer.consume(on_message, no_ack=False)


if __name__ == "__main__":

	if len(sys.argv) < 3:
		print(USAGE_MSG)
		sys.exit(1)

	exchange = sys.argv[1]
	queue = sys.argv[2]
	c = Consumer('rabbitmq-bd', 5672, 
				 exchange=exchange, 
				 queue=queue, 
				 routing_key=queue)
	
	print("[params] exchange={}, queue={}".format(exchange, queue))

	run(c)
