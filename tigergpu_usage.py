"""This script runs gpustat on the TigerGPU nodes excluding cyroem.
   The output of gpustat is written to file for each node. The files
   are used to make a visualization of GPU usage versus time.
   Files older than 1 hour are deleted."""

import subprocess
from datetime import datetime, timedelta
from glob import glob
from time import time

#tiger-i19g1  Mon Mar  2 12:22:58 2020
#[0] Tesla P100-PCIE-16GB | 41'C,  55 % |  1656 / 16280 MB | tgartner(255M)
#[1] Tesla P100-PCIE-16GB | 42'C,  54 % |  1656 / 16280 MB | tgartner(881M)
#[2] Tesla P100-PCIE-16GB | 41'C,  56 % |  1656 / 16280 MB | tgartner(255M)
#[3] Tesla P100-PCIE-16GB | 41'C,  57 % |  1656 / 16280 MB | tgartner(255M)

def extract_username(myfield):
  if '(' in myfield:
    return myfield[:myfield.index('(')]
  else:
    return ''

def process_gpustat_output(myfile):
  """This function takes a text file of gpustat output and
     it extracts and stores the relevant data."""
  with open(myfile, 'r') as f:
    lines = f.readlines()
  try:
    node_timestamp = lines[0]
    node = node_timestamp.split()[0]
    timestamp = int(myfile.split('.')[1])
    for line in lines[1:]:
      # assuming that we can split on white space to separate fields
      fields = line.strip().split()
      gpu_index = int(fields[0].replace('[', '').replace(']', ''))
      percent_usage = int(fields[5])
      username = '' if len(fields) < 14 else extract_username(fields[13])
      usage_user[(node, gpu_index, timestamp)] = (percent_usage, username)
  except:
    # failure here will cleanly result in "NO INFO" downstream
    pass

def process_all_files():
  gpufiles = glob('*.gpustat')
  for gpufile in gpufiles:
    process_gpustat_output(gpufile)

def cell_color(username, usage):
  # set cell color
  if (username == '' or username == 'NO INFO'):
     fcolor = '#CCCCCC'
  elif (usage == 0):
     fcolor = "#000000"
  elif (usage < 25):
     fcolor = "#FF0000"
  elif (usage < 50):
     fcolor = "#FF8C00"
  else:
     fcolor = "#FFFFFF"
  return fcolor

def celltext(username, usage):
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
  import matplotlib.pyplot as plt
  _, _, timestamps = zip(*usage_user.keys())
  times = sorted(set(timestamps))
  times = times[-num_snapshots:]
  # next line prevents IndexError in ax[idx, j] when script ran for first time
  if len(times) == 1: times = 2 * times
  fig, ax = plt.subplots(nrows=num_gpus, ncols=len(times), figsize=(10, 80))
  for i, node in enumerate(nodes):
      for gpu_index in range(gpus_per_node):
        idx = gpus_per_node * i + gpu_index
        for j, t in enumerate(times):
          mykey = (node, gpu_index, t)
          if (mykey in usage_user):
            usage, username = usage_user[mykey]
          else:
            usage, username = (-1, 'NO INFO')
          ax[idx, j].set_facecolor(cell_color(username, usage))
          # remove spines and ticks
          for side in ['top', 'right', 'bottom', 'left']:
            ax[idx, j].spines[side].set_visible(False)
          ax[idx, j].get_xaxis().set_ticks([])
          ax[idx, j].get_yaxis().set_ticks([])
          # set cell and labels text
          txtclr = 'w' if (usage < 25 or username == '') else 'k'
          ax[idx, j].text(0.5, 0.5, celltext(username, usage), fontsize=10, color=txtclr, \
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
  # -d and -I remove zero padding (linux only)
  fig.suptitle('TigerGPU Utilization (' + str(dt.strftime("%a %b %-d")) + ')', \
               y=0.997, ha='center', fontsize=18)
  fig.tight_layout(pad=0, w_pad=0, h_pad=0, rect=(0, 0, 1, 0.99))
  plt.savefig('tigergpu_utilization.png')

def remove_old_files():
  """Remove gpustat files that are more than an hour old if there
     are more than the minimum needed files."""
  import os
  gpufiles = glob('*.gpustat')
  if (len(gpufiles) > len(nodes) * num_snapshots):
    for gpufile in gpufiles:
      timestamp = int(gpufile.split('.')[1])
      dt = datetime.now() - datetime.fromtimestamp(timestamp)
      if (dt.seconds > 3600):
        os.remove(gpufile)

def write_data():
  _, _, timestamps = zip(*usage_user.keys())
  tmax = max(timestamps)
  f = open('utilization.csv', 'a')
  for node in nodes:
    for gpu_index in range(gpus_per_node):
      mykey = (node, gpu_index, tmax)
      if (mykey in usage_user):
        usage, username = usage_user[mykey]
        f.write('%d,%s,%d,%s,%d\n' % (int(tmax), node, gpu_index, username, usage))
  f.close()

# generate the node names
nodes = ['tiger-i' + str(i) + 'g' + str(j+1) for i in range(19, 24) for j in range(16)]
nodes.remove('tiger-i19g5')
nodes.remove('tiger-i23g13')
cryoem = ['tiger-h' + str(i) + 'g' + str(j) for i in range(19, 27) for j in [1, 2]] + \
         ['tiger-i26g1', 'tiger-i26g2']
cryoem.remove('tiger-h22g1')
#nodes += cryoem  # do not include cryoem node
assert len(nodes) == 78, "Assert: Node count"

# total expected gpus (equal to number of rows)
gpus_per_node = 4
num_gpus = gpus_per_node * len(nodes)

# display up to this number of snapshots (equal to number of columns)
num_snapshots = 7

usage_user = {}
timestamp = str(int(time()))
for node in nodes:
  gpustat_file = node + "." + timestamp + ".gpustat"
  cmd = "ssh -o ConnectTimeout=5 " + node + " \"gpustat > /scratch/gpfs/jdh4/gpustat/" + \
         gpustat_file + "\" > /dev/null 2>&1"
  try:
     # run the command via ssh on the compute nodes
     _ = subprocess.run(cmd, shell=True)
  except:
    # failure here will cleanly result in "NO INFO" downstream
    pass

process_all_files()
if usage_user: create_image()
if usage_user: write_data()
remove_old_files()
