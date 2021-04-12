#!/bin/bash

echo Hello World
source /home/bsvscraper/.bashrc
conda activate /var/opt/realestimator
python /var/opt/realestimator/scripts/ingatlan_com.py -e PROD -s 0
