import sys
import pika
import math
import time
from datetime import datetime

from distribution import ExponentialSeries, GaussianRandom, PoissonRandom, GeometricRandom, ExponentialRandom


EPOCH = datetime.utcfromtimestamp(0)

def get_milliseconds():
  return (datetime.utcnow() - EPOCH).total_seconds() * 1000.0


class Producer:

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

		self.exchange = exchange
		self.routing_key = routing_key


	def publish(self, body, mandatory=True):

		self.channel.basic_publish(exchange=self.exchange,
                      		  routing_key=self.routing_key,
                      		  body=body,
                      		  mandatory=mandatory)


def load_data(files):
	print "files: {}".format(files)

	res = []

	for fname in files:
		with open(fname, 'rb') as fd:
			res.append(fd.read())

	return res


def run(publisher, data, distribution, interval_ms):

	content = data[0]

	it_cnt = 0
	while True:
		timestamp = get_milliseconds()
		it_cnt += 1

		# publish_cnt = int(publish_cnt * 2)
		publish_cnt = distribution.next()
		print "it_cnt={}, publish_cnt={}".format(it_cnt, publish_cnt)

		for i in range(publish_cnt):
			publisher.publish(content)

		remaining_time = interval_ms - (get_milliseconds() - timestamp)
		sleep_time_ms = remaining_time if remaining_time > 0 else 0
		time.sleep(sleep_time_ms / 1000)


if __name__ == "__main__":

	if len(sys.argv) < 2:
		print "Usage: python producer.py file1 [file2, file3, ...]"
		sys.exit(1)

	data = load_data(sys.argv[1:])

	p = Producer('localhost', 5672, 
				 			 exchange='test1', 
				 			 queue='test1.test1', 
				 			 routing_key='test1.test1')
	
	distribution = ExponentialSeries()
	interval_ms = 1000

	run(p, data, distribution, interval_ms)
