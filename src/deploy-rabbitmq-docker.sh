#!/bin/bash

sudo docker run \
-d --name rabbitmq-bd \
--hostname rabbitmq-bd \
-p 5672:5672 \
-p 15672:15672 \
-v /home/bogdan/docker/rabbitmq/lib:/var/lib/rabbitmq \
--cpus="1" \
--memory="512m" \
--memory-swap="512m" \
bogdan/rabbitmq/bd:3-management

# -v /media/bogdan/Data/Personal/CTI/BD/Project/docker/rabbitmq/lib:/var/lib/rabbitmq \
# container stops, don't know why. maybe because of the ntfs file system [?]

# --memory-swap="512m" \
# Your kernel does not support swap limit capabilities or the cgroup is not mounted

# --storage-opt size="32G" \
# not supported for aufs
