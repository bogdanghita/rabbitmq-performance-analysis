#!/usr/bin/env python3

import sys, os
import json
import docker
import signal
import time
from datetime import datetime
import threading
import requests
from os import path


EPOCH = datetime.utcfromtimestamp(0)

def _get_milliseconds():
  return (datetime.utcnow() - EPOCH).total_seconds() * 1000.0


DOCKER_BASE_URL = "unix://var/run/docker.sock"
DOCKER_API_VERSION = "1.24"
CONTAINERS = ["rabbitmq-bd"]

RABBIT_HOST = "localhost"
RABBIT_PORT = 15672
RABBIT_USER = "guest"
RABBIT_PASS = "guest"
RABBIT_QUEUES = [
  "performance-analysis.gauss-rand",
  "performance-analysis.poisson-rand",
  "performance-analysis.geometric-rand",
  "performance-analysis.exp-rand",
  "performance-analysis.exp-series"
]

OUTPUT_DIR = "../output/"

USAGE_MSG = "Usage: ./monitor.py"


exit_event = threading.Event()

def signal_handler(signal, frame):
  if exit_event.is_set():
    return
  exit_event.set()
  m.stop()


class Monitor:


  def __init__(self, output_dir):

    self.OUTPUT_DIR = output_dir

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


  def start(self, raw=False):
    print("Monitoring started..")
    print("Press ^C to stop")

    while not exit_event.is_set():

      # docker stats
      for c in CONTAINERS:
        res = next(self.DOCKER_STATS[c]['stream'])

        data = {
          'timestamp': _get_milliseconds(),
          'metrics': self.extract_metrics_docker(res)
        }
        if raw:
          data['raw'] = res
        self.DOCKER_STATS[c]['stats'].append(data)

      # rabbit stats
      for q in RABBIT_QUEUES:
        url = "http://{}:{}/api/queues/%2F/{}".format(RABBIT_HOST, RABBIT_PORT, q)
        res = requests.get(url, auth=(RABBIT_USER, RABBIT_PASS))
        if res.status_code != 200:
          print("[rabbit-stats] error; status_code={}".format(res.status_code))
          continue
        res = res.json()

        data = {
          'timestamp': _get_milliseconds(),
          'metrics': self.extract_metrics_rabbit(res)
        }
        if raw:
          data['raw'] = res
        self.RABBIT_STATS[q]['stats'].append(data)


  def stop(self):
    print("Monitoring stopped\nProcessing results..")

    # dump data to files
    for c in CONTAINERS:
      with open(path.join(self.OUTPUT_DIR, "{}.json".format(c)), "w") as f:
        json.dump(self.DOCKER_STATS[c]['stats'], fp=f, indent=2, sort_keys=True)
    for q in RABBIT_QUEUES:
      with open(path.join(self.OUTPUT_DIR, "{}.json".format(q)), "w") as f:
        json.dump(self.RABBIT_STATS[q]['stats'], fp=f, indent=2, sort_keys=True)

    print("Done\nTerminating..")


  def extract_metrics_docker(self, data):
    res = {}

    # TODO

    return res

  def extract_metrics_rabbit(self, data):
    res = {}

    # TODO

    return res


if __name__ == "__main__":
  global m

  signal.signal(signal.SIGINT, signal_handler)

  output_dir = path.join(OUTPUT_DIR, str(datetime.now()))
  if not path.exists(output_dir):
    os.makedirs(output_dir)

  m = Monitor(output_dir)
  m.start(raw=True)
