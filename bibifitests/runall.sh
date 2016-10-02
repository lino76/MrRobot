#!/usr/bin/bash

for i in $(ls *.json); do
	./run.py $1 $i
done
