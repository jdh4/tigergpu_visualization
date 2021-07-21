#!/bin/bash

ssh della-gpu "/home/jdh4/bin/a100/a100.sh"
ssh traverse "/home/jdh4/bin/v100/v100.sh"
/home/jdh4/bin/p100/p100.sh

# stellar
#ssh stellar-intel "/home/jdh4/software/della_gpu_stats/a100.sh"
#ssh stellar-intel "/usr/licensed/anaconda3/2020.11/bin/python /home/jdh4/software/della_gpu_stats/extract.py"

# tigergpu
#cd /scratch/gpfs/jdh4/gpustat
#/usr/licensed/anaconda3/2019.10/bin/python tigergpu_usage.py > /scratch/gpfs/jdh4/gpustat/jjjjjjj
#convert tigergpu_utilization.png -resize 850x -quality 50 tigergpu_utilization.png
#cp tigergpu_utilization.png /tigress/jdh4/public_html

#HOUR=$(date +%-H)
#MINUTES=$(date +%M)
#REMAIN=$(($HOUR % 2))
#if [[ $REMAIN -eq 0 && $MINUTES -lt 10 ]]; then
#   MONTH=$(date +%b)
#   DAY=$(date +%d)
#   MYPATH=/scratch/gpfs/jdh4/gpustat/history
#   mv tigergpu_utilization.png ${MYPATH}/tigergpu_utilization_${DAY}_${MONTH}_${HOUR}_${MINUTES}.png
#fi

#find /scratch/gpfs/jdh4/gpustat/history -name '*.png' -mtime +7 -exec rm -f {} \;
