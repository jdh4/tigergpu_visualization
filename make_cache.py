#!/usr/licensed/anaconda3/2020.11/bin/python
  
base = "/home/jdh4/bin/gpus"

import sys
sys.path = list(filter(lambda p: p.startswith("/usr"), sys.path))
sys.path.append(base)
import json
import subprocess
import pandas as pd
from dossier import ldap_plus

if 1:
  rows = []
  with open(base + "/utilization.json") as fp:
    for line in fp.readlines():
      x = json.loads(line)
      rows.append(list(x.values()))
  df = pd.DataFrame(rows)
  del rows
  df.columns = ['timestamp', 'host', 'index', 'username', 'usage', 'jobid']
  netids = list(df.username.drop_duplicates().values)
  if "root" in netids: netids.remove("root")
  if "OFFLINE" in netids: netids.remove("OFFLINE")
else:
  cmd = "getent passwd | cut -d: -f1 | sort | uniq"
  output = subprocess.run(cmd, capture_output=True, shell=True)
  netids = output.stdout.decode("utf-8").split('\n')
  netids.remove('')
  netids.remove('+')

univ_info = ldap_plus(sorted(netids))
df = pd.DataFrame(univ_info[1:], columns=univ_info[0])
cols = ['NETID', 'POSITION', 'DEPT', 'NAME', 'SPONSOR']
df = df[cols]
df = df[pd.notna(df.POSITION) | pd.notna(df.DEPT) | pd.notna(df.SPONSOR)]
df.to_csv(f"{base}/cached_users.csv", columns=cols, index=False)
