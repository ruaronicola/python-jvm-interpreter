#!/bin/sh
cd examples
rm *.class
javac --release 8 *.java
cd ..
./run_unittest.py
