#!/bin/sh
cd example
rm *.class
javac --release 8 *.java
cd ..
./run_unittest.py
