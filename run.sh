#!/bin/sh
cd outputs
rm -rf *
mkdir simulator_outputs
cd ../patternutils/
python3 plot_Figure2.py --bitwidth=4
python3 plot_Figure2.py --bitwidth=8
python3 start.py
cd ../hwutils/
python3 main.py
python3 ratio.py > ../outputs/figure8_raw.txt
cat outputs/figure8_raw.txt
