#!/bin/bash

mkdir client-$1
head -c 10M /dev/urandom > client-$1/testfile
node client.js
rm -r client-$1