# TigerGPU Visualization

This repo contains a set of scripts for monitoring GPU utilization and usage on TigerGPU.

## checkgpu

The `checkgpu` command shows the mean GPU utilization and overall usage by user, department or sponsor. This command is available on Tiger and Tigressdata.

### How to use it?

Add this line to your `~/.bashrc` file (Tiger and Tigressdata):

```bash
alias checkgpu='/home/jdh4/bin/checkgpu'
```

Then look at the examples at the bottom of the help menu:

```
$ checkgpu -h
```

### Methodology

Every 10 minutes on tigergpu a script is called:

```
0,10,20,30,40,50 * * * * /scratch/gpfs/jdh4/gpustat/gpu.sh > /dev/null 2>&1
```

`gpu.sh` is:

```
#!/bin/bash
ssh della-gpu "/home/jdh4/bin/a100/a100.sh"
ssh traverse "/home/jdh4/bin/v100/v100.sh"
/home/jdh4/bin/p100/p100.sh
```

For example:

```
$ cat /home/jdh4/bin/p100/p100.sh
#!/bin/bash

DATA="/home/jdh4/bin/p100/data"
SBASE="/scratch/.gpudash"
printf -v SECS '%(%s)T' -1

curl -s 'http://vigilant.sn2907:8480/api/v1/query?query=nvidia_gpu_duty_cycle' > ${DATA}/util.${SECS}
curl -s 'http://vigilant.sn2907:8480/api/v1/query?query=nvidia_gpu_jobUid'     > ${DATA}/uid.${SECS}
curl -s 'http://vigilant.sn2907:8480/api/v1/query?query=nvidia_gpu_jobId'      > ${DATA}/jobid.${SECS}

find ${DATA} -type f -mmin +70 -exec rm -f {} \;

/usr/licensed/anaconda3/2020.11/bin/python /home/jdh4/bin/p100/extract.py

scp ${SBASE}/column.* tigercpu:${SBASE}
```

`extract.py` creates the "column" files for the gpudash command and it appends the latest data to `utilization.json`. `checkgpu` looks at `utilization.json`.
