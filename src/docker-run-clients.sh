#!/bin/bash

# sudo docker run -d \
sudo docker run -ti \
--name clients-bd \
--hostname clients-bd \
-v /home/bghita/rabbitmq-performance-analysis/src:/root/rabbitmq-performance-analysis/src \
--add-host=rabbitmq-bd:192.168.1.142 \
bogdan/ubuntu/bd:16.04
