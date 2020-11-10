# TigerGPU Visualization

This repo contains a set of scripts used for monitoring GPU utilization and usage on TigerGPU.

## checkgpu

The `checkgpu` command shows the mean GPU utilization and overall usage by user, department or sponsor. This command is available on Tiger and Tigressdata.

### How to use it?

Add this line to your `~/.bashrc` file on each cluster (Adroit, Della, Perseus, Tiger, Tigressdata and Traverse):

```bash
alias checkgpu='/home/jdh4/bin/checkgpu'
```

Then look at the examples at the bottom of the help menu:

```
# ssh tiger, tigergpu or tigressdata
$ checkgpu -h
```
