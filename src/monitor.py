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

from logger import LogshtashLogger


EPOCH = datetime.utcfromtimestamp(0)

def _get_milliseconds():
  return (datetime.utcnow() - EPOCH).total_seconds() * 1000.0


LOGSTASH_HOST = "127.0.0.1"
LOGSTASH_PORT = 8082

DOCKER_BASE_URL = "unix://var/run/docker.sock"
DOCKER_API_VERSION = "1.24"
CONTAINERS = ["rabbitmq-bd", "clients-bd", "elk-bd"]

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


  def __init__(self, output_dir, analysis_params):

    self.OUTPUT_DIR = output_dir
    self.ANALYSIS_PARAMS = analysis_params

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

    self.LOGSTASH = LogshtashLogger(LOGSTASH_HOST, LOGSTASH_PORT)


  def start(self, raw=False):
    print("Monitoring started..")
    print("Press ^C to stop")

    while not exit_event.is_set():

      # docker stats
      for c in CONTAINERS:
        res = next(self.DOCKER_STATS[c]['stream'])

        data = {
          "timestamp": _get_milliseconds(),
          "target": {"docker_base_url": DOCKER_BASE_URL, "container": c},
          "analysis_params": self.ANALYSIS_PARAMS,
          "stats": self.extract_metrics_docker(res)
        }
        if raw:
          data["raw"] = res

        self.DOCKER_STATS[c]['stats'].append(data)
        self.LOGSTASH.log(metric_type="stats", metric="docker", data=data)

      # rabbit stats
      for q in RABBIT_QUEUES:
        url = "http://{}:{}/api/queues/%2F/{}".format(RABBIT_HOST, RABBIT_PORT, q)
        res = requests.get(url, auth=(RABBIT_USER, RABBIT_PASS))
        if res.status_code != 200:
          print("[rabbit-stats] error; status_code={}".format(res.status_code))
          continue
        res = res.json()

        data = {
          "timestamp": _get_milliseconds(),
          "target": {"host": RABBIT_HOST, "port": RABBIT_PORT, "queue": q},
          "analysis_params": self.ANALYSIS_PARAMS,
          "stats": self.extract_metrics_rabbit(res)
        }
        if raw:
          data["raw"] = res
        
        self.RABBIT_STATS[q]['stats'].append(data)
        self.LOGSTASH.log(metric_type="stats", metric="rabbitmq", data=data)


  def stop(self):
    print("Monitoring stopped\nProcessing results..")

    # dump data to files
    for c in CONTAINERS:
      with open(path.join(self.OUTPUT_DIR, "docker_{}.json".format(c)), "w") as f:
        json.dump(self.DOCKER_STATS[c]['stats'], fp=f, indent=2, sort_keys=True)
    for q in RABBIT_QUEUES:
      with open(path.join(self.OUTPUT_DIR, "rabbitmq_{}.json".format(q)), "w") as f:
        json.dump(self.RABBIT_STATS[q]['stats'], fp=f, indent=2, sort_keys=True)

    print("Done\nTerminating..")


  def extract_metrics_docker(self, data):
    try:
      res = {
        "memory": {
          "usage": data["memory_stats"]["usage"],
          "max_usage": data["memory_stats"]["max_usage"],
          "limit": data["memory_stats"]["limit"],
          "usage_percentage": float(data["memory_stats"]["usage"]) / data["memory_stats"]["limit"] * 100,
        },
        "cpu": {

        },
        # "blkio": {},
        # "networks": {}
      }
    except Exception as e:
      print("[error][extract_metrics_docker] Unable to extract docker metrics. error={}".format(e))
      return {}

    try:
      res["cpu"]["usage_percentage"] = self.compute_cpu_usage_percentage(data["precpu_stats"], data["cpu_stats"])
    except Exception as e:
      print("[error][extract_metrics_docker] Unable to compute_cpu_usage_percentage. error={}".format(e))
      pass

    return res


  def extract_metrics_rabbit(self, data):   
    try:
      res = {
        "consumers": data["consumers"],
        "consumer_utilisation": data["consumer_utilisation"],
        "messages": data["messages"],
        "messages_details": data["messages_details"],
        "message_stats": data["message_stats"],
        "messages_ready": data["messages_ready"],
        "messages_ready_details": data["messages_ready_details"],
        "messages_unacknowledged": data["messages_unacknowledged"],
        "messages_unacknowledged_details": data["messages_unacknowledged_details"],
      }
    except Exception as e:
      print("[error][extract_metrics_rabbit] Unable to extract rabbitmq metrics. error={}".format(e))
      res = {}

    return res


  def compute_cpu_usage_percentage(self, previous, current):
    cpu_percent = 0.0

    cpu_delta = float(current["cpu_usage"]["total_usage"]) - previous["cpu_usage"]["total_usage"]
    system_delta = float(current["system_cpu_usage"]) - previous["system_cpu_usage"]

    if cpu_delta > 0 and system_delta > 0:
      cpu_percent = cpu_delta / system_delta * len(current["cpu_usage"]["percpu_usage"]) * 100

    return cpu_percent




if __name__ == "__main__":
  global m

  signal.signal(signal.SIGINT, signal_handler)

  output_dir = path.join(OUTPUT_DIR, str(datetime.now()))
  if not path.exists(output_dir):
    os.makedirs(output_dir)

  # TODO: take from argv the current analysis params
  analysis_params = {}

  m = Monitor(output_dir, analysis_params)
  m.start(raw=False)
