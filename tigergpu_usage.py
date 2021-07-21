"""This script runs gpustat on the TigerGPU nodes excluding cyroem.
   The output of gpustat is written to file for each node. The files
   are used to make a visualization of GPU usage versus time.
   Files older than 1 hour are deleted."""

import subprocess
from datetime import datetime, timedelta
from glob import glob
from time import time
import re

#scontrol show hostname tiger-i14g[1-20]
#nodeset -e tiger-i14g[1-20]

#tiger-h26c1n7,tiger-i26c1n[18,22,24],tiger-i26c2n13
#tiger-h20c1n6,tiger-h25c2n[9-10],tiger-h26c2n[6-7]
#tiger-h25c2n[1,4,6,10-12,15]
#tiger-i25c1n[13-16]
#tiger-i25c1n9

#sihuid   R 6        6 1    gpu:2      tiger-i23g13
#smondal  R 1        8 1    gpu:1      tiger-i20g16
#vcorbit  R 1        1 1    gpu:1      tiger-i23g15

def extract_from_range(hosts):
  # handles cases with ranges such as tiger-h26c2n[6-7]
  base = hosts[:hosts.index("[")]
  other = hosts[hosts.index("[") + 1:-1]
  individs = []
  for num in other.split(","):
    if "-" in num:
      start, end = map(int, num.split("-"))
      individs.extend(map(lambda x: base + str(x), list(range(start, end + 1))))
    else:
      individs.append(base + num)
  return individs

def extract_nodes(hosts):
  single_hosts = []
  for host in hosts:
    if host.startswith("iger"): host = "t" + host
    if "[" in host:
      single_hosts.extend(extract_from_range(host))
    else:
      single_hosts.append(host)
  return single_hosts

def squeue_gpus(node):
  names = []
  for line in singles:
    user, state, cores, num_nodes, gres, host = line.split()
    if node == host:
      num_gpus = int(gres.split(":")[1])
      for _ in range(num_gpus):
        names.append(user)
  return names

#tiger-i19g1  Mon Mar  2 12:22:58 2020
#[0] Tesla P100-PCIE-16GB | 41'C,  55 % |  1656 / 16280 MB | tgartner(255M)
#[1] Tesla P100-PCIE-16GB | 42'C,  54 % |  1656 / 16280 MB | tgartner(881M)
#[2] Tesla P100-PCIE-16GB | 41'C,  56 % |  1656 / 16280 MB | tgartner(255M)
#[3] Tesla P100-PCIE-16GB | 41'C,  57 % |  1656 / 16280 MB | tgartner(255M)

#tiger-i19g3  Sun May  9 11:48:29 2021
#[0] NVIDIA Tesla P100-PCIE-16GB | 46'C, 100 % |   271 / 16280 MB | jongkees(269M)
#[1] NVIDIA Tesla P100-PCIE-16GB | 49'C, 100 % |   271 / 16280 MB | jongkees(269M)
#[2] NVIDIA Tesla P100-PCIE-16GB | 51'C, 100 % |   271 / 16280 MB | jongkees(269M)
#[3] NVIDIA Tesla P100-PCIE-16GB | 50'C, 100 % |   271 / 16280 MB | jongkees(269M)

def extract_username(myfield):
  if '(' in myfield:
    name = myfield[:myfield.index('(')]
    memory = myfield[myfield.index('(') + 1:-1]
    return (name, memory)
  else:
    return ('', "42G")

def process_gpustat_output(myfile, max_stamp):
  """This function takes a text file of gpustat output and
     it extracts and stores the relevant data."""
  with open(myfile, 'r') as f:
    lines = f.readlines()
  try:
    node_timestamp = lines[0]
    node = node_timestamp.split()[0]
    timestamp = int(myfile.split('.')[1])
    ggpus = ['', '', '', '']
    ggpus_count = 0
    for line in lines[1:]:
      # assuming that we can split on white space to separate fields
      line = line.replace("NVIDIA Tesla", "Tesla")
      fields = line.strip().split()
      gpu_index = int(fields[0].replace('[', '').replace(']', ''))
      percent_usage = int(fields[5])
      username, memory = ('', "42G") if len(fields) < 14 else extract_username(fields[13])
      gpu_proc = False if memory == "0J" else True
      usage_user[(node, gpu_index, timestamp)] = (percent_usage, username, gpu_proc)
      if timestamp == max_stamp:
        ggpus[gpu_index] = username
        if username != '': ggpus_count += 1
 
    if timestamp == max_stamp:
      # check for mismatch between allocated gpus (squeue) and active gpus (gpustat)
      sgpus = squeue_gpus(node)
      if len(sgpus) > ggpus_count and len(sgpus) <= 4:
        # users have allocated gpus without gpu processes
        for name in ggpus:
          if name in sgpus: sgpus.remove(name)
        sgpus.sort()

        # fill in missing names
        changed_indices = []
        ptr = 0
        for i in range(4):
          if ggpus[i] == '' and ptr < len(sgpus):
            usage_user[(node, i, timestamp)] = (0, sgpus[ptr], False)
            ggpus[i] = sgpus[ptr]
            ptr += 1
            changed_indices.append(i)

        # overwrite files with usernames for new entries
        for i in changed_indices:
          name = ggpus[i]
          lines[i + 1] = lines[i + 1].replace("16280 MB |", f"16280 MB | {name}(0J)") 
        with open(myfile, 'w') as f:
          for line in lines:
            f.write(line)

  except:
    # failure here will cleanly result in "NO INFO" downstream
    pass

def process_all_files():
  gpufiles = glob('/scratch/gpfs/jdh4/gpustat/dot_gpustat/*.gpustat')
  max_stamp = max(map(lambda x: int(x.split(".")[1]), gpufiles))
  for gpufile in gpufiles:
    if debug: print(gpufile)
    process_gpustat_output(gpufile, max_stamp)

def cell_color(username, usage, gpu_proc):
  # set cell color
  if (username == '' or username == 'NO INFO'):
     fcolor = '#CCCCCC'
  elif (usage == 0 and gpu_proc):
     fcolor = "#000000"
  elif (usage == 0 and not gpu_proc):
     fcolor = "#000099"
  elif (usage < 25):
     fcolor = "#FF0000"
  elif (usage < 50):
     fcolor = "#FF8C00"
  elif (usage < 75):
     fcolor = "#F9E79F"
  else:
     fcolor = "#FFFFFF"
  return fcolor

def celltext(node, j, username, usage):
  # text for each cell
  if (username == ''):
    ctext = 'IDLE'
  elif (username == 'NO INFO'):
    ctext = username
  else:
    ctext = username + ":" + str(usage)
  return ctext

def gpu_labels(gpu_index, node):
  # set labels for gpu ids and node names
  lbl = str(gpu_index)
  if (gpu_index == 0):
    lbl = node + '  ' + lbl
  elif (gpu_index == 1 and node in cryoem):
    lbl = '(cryoem)    ' + lbl
  return lbl

def create_image():
  import matplotlib
  matplotlib.use('Agg')
  import matplotlib.pyplot as plt
  _, _, timestamps = zip(*usage_user.keys())
  times = sorted(set(timestamps))
  times = times[-num_snapshots:]
  # next line prevents IndexError in ax[idx, j] when script runs for first time
  if len(times) == 1: times = 2 * times
  fig, ax = plt.subplots(nrows=num_gpus, ncols=len(times), figsize=(10, 80))
  # write to file
  f = open("dashboard.csv", "w")
  for i, node in enumerate(nodes):
      for gpu_index in range(gpus_per_node):
        idx = gpus_per_node * i + gpu_index
        for j, t in enumerate(times):
          mykey = (node, gpu_index, t)
          if (mykey in usage_user):
            usage, username, gpu_proc = usage_user[mykey]
          else:
            usage, username = (-1, 'NO INFO')
          ax[idx, j].set_facecolor(cell_color(username, usage, gpu_proc))
          # remove spines and ticks
          for side in ['top', 'right', 'bottom', 'left']:
            ax[idx, j].spines[side].set_visible(False)
          ax[idx, j].get_xaxis().set_ticks([])
          ax[idx, j].get_yaxis().set_ticks([])
          # set cell and labels text
          txtclr = 'w' if (usage < 25 or username == '') else 'k'
          to_write = ','.join([datetime.fromtimestamp(t).strftime('%-I:%M %p'), node, str(gpu_index), username, str(usage)])
          f.write(to_write + "\n")
          ax[idx, j].text(0.5, 0.5, celltext(node, j, username, usage), fontsize=10, color=txtclr, \
                          ha='center', va='center', transform=ax[idx, j].transAxes)
          # node and gpu index labels
          if (j == 0): ax[idx, j].set_ylabel(gpu_labels(gpu_index, node), fontsize=12, \
                                             rotation=0, ha='right', va='center')
          dt = datetime.fromtimestamp(t)
          # -I removes zero padding (linux only)
          stamp = dt.strftime('%-I:%M %p')
          if (idx == 0):
            ax[idx, j].xaxis.set_label_position('top')
            ax[idx, j].set_xlabel(stamp, fontsize=12, rotation=0, ha='center', va='bottom')
  f.close()
  # -d and -I remove zero padding (linux only)
  fig.suptitle('TigerGPU Utilization (' + str(dt.strftime("%a %b %-d")) + ')', \
               y=0.997, ha='center', fontsize=18)
  fig.tight_layout(pad=0, w_pad=0, h_pad=0, rect=(0, 0, 1, 0.99))
  if not debug: plt.savefig('tigergpu_utilization.png')

def remove_old_files():
  """Remove gpustat files that are more than an hour old if there
     are more than the minimum needed files."""
  import os
  gpufiles = glob('/scratch/gpfs/jdh4/gpustat/dot_gpustat/*.gpustat')
  if (len(gpufiles) > len(nodes) * num_snapshots):
    for gpufile in gpufiles:
      timestamp = int(gpufile.split('.')[1])
      dt = datetime.now() - datetime.fromtimestamp(timestamp)
      if (dt.seconds > 3600):
        os.remove(gpufile)

def write_data():
  _, _, timestamps = zip(*usage_user.keys())
  tmax = max(timestamps)
  with open('utilization.csv', 'a') as f:
    for node in nodes:
      for gpu_index in range(gpus_per_node):
        mykey = (node, gpu_index, tmax)
        if (mykey in usage_user):
          usage, username, gpu_proc = usage_user[mykey]
          f.write('%d,%s,%d,%s,%d\n' % (int(tmax), node, gpu_index, username, usage))

###############################
## if __name__ == "__main__" ##
###############################

# generate the node names
nodes = ['tiger-i' + str(i) + 'g' + str(j+1) for i in range(19, 24) for j in range(16)]
cryoem = []
squeue_lines = []

# remove down and drained nodes while finding idle nodes
#cmd = "timeout 3 sinfo -p gpu --Node -h | grep -E 'drain|down|boot|drng'"
cmd = "timeout 3 sinfo -p gpu --Node -h | grep -E 'drain|down'"
try:
  output = subprocess.run(cmd, capture_output=True, shell=True, timeout=3)
  lines = output.stdout.decode("utf-8").split('\n')
  for line in lines:
    #if any([term in line for term in ["drain", "down", "boot", "drng"]]):
    if "drain" in line or "down" in line:
      bad_node = line.split()[0]
      if re.match('tiger-i[12][01239]g[0-9]{1,2}', bad_node):
        nodes.remove(bad_node)
except:
  pass

with open("/scratch/gpfs/jdh4/gpustat/nodes.log", "w") as f:
  for node in nodes:
    f.write(node + "\n")

# store the running jobs with username, node and number of gpus
cmd = "timeout 3 squeue -p gpu -t R -h -o '%.8u %.2t %.6C %4D %10b %R'"
try:
  output = subprocess.run(cmd, capture_output=True, shell=True, timeout=3)
  squeue_lines = output.stdout.decode("utf-8").split('\n')
except:
  pass

squeue_lines = list(filter(lambda x: len(x) > 0, squeue_lines))
# make each item in squeue_lines have only one node in singles
singles = []
for line in squeue_lines:
  user, state, cores, num_nodes, gres, many_hosts = line.split()
  if num_nodes == "1":
    singles.append(line)
  else:
    for host in extract_nodes(many_hosts.split(",t")):
      singles.append(" ".join([user, state, cores, num_nodes, gres, host]))

# debug flag
debug = False

# total expected gpus (equal to number of rows)
gpus_per_node = 4
num_gpus = gpus_per_node * len(nodes)

# display up to this number of snapshots (equal to number of columns)
num_snapshots = 7

usage_user = {}
timestamp = str(int(time()))
if not debug:
  for node in nodes:
    gpustat_file = node + "." + timestamp + ".gpustat"
    cmd = "timeout 5 ssh -o ConnectTimeout=4 " + node + " \"gpustat > /scratch/gpfs/jdh4/gpustat/dot_gpustat/" + \
           gpustat_file + "\" > /dev/null 2>&1"
    try:
       # run the command via ssh on the compute nodes
       _ = subprocess.run(cmd, shell=True, timeout=6)
    except:
      # failure here will cleanly result in "NO INFO" downstream
      pass

process_all_files()
if debug:
 for u,v in zip(usage_user.keys(), usage_user.values()):
    print(u,v)
if usage_user and not debug: create_image()
if usage_user and not debug: write_data()
if not debug: remove_old_files()
