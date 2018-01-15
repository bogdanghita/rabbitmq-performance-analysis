#!/usr/bin/env python3

import json
import requests


class LogshtashLogger:

  def __init__(self, host, port):
    self.URL = "http://{}:{}".format(host, port)

  def log(self, metric_type, metric, data):
    headers = {'content-type': 'application/json'}
    content = {
      "metric_type": metric_type,
      "metric": metric,
    }
    content.update(data)

    requests.put(self.URL, data=json.dumps(content), headers=headers)




if __name__ == "__main__":

  l = LogshtashLogger("127.0.0.1", 8082)
  l.log(metric_type="test", metric="test", data={"test-name": "mimi", "message":"zuzu"})
