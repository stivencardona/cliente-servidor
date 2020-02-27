#!/bin/bash

mkdir storage-client-$1
head -c 200M /dev/urandom > storage-client-$1/testfile
echo "Input client format:"
echo "<command> [upload, download]"
echo "<filename> [testfile: default file]"
python3 client.py $1 $2 $3
rm -r storage-client-$1