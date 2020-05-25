#!/usr/licensed/anaconda3/2020.2/bin/python
import sys
sys.path = list(filter(lambda p: p.startswith("/usr"), sys.path))
sys.path.append('/scratch/gpfs/jdh4/gpustat')
import subprocess
import pandas as pd
from dossier import ldap_plus

cmd = "getent passwd | cut -d: -f1 | sort | uniq"
output = subprocess.run(cmd, capture_output=True, shell=True)
netids = output.stdout.decode("utf-8").split('\n')
netids.remove('')
netids.remove('+')

univ_info = ldap_plus(netids[:50])
df = pd.DataFrame(univ_info[1:], columns=univ_info[0])
cols = ['NETID', 'POSITION', 'DEPT', 'SPONSOR']
df = df[cols]
df = df[pd.notna(df.POSITION) | pd.notna(df.DEPT) | pd.notna(df.SPONSOR)]
df.to_csv('/scratch/gpfs/jdh4/gpustat/cached_users.csv', columns=cols, index=False)
