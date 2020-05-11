#!/bin/bash

for i in {1..11}
do
    ./compiler -t "testfiles/test$i.asm" "testfiles/test$i"
done
