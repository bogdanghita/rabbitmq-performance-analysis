#!/usr/bin/env python3

import sys
import json
import docker
import signal
import time
from datetime import datetime
import threading
import requests


EPOCH = datetime.utcfromtimestamp(0)

def _get_milliseconds():
  return (datetime.utcnow() - EPOCH).total_seconds() * 1000.0


DOCKER_BASE_URL = "unix://var/run/docker.sock"
DOCKER_API_VERSION = "1.24"
CONTAINERS = ["rabbitmq-bd", "mongo_default"]

RABBIT_HOST = "localhost"
RABBIT_PORT = 15672
RABBIT_USER = "guest"
RABBIT_PASS = "guest"
RABBIT_QUEUES = ["test1.test1"]


exit_event = threading.Event()

def signal_handler(signal, frame):
  if exit_event.is_set():
    return
  exit_event.set()
  m.stop()


class Monitor:


  def __init__(self):

    self.DOCKER = docker.from_env(version=DOCKER_API_VERSION)
    self.DOCKER_LOWLEVEL = docker.APIClient(base_url=DOCKER_BASE_URL,
                                            version=DOCKER_API_VERSION)

    self.DOCKER_STATS = {c: {
      'stream': self.DOCKER.containers.get(c).stats(decode=True, stream=True),
      'stats': []
    } for c in CONTAINERS}
    self.RABBIT_STATS = {q: {
      'stats': []
    } for q in RABBIT_QUEUES}


  def start(self):
    print("Monitoring started..")
    print("Press ^C to stop")

    while not exit_event.is_set():

      # docker stats
      for c in CONTAINERS:
        res = next(self.DOCKER_STATS[c]['stream'])

        self.DOCKER_STATS[c]['stats'].append({
          'timestamp': _get_milliseconds(),
          'data': res
        })

      # rabbit stats
      for q in RABBIT_QUEUES:
        url = "http://{}:{}/api/queues/%2F/{}".format(RABBIT_HOST, RABBIT_PORT, q)
        res = requests.get(url, auth=(RABBIT_USER, RABBIT_PASS))
        if res.status_code != 200:
          print("[rabbit-stats] error; status_code={}".format(status_code))
          continue
        res = res.json()

        self.RABBIT_STATS[q]['stats'].append({
          'timestamp': _get_milliseconds(),
          'data': res
        })


  def stop(self):
    print("Monitoring stopped\nProcessing results..")

    for c in CONTAINERS:
      print(c, json.dumps(self.DOCKER_STATS[c]['stats'], indent=2, sort_keys=True))

    for q in RABBIT_QUEUES:
      print(q, json.dumps(self.RABBIT_STATS[q]['stats'], indent=2, sort_keys=True))

    print("Done\nTerminating..")


if __name__ == "__main__":
  global m

  signal.signal(signal.SIGINT, signal_handler)

  m = Monitor()
  m.start()
