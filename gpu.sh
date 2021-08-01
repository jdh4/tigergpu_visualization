#!/bin/bash

ssh della-gpu "/home/jdh4/bin/gpus/a100.sh"
ssh traverse "/home/jdh4/bin/gpus/v100.sh"
/home/jdh4/bin/gpus/p100.sh
