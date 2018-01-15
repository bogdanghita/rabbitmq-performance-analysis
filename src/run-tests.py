#!/usr/bin/env python3

import os
import subprocess
import time
import json

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)
print(dname)


TEST_FILES_PATH = "./tests/"
TEST_FILES = ["exp-rand_1K.json", "exp-series_1K.json", "gauss-rand_1K.json", "geometric-rand_1K.json", "poisson-rand_1K.json"]

RESULT_FILES_PATH = "./results/"

KIBANA_URL_TEMPLATE = "http://localhost:5601/app/kibana#/dashboard/b1f0d270-f9eb-11e7-a4b0-5155dd746b41?_g=(refreshInterval:('$$hashKey':'object:192',display:Off,pause:!f,section:0,value:0),time:(from:'{}',mode:absolute,to:'{}'))&_a=(description:'',filters:!(),fullScreenMode:!f,options:(darkTheme:!f,hidePanelTitles:!f,useMargins:!t),panels:!((gridData:(h:7,i:'1',w:6,x:0,y:10),id:'56df1220-f9eb-11e7-a4b0-5155dd746b41',panelIndex:'1',type:visualization,version:'6.1.1'),(gridData:(h:10,i:'2',w:6,x:0,y:0),id:'96c95160-f9f1-11e7-a4b0-5155dd746b41',panelIndex:'2',type:visualization,version:'6.1.1'),(gridData:(h:10,i:'3',w:6,x:6,y:0),id:ec1d93e0-f9f3-11e7-a4b0-5155dd746b41,panelIndex:'3',type:visualization,version:'6.1.1'),(gridData:(h:7,i:'4',w:6,x:6,y:10),id:c99f1800-f9f5-11e7-a4b0-5155dd746b41,panelIndex:'4',type:visualization,version:'6.1.1')),query:(language:lucene,query:''),timeRestore:!f,title:'RabbitMQ%20Performance%20Analysis',uiState:(),viewMode:view)"
KIBANA_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.0Z"




def run_test(name, params):
  print("[run_test] name: {}; params:\n{}".format(name, json.dumps(params, indent=2)))

  # register start time
  start_time = time.gmtime()

  # begin delay
  print("Waiting {}s..".format(params['begin_delay_s']))
  time.sleep(params['begin_delay_s'])

  # start producer & consumer
  print("Starting consumer..")
  c = subprocess.Popen(["./consumer.py", params['exchange'], params['queue']])
  print("Starting producer..")
  p = subprocess.Popen(["./producer.py", params['distribution'], params['file']])

  # let processes run
  time.sleep(params['run_time_s'])

  # stop producer & consumer
  print("Terminating producer..")
  p.kill()
  p.wait()
  print("Terminating consumer..")
  c.kill()
  c.wait()

  # end delay
  print("Waiting {}s..".format(params['end_delay_s']))
  time.sleep(params['end_delay_s'])

  # register end time
  end_time = time.gmtime()

  # export results
  start_time_fmt = time.strftime(KIBANA_TIME_FORMAT, start_time)
  end_time_fmt = time.strftime(KIBANA_TIME_FORMAT, end_time)
  result = "[run_test] end\ntime interval: {} - {}\nKibana URL: {}".format(
            start_time_fmt, end_time_fmt,
            KIBANA_URL_TEMPLATE.format(start_time_fmt, end_time_fmt))
  result_file = os.path.join(RESULT_FILES_PATH, "{}.out".format(name))
  with open(result_file, 'w') as fp:
    fp.write(result)
  print(result)





if __name__ == "__main__":

  for f in TEST_FILES:
    f_path = os.path.join(TEST_FILES_PATH, f)
    with open(f_path, 'r') as fp:
      params = json.load(fp)
      print(params)
      run_test(f, params)
