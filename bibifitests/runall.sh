#!/bin/bash

for i in $(ls *.json); do
        echo $i
	./run.py $1 ../build/server $i
done
