#!/bin/bash
cd /scratch/gpfs/jdh4/gpustat
/usr/licensed/anaconda3/2019.10/bin/python tigergpu_usage.py
cp tigergpu_utilization.png /tigress/jdh4/public_html

HOUR=$(date +%-H)
MINUTES=$(date +%M)
REMAIN=$(($HOUR % 2))
if [[ $REMAIN -eq 0 && $MINUTES -lt 10 ]]; then
   MONTH=$(date +%b)
   DAY=$(date +%d)
   MYPATH=/scratch/gpfs/jdh4/gpustat/history
   mv tigergpu_utilization.png ${MYPATH}/tigergpu_utilization_${DAY}_${MONTH}_${HOUR}_${MINUTES}.png
fi

find /scratch/gpfs/jdh4/gpustat/history -name '*.png' -mtime +7 -exec rm -f {} \;
