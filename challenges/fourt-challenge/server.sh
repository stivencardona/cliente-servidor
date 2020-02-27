#!/bin/bash

mkdir storage-server-$1-$2
echo "Input server format:"
echo "<proxy_ip>"
echo "<proxy_port>"
python3 server.py $1 $2
rm -r storage-server-$1-$2