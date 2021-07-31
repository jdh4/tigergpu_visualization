# TigerGPU Visualization

This repo contains a set of scripts for monitoring GPU utilization and usage on TigerGPU.

## checkgpu

The `checkgpu` command shows the mean GPU utilization and overall usage by user, department or sponsor. This command is available on Tiger and Tigressdata.

### How to use it?

Add this line to your `~/.bashrc` file (della-gpu, tiger and traverse):

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

The UIDs and NetIDs are also stored once per week:

```
0 6 * * 1 getent passwd | awk -F":" '{print $3","$1}' > /home/jdh4/bin/gpus/master.uid 2> /dev/null
0 6 * * 1 ssh della 'getent passwd | awk -F":" '\''{print $3","$1}'\'' > /home/jdh4/bin/gpus/master.uid' > /dev/null 2>&1
0 6 * * 1 ssh traverse 'getent passwd | awk -F":" '\''{print $3","$1}'\'' > /home/jdh4/bin/gpus/master.uid' > /dev/null 2>&1
```

`gpu.sh` is:

```
#!/bin/bash
ssh della-gpu "/home/jdh4/bin/gpus/a100.sh"
ssh traverse "/home/jdh4/bin/gpus/v100.sh"
/home/jdh4/bin/gpus/p100.sh
```

For example:

```
$ cat /home/jdh4/bin/gpus/p100.sh
#!/bin/bash

DATA="/home/jdh4/bin/gpus/data"
SBASE="/scratch/.gpudash"
printf -v SECS '%(%s)T' -1

curl -s 'http://vigilant.sn2907:8480/api/v1/query?query=nvidia_gpu_duty_cycle' > ${DATA}/util.${SECS}
curl -s 'http://vigilant.sn2907:8480/api/v1/query?query=nvidia_gpu_jobUid'     > ${DATA}/uid.${SECS}
curl -s 'http://vigilant.sn2907:8480/api/v1/query?query=nvidia_gpu_jobId'      > ${DATA}/jobid.${SECS}

find ${DATA} -type f -mmin +70 -exec rm -f {} \;

/usr/licensed/anaconda3/2020.11/bin/python /home/jdh4/bin/gpus/extract.py

scp ${SBASE}/column.* tigercpu:${SBASE}
```

`extract.py` creates the "column" files for the gpudash command and it appends the latest data to `utilization.json`. `checkgpu` looks at `utilization.json`. `extract.py` lives in `https://github.com/jdh4/gpudash`

`extract.py` assumes a given set of hostnames. If a host is not found in the raw data from vigilant then the entry is written with the user as "OFFLINE" -- a better choice would have been "NO-INFO". Below are some samples from `utilization.json`:

```
{"timestamp": "1622344202", "host": "della-i14g15", "index": "1", "user": "OFFLINE", "util": "N/A", "jobid": "N/A"}  # no info from vigilant
{"timestamp": "1622344202", "host": "della-i14g20", "index": "0", "user": "gdolsten", "util": "40", "jobid": "34792230"}  # active job
{"timestamp": "1622344202", "host": "della-i14g20", "index": "1", "user": "root", "util": "0", "jobid": "0"}  # idle gpu
```

The code produces a line like:

```
Active GPUs/Idle GPUs/No Info = 60.8%/39.2%/1.2%
```

The code produces the line above assuming that all the GPUs are online. Tiger has 320 GPUs, Della-GPU 40 and Traverse 184. "No Info" correponds to down nodes and cases where vigilant fails to produce data.
