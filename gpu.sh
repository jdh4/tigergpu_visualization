#!/bin/bash
timeout 30 /home/jdh4/bin/gpus/p100.sh
timeout 30 ssh della-gpu "/home/jdh4/bin/gpus/a100.sh"
timeout 30 ssh traverse "/home/jdh4/bin/gpus/v100.sh"
