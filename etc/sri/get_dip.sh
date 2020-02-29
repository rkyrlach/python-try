#!/bin/bash

rm "/etc/sri/dipsw.txt"
python3 read-dip-switches.py>>"/etc/sri/dipsw.txt"


