#!/bin/bash

sudo docker run -d \
--name elk-bd \
--hostname elk-bd \
-p 5601:5601 \
-p 9200:9200 \
-p 8082:8082 \
bogdan/sebp/elk/bd

# 5601 (Kibana web interface).
# 9200 (Elasticsearch JSON interface).
# 8082 (Logstash HTTP interface).
