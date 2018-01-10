import sys
import pika


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


def run(publisher, data):

	publisher.publish(data[0])


if __name__ == "__main__":

	if len(sys.argv) < 2:
		print "Usage: python producer.py file1 [file2, file3, ...]"
		sys.exit(1)

	d = load_data(sys.argv[1:])

	p = Producer('localhost', 5672, 
				 exchange='test1', 
				 queue='test1.test1', 
				 routing_key='test1.test1')
	
	run(p, d)
