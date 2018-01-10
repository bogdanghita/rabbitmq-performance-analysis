#!/bin/bash

cd data

dd if=/dev/urandom of=8B.out bs=8 count=1
dd if=/dev/urandom of=64B.out bs=64 count=1
dd if=/dev/urandom of=128B.out bs=32 count=4
dd if=/dev/urandom of=512B.out bs=128 count=4

dd if=/dev/urandom of=1K.out bs=256 count=4
dd if=/dev/urandom of=2K.out bs=1024 count=2
dd if=/dev/urandom of=5K.out bs=1024 count=5
dd if=/dev/urandom of=10K.out bs=1024 count=10
dd if=/dev/urandom of=20K.out bs=1024 count=20
dd if=/dev/urandom of=50K.out bs=1024 count=50
dd if=/dev/urandom of=100K.out bs=1024 count=100
dd if=/dev/urandom of=500K.out bs=1024 count=500

dd if=/dev/urandom of=1M.out bs=1024 count=1024
dd if=/dev/urandom of=2M.out bs=2048 count=1024
dd if=/dev/urandom of=10M.out bs=10240 count=1024
dd if=/dev/urandom of=50M.out bs=10240 count=5120
dd if=/dev/urandom of=100M.out bs=10240 count=10240
