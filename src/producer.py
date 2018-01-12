#!/usr/bin/env python3

import sys
import pika
import math
import time
from datetime import datetime

from distribution import ExponentialSeries, GaussianRandom, PoissonRandom, GeometricRandom, ExponentialRandom


DISTRIBUTIONS = {
	"gauss-rand": {
		"distribution": GaussianRandom(),
		"multiplier": 1000,
		"interval_ms": 1000
	}, 
	"poisson-rand": {
		"distribution": PoissonRandom(),
		"multiplier": 1000,
		"interval_ms": 1000
	}, 
	"geometric-rand": {
		"distribution": GeometricRandom(),
		"multiplier": 1000,
		"interval_ms": 1000
	}, 
	"exp-rand": {
		"distribution": ExponentialRandom(),
		"multiplier": 1000,
		"interval_ms": 1000
	}, 
	"exp-series": {
		"distribution": ExponentialSeries(),
		"multiplier": 1,
		"interval_ms": 1000
	}
}

EXCHANGE = "performance-analysis"

USAGE_MSG = "Usage: python producer.py distribution file1 [file2, file3, ...]\n<distribution> can take one of the following values: {}".format(DISTRIBUTIONS.keys())


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
	print("files: {}".format(files))

	res = []

	for fname in files:
		with open(fname, 'rb') as fd:
			res.append(fd.read())

	return res


def run(publisher, data, distribution, interval_ms, multiplier):
	file_idx = 0
	print("[run] file_idx={}".format(file_idx))

	content = data[file_idx]
	it_cnt = 0
	while True:
		timestamp = get_milliseconds()
		it_cnt += 1

		publish_cnt = int(abs(distribution.next()) * multiplier)
		print("it_cnt={}, publish_cnt={}".format(it_cnt, publish_cnt))

		for i in range(publish_cnt):
			publisher.publish(content)

		remaining_time = interval_ms - (get_milliseconds() - timestamp)
		sleep_time_ms = remaining_time if remaining_time > 0 else 0
		time.sleep(sleep_time_ms / 1000)


if __name__ == "__main__":

	if len(sys.argv) < 3 or \
		 sys.argv[1] not in DISTRIBUTIONS:
		print(USAGE_MSG)
		sys.exit(1)

	distribution = DISTRIBUTIONS[sys.argv[1]]
	queue = '{}.{}'.format(EXCHANGE, sys.argv[1])
	data = load_data(sys.argv[2:])
	p = Producer('localhost', 5672, 
				 			 exchange=EXCHANGE, 
				 			 queue=queue, 
				 			 routing_key=queue)

	print("[params] exchange={}, queue={}\ndistribution={}".format(EXCHANGE, queue, distribution))

	run(p, data, distribution["distribution"], distribution["interval_ms"], distribution["multiplier"])
