#!/usr/bin/env python3

import sys
import json
import docker
import signal
import time
from datetime import datetime
import threading


EPOCH = datetime.utcfromtimestamp(0)

def _get_milliseconds():
  return (datetime.utcnow() - EPOCH).total_seconds() * 1000.0


DOCKER_BASE_URL = "unix://var/run/docker.sock"
DOCKER_API_VERSION = "1.24"
CONTAINERS = ["rabbitmq-bd", "mongo_default"]


exit_event = threading.Event()

def signal_handler(signal, frame):
  if exit_event.is_set():
    return
  exit_event.set()
  m.stop()


class Monitor:


  def __init__(self, docker_base_url, docker_api_version):

    self.DOCKER = docker.from_env(version=docker_api_version)
    self.DOCKER_LOWLEVEL = docker.APIClient(base_url=docker_base_url,
                                            version=docker_api_version)

    self.STATS = {c: {
      'stream': self.DOCKER.containers.get(c).stats(decode=True, stream=True),
      'stats': []
    } for c in CONTAINERS}


  def start(self):

    while not exit_event.is_set():
      # TODO
      print("TODO: provide feedback so that the user knows that something is actual happending")

      for c in CONTAINERS:
        self.STATS[c]['stats'].append({
          'timestamp': _get_milliseconds(),
          'data': next(self.STATS[c]['stream'])
        })


  def stop(self):
    print("Monitorization stopped\nProcessing results..")

    for c in CONTAINERS:
      print(c, len(self.STATS[c]['stats']))

    print("Done\nTerminating..")


if __name__ == "__main__":
  global m

  signal.signal(signal.SIGINT, signal_handler)

  m = Monitor(DOCKER_BASE_URL, DOCKER_API_VERSION)
  m.start()
