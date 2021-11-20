import subprocess
from collections import defaultdict

depts = {'Advanced Projects, Princeton Plasma Physics Laboratory':'PPPL',
'Applied and Computational Mathematics':'PACM',
'Andlinger Center for Energy and the Environment':'ACEE',
'Analytics & Data Management, University Advancement':'ANALYTICS',
'Anthropology':'ANTHRO',
'Architecture':'ARCH',
'Art and Archaeology':'ART-ARCH',
'Astrophysical Sciences':'ASTRO',
'Astrophysical Sciences, Plasma Physics Laboratory':'ASTRO/PPPL',
'Atmospheric and Oceanic Sciences':'AOS',
'Bendheim Center for Finance':'FINANCE',
'Center for Digital Humanities':'CDH',
'Center for Information Technology Policy':'IT-POL',
'Classics':'CLASSICS',
'Computational Science, Princeton Plasma Physics Laboratory':'PPPL',
'Center for Statistics and Machine Learning':'CSML',
'Chemical and Biological Engineering':'CBE',
'Chemistry':'CHEM',
'Civil and Environmental Engineering':'CEE',
'Computer Science':'CS',
'Data Driven Social Science':'DDSS',
'East Asian Studies':'EAS',
'Electrical and Computer Engineering':'ECE',
'Enterprise Infrastructure Services, Office of Information Techno':'OIT',
'Ecology and Evolutionary Biology':'EEB',
'Economics':'ECON',
'Electrical Engineering':'EE',
'Engineering and Technical Infrastructure, Princeton Plasma Physi':'PPPL',
'Engineering and Technical Infrastructure, Princeton Plasma Physics Lab':'PPPL',
'English':'ENGLSH',
'Enterprise Infrastructure Services, Office of Information Technology':'OIT',
'French and Italian':'LANGUAGE',
'Fusion Simulation Program, Princeton Plasma Physics Laboratory':'PPPL',
'Geosciences':'GEO',
'High Meadows Environmental Institute':'ENV-INST',
'History':'HISTORY',
'History of Science':'HIST-SCI',
'Industrial Relations':'INDUST-REL',
'Information Security Office':'ISO',
'ITER and Tokamaks, Princeton Plasma Physics Laboratory':'PPPL',
'Information Technology, Princeton Plasma Physics Laboratory':'PPPL',
'Lewis-Sigler Institute for Integrative Genomics':'LSI',
'Library - Information Technology':'LIBRARY',
'Library - Scholarly Collections and Research Services':'LIBRARY',
'Library - Special Collections':'LIBRARY',
'Music':'MUSIC',
'Mathematics':'MATH',
'Mechanical and Aerospace Engineering':'MAE',
'Molecular Biology':'MOLBIO',
'Near Eastern Studies':'NES',
'Office of the Dean for Research':'DEAN-RES',
'Office of the Dean of the College':'DEAN-COL',
'Office of the Dean of the Faculty':'DEAN-FAC',
'Office of the Dean of Undergraduate Students':'DEAN-UND',
'Office of the Vice President for Information Technology':'VP-IT',
'Other Affiliates':'AFFIL',
'Office of the Director, Princeton Plasma Physics Laboratory':'PPPL',
'Operations and Planning, Office of Information Technology':'OIT',
'Operations Research and Financial Engineering':'ORFE',
'Pace Center for Civic Engagement':'CIV-ENGAGE',
'Philosophy':'PHIL',
'Plasma Science and Technology, Princeton Plasma Physics Laborato':'PPPL',
'Population Research':'POP-RES',
'Princeton Center for Language Study':'LANGUAGE',
'Princeton University Investment Company':'INVEST',
'Princeton Writing Program':'WRITING',
'Physics':'PHYSICS',
'Plasma Science and Technology, Princeton Plasma Physics Laboratory':'PPPL',
'Politics':'POLITICS',
'Princeton Center for Theoretical Science':'PCTS',
'Princeton Environmental Institute':'PEI',
'Princeton Institute for Computational Science and Engineering':'PICSciE',
'Princeton Institute for International and Regional Studies':'PIIRS',
'Princeton Institute for the Science and Technology of Materials':'PRISM',
'Princeton Neuroscience Institute':'PNI',
'Princeton School of Public and International Affairs':'SPIA',
'Psychology':'PSYCH',
'Research Computing, Office of Information Technology':'CSES',
'Special Student':'',
'Service Management Office, Office of Information Technology':'OIT',
'Sociology':'SOCIO',
'Software and Application Services, Office of Information Technol':'OIT',
'Spanish and Portuguese':'LANG',
'Theory Department, Princeton Plasma Physics Laboratory':'PPPL',
'Undergraduate Class of 2019':'UDG2019',
'Undergraduate Class of 2020':'UDG2020',
'Undergraduate Class of 2021':'UDG2021',
'Undergraduate Class of 2022':'UDG2022',
'Undergraduate Class of 2023':'UDG2023',
'Undergraduate Class of 2024':'UDG2024',
'Undergraduate Class of 2025':'UDG2025',
'Undergraduate Class of 2026':'UDG2026',
'Undergraduate Class of 2027':'UDG2027',
'Undergraduate Class of 2028':'UDG2028',
'Undergraduate Class of 2029':'UDG2029',
'Undergraduate Class of 2030':'UDG2030',
'Undergraduate Class withheld':'UDG',
'Unspecified Department':'UNKNOWN',
'Vice President, Plasma Physics Lab':'PPPL',
'Woodrow Wilson School':'WWS'}

def make_dict(text):
  # make dictionary out of strings separated by colons
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

def infer_position(edu, aca, title, stat, dept):
  # infer the job position of the user
  if stat == 'undergraduate' or stat == 'xundergraduate' or stat == 'ugdcu':
    if dept.startswith('Undergraduate Class of '): return 'Udrg' + dept[-4:]
    return 'Undergrad'
  elif edu == 'alum' and dept.startswith('Undergraduate Class of '):
    return 'Udrg' + dept[-4:]
  elif aca in ['G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8', 'G9']:
    return aca
  elif 'postdoc' in title.lower():
    return 'Postdoc'
  elif (edu.lower() == 'faculty' or stat == 'fac' or 'professor' in title.lower()):
    return 'Faculty'
  elif (stat == 'stf' and 'visiting' in title.lower()):
    return 'Visitor'
  elif (edu.lower() == 'staff' or stat == 'stf' or stat == 'xstf'):
    return 'Staff'
  elif edu.lower() == 'affiliate':
    if   stat == 'rcu': return 'RCU'
    elif stat == 'dcu': return 'DCU'
    elif stat == 'researchuser': return 'RU'
    elif stat == 'exceptiondcu': return 'XDCU'
    elif stat == 'sps': return 'SPS'
    else: return ''
  else:
    return ''

def get_dept_code(dept, stat, edu, office):
  # replace the department name with an abbreviation
  trans = {'CHEMISTRY':'CHEM', 'PSYCHOLOGY':'PSYCH','GENOMICS':'LSI'}
  if ((dept.startswith('Undergraduate Class of ') or dept == 'Unspecified Department' \
      or edu == 'affiliate') and office):
    odept = office.split(',')[0].upper()
    return odept if odept not in trans else trans[odept]
  elif (dept in depts):
    return depts[dept]
  else:
    return ''

def get_office_from_finger(netid_true):
  # get office (i.e, principal investigator or project)
  output = subprocess.run("finger " + netid_true, shell=True, \
			  capture_output=True)
  lines = output.stdout.decode("utf-8").split('\n')
  finger = make_dict(lines)
  return finger['Office']

def get_sponsor_from_getent(netid_true):
  # get sponsor of the user
  output = subprocess.run("getent passwd " + netid_true, shell=True,
                          capture_output=True)
  line = output.stdout.decode("utf-8").split('\n')
  sponsor = line[0].split(':')[4].split(',')[-1] if line != [''] else 'NULL'
  return sponsor

def ldap_plus(netids):
  # return a list of lists
  columns = ['NAME', 'DEPT', 'STATUS', 'POSITION', 'TITLE', 'ACAD', 'OFFICE', \
             'SPONSOR', 'NETID', 'NETID_TRUE']
  people = [columns]
  not_found = 0
  for netid in netids:
    uid_except = False
    try:
      output = subprocess.run("ldapsearch -x uid=" + netid, capture_output=True, \
                              shell=True, timeout=2)
    except:
      uid_except = True
      uid_success = False
    else:
      lines = output.stdout.decode("utf-8").split('\n')
      record = make_dict(lines)
      uid_success = (record['numResponses'] == str(2))

    mail_except = False
    mail_success = False
    if (not uid_success):
      # netid not found so assume it was an alias and search by mail
      # this good idea comes from R. Knight
      try:
        output = subprocess.run("ldapsearch -x mail=" + netid + "@princeton.edu",
                                capture_output=True, shell=True, timeout=2)
      except:
        mail_except = True
        mail_success = False
      else:
        lines = output.stdout.decode("utf-8").split('\n')
        record = make_dict(lines)
        mail_success = (record['numResponses'] == str(2))

    if ((not uid_success) and (not mail_success)):
      # both attempts failed
      people.append([None] * (len(columns) - 2) + [netid, None])
      not_found += 1
    elif (uid_except and mail_except):
      # both commands failed
      people.append([None] * (len(columns) - 2) + [netid, None])
    else:
      # netid_true is the true netid while netid may be an alias
      netid_true = record['uid']
      name = record['cn']  # sponsor_report uses cn to get name
      dept = record['ou']
      title = record['title']
      stat = record['pustatus']
      aca = record['puacademiclevel']
      phone = record['telephoneNumber']
      edu = record['eduPersonPrimaryAffiliation']
      #street = record['street']
      #addr = record['puinterofficeaddress']

      office = get_office_from_finger(netid_true)
      sponsor = format_sponsor(get_sponsor_from_getent(netid_true))
      position = infer_position(edu, aca, title, stat, dept)
      dept_code = get_dept_code(dept, stat, edu, office)
      #addr = addr.replace('$', ', ')

      people.append([name, dept_code, stat, position, title, aca, office, sponsor, \
                     netid, netid_true])
  #if (not_found): print('Number of netids not found: %d' % not_found)
  return people
