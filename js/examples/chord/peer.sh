#!/bin/bash

mkdir peer-$1
PORT=$1 IPCONNECT=$2 PORTCONNECT=$3 node server.js
rm -r peer-$1