#!/bin/bash

# Kill all python processes before main.py initialization to avoid client-server connection problems
pkill -9 python

# Initialize main.py script
python main.py
