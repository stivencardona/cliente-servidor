#!/bin/bash

mkdir storage-server-$1-$2
python3 server.py $1 $2 $3 $4
rm -r storage-server-$1-$2