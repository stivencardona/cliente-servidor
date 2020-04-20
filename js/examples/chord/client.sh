#!/bin/bash

mkdir client-$1
head -c 20M /dev/urandom > client-$1/testfile
ID=$1 IP=$2 PORT=$3 node client.js
rm -r client-$1
