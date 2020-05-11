#!/bin/bash

for i in {1..11}
do
    ./compiler -p "testfiles/test$i"
done
