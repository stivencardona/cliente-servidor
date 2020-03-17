#!/bin/bash

mkdir peer-$1
PORT=$1 IPCONNECT=$2 PORTCONNECT=$3 node server.js >> logs-peer-$1.txt
rm -r peer-$1
rm logs-peer-$1.txt