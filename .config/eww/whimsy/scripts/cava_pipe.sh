#!/bin/bash
confPath="$(pwd)/scripts/cava_config"

# Taken from Tail-R
cava -p $confPath | while read -r line; do echo $line| sed -e 's/;/,/g'; done | while read -r line; do echo "["`echo ${line/%?/}`"]"; done
