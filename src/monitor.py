#!/bin/bash

CONTAINER_ID="32f4a5fb7c7fa7dd9b8da126533d2bf542bb36ee327308b3925d75e8f04daf1b"


# [disk]
printf "*** DISK ***\n"

# docker system df -v
docker ps -s -f "id=${CONTAINER_ID}"


# [memory]
printf "\n*** MEMORY ***\n"

BASE_DIR="/sys/fs/cgroup/memory/docker/${CONTAINER_ID}"

echo -n "usage: Mem (mb): " && expr `cat ${BASE_DIR}/memory.usage_in_bytes` / 1024 / 1024
echo -n "limit: Mem+swap (mb): " && expr `cat ${BASE_DIR}/memory.limit_in_bytes` / 1024 / 1024

