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
