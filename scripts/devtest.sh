#!/bin/bash

echo Hello World
source /home/bsvscraper/.bashrc
conda activate /var/opt/realestimator
python /var/opt/realestimator/scripts/ingatlan_com.py -e UAT -b 100 -s 32053682
