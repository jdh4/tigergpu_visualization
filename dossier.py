import pandas as pd
import subprocess
from collections import defaultdict

depts = {'Advanced Projects, Princeton Plasma Physics Laboratory':'PPPL',
'Applied and Computational Mathematics':'PACM',
'Andlinger Center for Energy and the Environment':'ACEE',
'Astrophysical Sciences':'ASTRO',
'Astrophysical Sciences, Plasma Physics Laboratory':'ASTRO/PPPL',
'Atmospheric and Oceanic Sciences':'AOS',
'Center for Statistics and Machine Learning':'CSML',
'Chemical and Biological Engineering':'CBE',
'Chemistry':'CHEM',
'Civil and Environmental Engineering':'CEE',
'Computer Science':'CS',
'Ecology and Evolutionary Biology':'EEB',
'Economics':'ECON',
'Electrical Engineering':'EE',
'Engineering and Technical Infrastructure, Princeton Plasma Physics Lab':'PPPL',
'Enterprise Infrastructure Services, Office of Information Technology':'OIT',
'Fusion Simulation Program, Princeton Plasma Physics Laboratory':'PPPL',
'Geosciences':'GEO',
'ITER and Tokamaks, Princeton Plasma Physics Laboratory':'PPPL',
'Information Technology, Princeton Plasma Physics Laboratory':'PPPL',
'Lewis-Sigler Institute for Integrative Genomics':'LSI',
'Library - Information Technology':'LIBRARY',
'Mathematics':'MATH',
'Mechanical and Aerospace Engineering':'MAE',
'Molecular Biology':'MOLBIO',
'Office of the Director, Princeton Plasma Physics Laboratory':'PPPL',
'Operations Research and Financial Engineering':'ORFE',
'Physics':'PHYSICS',
'Plasma Science and Technology, Princeton Plasma Physics Laboratory':'PPPL',
'Politics':'POLITICS',
'Princeton Center for Theoretical Science':'PCTS',
'Princeton Environmental Institute':'PEI',
'Princeton Institute for Computational Science and Engineering':'PICSciE',
'Princeton Institute for International and Regional Studies':'PIIRS',
'Princeton Institute for the Science and Technology of Materials':'PRISM',
'Princeton Neuroscience Institute':'PNI',
'Psychology':'PSYCH',
'Research Computing, Office of Information Technology':'CSES',
'Special Student':'',
'Theory Department, Princeton Plasma Physics Laboratory':'PPPL',
'Undergraduate Class of 2019':'UDG2019',
'Undergraduate Class of 2020':'UDG2020',
'Undergraduate Class of 2021':'UDG2021',
'Undergraduate Class of 2022':'UDG2022',
'Undergraduate Class of 2023':'UDG2023',
'Undergraduate Class of 2024':'UDG2024',
'Undergraduate Class of 2025':'UDG2025',
'Undergraduate Class of 2026':'UDG2026',
'Woodrow Wilson School':'WWS'}

def make_dict(text):
  record = defaultdict(str)
  for line in text:
    if (':' in line):
      idx = line.find(':')
      field = line[:idx].replace('#', '').strip()
      value = line[idx + 1:].strip()
      record[field] = value
  return record

def format_sponsor(s):
  # extract last name from sponsor
  names = list(filter(lambda x: x not in ['Jr.', 'II', 'III', 'IV'], s.split()))
  if len(names) == 2:
    if len(names[1]) > 1: return names[1]
    else: return s
  elif (len(names) > 2):
    idx = 0
    while (names[idx].endswith('.') and (idx < len(names) - 1)):
      idx += 1
    names = names[idx:]
    e = ''.join([str(int(name.endswith('.'))) for name in names])
    if '1' in e: return ' '.join(names[e.index('1') + 1:])
    else: return names[-1]
  else:
    return s

def infer_position(edu, aca, title, stat):
  # infer the job position of the user
  if stat == 'undergraduate' or stat == 'xundergraduate':
    return 'Undergrad'
  elif aca in ['G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8', 'G9']:
    return aca
  elif 'postdoc' in title.lower():
    return 'Postdoc'
  elif (edu == 'Faculty' or stat == 'fac' or 'Professor' in title):
    return 'Faculty'
  elif (stat == 'stf' and 'visiting' in title.lower()):
    return 'Visitor'
  elif (edu == 'Staff' or stat == 'stf' or stat == 'xstf'):
    return 'Staff'
  elif edu == 'affiliate':
    if   stat == 'rcu': return 'RCU'
    elif stat == 'dcu': return 'DCU'
    elif stat == 'researchuser': return 'RU'
    elif stat == 'exceptiondcu': return 'XDCU'
    elif stat == 'sps': return 'SPS'
    else: return ''
  else:
    return ''

def dept_code(dept, stat, edu, office):
  # replace the department name with an abbreviation
  if (dept in depts):
    return depts[dept]
  elif ((dept == 'Unspecified Department' or edu == 'affiliate') and office):
    dept = office.split(',')[0].upper()
    trans = {'CHEMISTRY':'CHEM', 'PSYCHOLOGY':'PSYCH','GENOMICS':'LSI'}
    return dept if dept not in trans else trans[dept]
  else:
    return ''

def ldap_plus(netids):
  # return a dataframe with a row of info for each netid
  columns = ['NAME', 'DEPT', 'STATUS', 'POSITION', 'TITLE', 'ACAD', 'OFFICE', \
             'SPONSOR', 'NETID', 'NETID_TRUE']
  people = [columns]
  not_found = 0
  for netid in netids:
    output = subprocess.run("ldapsearch -x uid=" + netid, shell=True,
                            capture_output=True)
    lines = output.stdout.decode("utf-8").split('\n')
    record = make_dict(lines)
    uid_success = (record['numResponses'] == str(2))

    mail_success = False
    if (not uid_success):
      # netid not found so assume it was an alias and search by mail
      output = subprocess.run("ldapsearch -x mail=" + netid + "@princeton.edu",
                              shell=True, capture_output=True)
      lines = output.stdout.decode("utf-8").split('\n')
      record = make_dict(lines)
      mail_success = (record['numResponses'] == str(2))

    if ((not uid_success) and (not mail_success)):
      # both attempts failed
      people.append([None] * (len(columns) - 1) + [netid])
      not_found += 1
    else:
      # netid_true is the true netid while netid may be an alias
      netid_true = record['uid']
      name = record['displayName']
      dept = record['ou']
      title = record['title']
      stat = record['pustatus']
      aca = record['puacademiclevel']
      phone = record['telephoneNumber']
      edu = record['eduPersonPrimaryAffiliation']
      #street = record['street']
      #addr = record['puinterofficeaddress']

      # get office (i.e, principal investigator or project)
      output = subprocess.run("finger " + netid_true, shell=True, \
                              capture_output=True)
      lines = output.stdout.decode("utf-8").split('\n')
      finger = make_dict(lines)
      office = finger['Office']

      # get and format sponsor
      output = subprocess.run("getent passwd " + netid_true, shell=True,
                              capture_output=True)
      line = output.stdout.decode("utf-8").split('\n')
      sponsor = line[0].split(':')[4].split(',')[-1] if line != [''] else 'NULL'
      sponsor = format_sponsor(sponsor)

      position = infer_position(edu, aca, title, stat)
      dept = dept_code(dept, stat, edu, office)
      #addr = addr.replace('$', ', ')

      people.append([name, dept, stat, position, title, aca, office, sponsor, \
                     netid, netid_true])
  #if (not_found): print('Number of netids not found: %d' % not_found)
  return pd.DataFrame(people[1:], columns=people[0])
