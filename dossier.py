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
'Computer Science':'COS',
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
'Physics':'PHYS',
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
  names = list(filter(lambda x: x not in ['Jr.', 'II', 'III', 'IV'], s.split()))
  if len(names) == 2:
    if len(names[1]) > 1: return names[1]
    else: return s
  elif (len(names) > 2):
    idx = 0
    while names[idx].endswith('.'):
      idx += 1    
    names = names[idx:]
    e = ''.join([str(int(name.endswith('.'))) for name in names])
    if '1' in e: return ' '.join(names[e.index('1') + 1:])
    else: return names[-1]
  else:
    return names[-1]

def infer_position(edu, aca, title, stat):
  edict = {'faculty':'Faculty', 'staff':'Staff', 'student':'Student', \
           'affiliate':'Affiliate'}
  if (edu in edict): edu = edict[edu]
  grad = ['G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8', 'G9']
  if 'postdoc' in title.lower():
    position = 'Postdoc'
  elif aca in grad:
    position = aca
  elif stat == 'undergraduate':
    position = 'Undergrad'
  elif 'scholar' in title.lower():
    position = 'Scholar'
  elif 'lecturer' in title.lower():
    position = 'Lecturer'
  elif 'instructor' in title.lower():
    position = 'Instructor'
  else:
    position = edu
  return position

def dept_code(dept, stat):
  if (dept in depts):
    dept = depts[dept]
  elif (dept == 'Unspecified Department'):
    if   stat == 'rcu': dept = '(RCU)'
    elif stat == 'dcu': dept = '(DCU)'
    elif stat == 'researchuser': dept = '(RU)'
    elif stat == 'exceptiondcu': dept = '(XDCU)'
    elif stat == 'sps': dept = '(SPS)'
    else: dept = ''
  else:
    #print('\n\n*** MISSING DEPT: ', dept, '\n\n')
    dept = ''
  return dept

def ldapbio(netids):
  # return a dataframe of info on each netid
  not_found = 0
  columns = ['NAME', 'DEPT', 'STATUS', 'EDU', 'TITLE', 'ACAD', 'OFFICE', \
             'SPONSOR', 'USER2LDAP', 'NETID']
  people = [columns]
  for netid in netids:
    output = subprocess.run("ldapsearch -x uid=" + netid, shell=True,
                            capture_output=True)
    lines = output.stdout.decode("utf-8").split('\n')
    record = make_dict(lines)
    uid_success = (record['numResponses'] == str(2))

    mail_success = False
    if (not uid_success):
      # netid not found so assume it was an email alias and search by mail
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
      # netid2 is the true netid while netid may be an email alias
      netid2 = record['uid']
      name = record['displayName']
      dept = record['ou']
      title = record['title']
      stat = record['pustatus']
      aca = record['puacademiclevel']
      phone = record['telephoneNumber']
      edu = record['eduPersonPrimaryAffiliation']
      street = record['street']
      addr = record['puinterofficeaddress']

      # get office (i.e, principal investigator or project)
      output = subprocess.run("finger " + netid2, shell=True,
                              capture_output=True)
      lines = output.stdout.decode("utf-8").split('\n')
      finger = make_dict(lines)
      office = finger['Office']

      # get sponsor
      output = subprocess.run("getent passwd " + netid2, shell=True,
			      capture_output=True)
      line = output.stdout.decode("utf-8").split('\n')
      sponsor = line[0].split(':')[4].split(',')[-1] if line != [''] else 'NULL'
      sponsor = format_sponsor(sponsor)

      position = infer_position(edu, aca, title, stat)
      dept = dept_code(dept, stat)
      addr = addr.replace('$', ', ')

      people.append([name, dept, stat, position, title, aca, office, sponsor, netid, netid2])
  return pd.DataFrame(people[1:], columns=people[0])
