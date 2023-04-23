import subprocess
from collections import defaultdict

depts = {'Advanced Projects, Princeton Plasma Physics Laboratory':'PPPL',
'Applied and Computational Mathematics':'PACM',
'Andlinger Center for Energy and the Environment':'ACEE',
'Analytics & Data Management, University Advancement':'ANALYTICS',
'Anthropology':'ANTHRO',
'Architecture':'ARCHIT',
'Art and Archaeology':'ART-ARCH',
'Astrophysical Sciences':'ASTRO',
'Astrophysical Sciences, Plasma Physics Laboratory':'ASTRO/PPPL',
'Atmospheric and Oceanic Sciences':'AOS',
'Bendheim Center for Finance':'FINANCE',
'Center for Digital Humanities':'CDH',
'Center for Information Technology Policy':'IT-POL',
'Center for Policy Research on Energy and the Environment':'C-PREE',
'Classics':'CLASSICS',
'Computational Science, Princeton Plasma Physics Laboratory':'PPPL',
'Center for Statistics and Machine Learning':'CSML',
'Chemical and Biological Engineering':'CBE',
'Chemistry':'CHEM',
'Civil and Environmental Engineering':'CEE',
'Comparative Literature':'COMP-LIT',
'Computer Science':'CS',
'Data Driven Social Science':'DDSS',
'East Asian Studies':'EAS',
'Electrical and Computer Engineering':'ECE',
'Enterprise Infrastructure Services, Office of Information Techno':'OIT',
'Ecology and Evolutionary Biology':'EEB',
'Economics':'ECON',
'Electrical Engineering':'ECE',
'Engineering and Technical Infrastructure, Princeton Plasma Physi':'PPPL',
'Engineering and Technical Infrastructure, Princeton Plasma Physics Lab':'PPPL',
'English':'ENGLISH',
'Enterprise Infrastructure Services, Office of Information Technology':'OIT',
'Financial Services, Office of the VP for Finance and Treasurer':'FIN-SERVICE',
'French and Italian':'FRENCH-ITAL',
'Fusion Simulation Program, Princeton Plasma Physics Laboratory':'PPPL',
'Geosciences':'GEO',
'German':'GERMAN',
'High Meadows Environmental Institute':'HMEI',
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
'Library-Data, Research and Teaching Services':'LIBRARY',
'Library - Collections and Access Services':'LIBRARY',
'Library - Deputy University Library':'LIBRARY',
'Music':'MUSIC',
'Mathematics':'MATH',
'McGraw Center for Teaching and Learning':'MCGRAW',
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
'Population Research':'OPR',
'Princeton Center for Language Study':'LANG-STUDY',
'Princeton University Investment Company':'INVEST-CO',
'Princeton Writing Program':'WRITING',
'Physics':'PHYSICS',
'Plasma Science and Technology, Princeton Plasma Physics Laboratory':'PPPL',
'Politics':'POLITICS',
'Princeton Center for Theoretical Science':'PCTS',
'Princeton Environmental Institute':'PEI',
'Princeton Institute for Computational Science and Engineering':'PICSCIE',
'Princeton Institute for International and Regional Studies':'PIIRS',
'Princeton Institute for the Science and Technology of Materials':'PRISM',
'Princeton Neuroscience Institute':'PNI',
'Princeton School of Public and International Affairs':'SPIA',
'Programs in Access & Opportunity':'ACCESS-OPP',
'Psychology':'PSYCH',
'Research Computing, Office of Information Technology':'CSES',
'Research Integrity and Assurance':'RES-INTEG-ASSUR',
'Special Student':'SPEC-STUDENT',
'Service Management Office, Office of Information Technology':'OIT',
'Sociology':'SOCIO',
'Software and Application Services, Office of Information Technol':'OIT',
'Spanish and Portuguese':'SPANISH-PORT',
'Theory Department, Princeton Plasma Physics Laboratory':'PPPL',
'Undergraduate Class of 2019':'U2019',
'Undergraduate Class of 2020':'U2020',
'Undergraduate Class of 2021':'U2021',
'Undergraduate Class of 2022':'U2022',
'Undergraduate Class of 2023':'U2023',
'Undergraduate Class of 2024':'U2024',
'Undergraduate Class of 2025':'U2025',
'Undergraduate Class of 2026':'U2026',
'Undergraduate Class of 2027':'U2027',
'Undergraduate Class of 2028':'U2028',
'Undergraduate Class of 2029':'U2029',
'Undergraduate Class of 2030':'U2030',
'Undergraduate Class withheld':'U20XX',
'Unspecified Department':'UNSPECIFIED',
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
    else: return " ".join(names)
  elif (len(names) > 2):
    idx = 0
    while (names[idx].endswith('.') and (idx < len(names) - 1)):
      idx += 1
    names = names[idx:]
    e = ''.join([str(int(name.endswith('.'))) for name in names])
    if '1' in e: return ' '.join(names[e.index('1') + 1:])
    else: return names[-1]
  else:
    return " ".join(names)

def get_position(netid):
  """Note that each field can appear multiple times. The netid is assumed to be a 
     true netid and not an alias. Otherwise call ldap_plus to get position."""
  cmd = f"ldapsearch -x uid={netid}"
  try:
    output = subprocess.run(cmd, capture_output=True, shell=True, timeout=5)
  except:
    return ""
  lines = output.stdout.decode("utf-8").split('\n')
  if lines != [] and lines[-1] == "": lines = lines[:-1]
  return get_position_from_lines(lines)

def get_position_from_lines(lines):
  faculty = False
  xfaculty = False
  emeritus = False
  staff = False
  postdoc_in_title = False
  prof_in_title = False
  lecturer = False
  scholar = False
  collaborator = False
  fellow = False
  graduate = False
  xgraduate = False
  Gx = ""
  gradaccept = False
  undergraduate = False
  Ux = ""
  rcu = False
  dcu = False
  ru = False
  xdcu = False
  sps = False
  xstf = False
  cas = False
  retired = False
  intern_or_assist = False
  alumg = False
  visitor = False
  for line in lines:
    if line.startswith("#"): continue
    line = line.lower()
    if "professor" in line and "title:" in line: prof_in_title = True
    if ("pustatus: fac" in line or "puaffiliation: fac" in line) or prof_in_title: faculty = True
    if "puaffiliation: xfac" in line or "pustatus: xfac" in line: xfaculty = True
    if "pustatus: eme" in line: emeritus = True
    if "lecturer" in line and "title:" in line: lecturer = True
    if "research scholar" in line and "title:" in line: scholar = True
    if "collaborator" in line and "title:" in line: collaborator = True
    if "fellow" in line and "title:" in line: fellow = True
    if "pustatus: stf" in line or "puaffiliation: stf" in line: staff = True
    if "postdoc" in line and "title:" in line: postdoc_in_title = True
    if "visit" in line and "title:" in line: visitor = True
    if "pustatus: graduate" in line: graduate = True
    if "puaffiliation: xgraduate" in line or "pustatus: xgraduate" in line: xgraduate = True
    if "puacademiclevel" in line and any([f" g{yr}" in line for yr in range(1, 10)]): Gx = line.split()[-1]
    if "pustatus: gradaccept" in line: gradaccept = True
    if "pustatus: undergraduate" in line: undergraduate = True
    if "undergraduate class of" in line: Ux = line.split()[-1]  # or use puclassyear
    if "pustatus: rcu" in line or "puaffiliation: rcu" in line: rcu = True
    if "pustatus: dcu" in line or "puaffiliation: dcu" in line: dcu = True
    if "pustatus: researchuser" in line or "puaffiliation: researchuser" in line: ru = True
    if "pustatus: exceptiondcu" in line: xdcu = True
    if "pustatus: sps" in line: sps = True
    if "pustatus: xstf" in line: xstf = True
    if "pustatus: xmiscaffil" in line: return "XMiscAffil"
    if "pustatus: alumg" in line: alumg = True
    if "pustatus: cas" in line: cas = True
    if "pustatus: ret" in line: retired = True
    if ("intern" in line or "assist" in line) and "title" in line: intern_or_assist = True

  # cleaning
  if faculty and postdoc_in_title and not prof_in_title:
    faculty = False
  if faculty and lecturer and not prof_in_title:
    faculty = False
  visiting = " (visiting)" if visitor else ""
  former_gx = f" (formerly {Gx.upper()})" if Gx else ""

  other = [rcu, dcu, ru, xdcu, sps, xstf, cas]
  if faculty and not xfaculty and not emeritus:
    return f"Faculty{visiting}"
  elif xfaculty and not emeritus:
    return "XFaculty"
  elif emeritus:
    return "Faculty (emeritus)"
  elif lecturer and postdoc_in_title:
    return "Lecturer and Postdoc"
  elif lecturer:
    return f"Lecturer{visiting}"
  elif scholar:
    return f"Scholar{visiting}"
  elif collaborator:
    return f"Collaborator{visiting}{former_gx}"
  elif fellow and not postdoc_in_title:
    return f"Fellow{visiting}"
  elif staff and not postdoc_in_title:
    return f"Staff{visiting}"
  elif staff and postdoc_in_title:
    return "Postdoc"
  elif xgraduate:
    return f"XGraduate{former_gx}"
  elif graduate and Gx and not alumg:
    return Gx.upper()
  elif graduate and Gx and alumg:
    return f"Alumni{former_gx}"
  elif Gx and alumg and not any(other):
    return f"Alumni{former_gx}"
  elif Gx and not alumg and not any(other):
    return f"{Gx.upper()}"
  elif graduate:
    return "Graduate"
  elif undergraduate and Ux and not alumg:
    return f"U{Ux}"
  elif undergraduate and Ux and alumg:
    return f"Alumni (U{Ux})"
  elif undergraduate or Ux:
    return f"U{Ux}"
  elif rcu:
    return f"RCU{visiting}{former_gx}"
  elif dcu:
    return f"DCU{visiting}{former_gx}"
  elif ru:
    return f"RU{visiting}{former_gx}"
  elif xdcu:
    return f"XDCU{visiting}{former_gx}"
  elif sps:
    return "SPS"
  elif xstf:
    return "XStaff"
  elif cas:
    return f"Casual{former_gx}"
  elif retired:
    return "Retired"
  elif gradaccept:
    return "G0"
  else:
    return "UNKNOWN"

def clean_position(position, level=0):
  """Level 3: Faculty, Staff, Postdoc, Graduate, Undergraduate
  if level == 3:
    if position.startswith("U20") or "Alumni (U" in position or position == "U":
      position = "Undergrad"
    if "Alumni (G" in position or "XGraduate" in position:
      position = "Graduate"
    if position in [f"G{n}" for n in range(1, 10)]:
      position = "Graduate"
    others = ("XStaff", "Casual", "Scholar", "Lecturer", "Collaborator", "Fellow")
    if any([p in position for p in others]):
      position = "Staff"
    if "Lecturer and Postdoc" in position:
      position = "Postdoc"
    if "XFaculty" in position:
      position = "Faculty"
    if any([p in position for p in ("RCU", "DCU", "RU", "XDCU")]):
      position = "RCU/DCU/RU"
    position = position.split(" (")[0]
    return position
  position = position.split(" (")[0]
  if position in ("RCU", "DCU", "RU", "XDCU"):
    position = "RCU/DCU/RU"
  if level == 2:
    if position.startswith("U20"):
      position = "Undergrad"
    if position in [f"G{n}" for n in range(1, 10)]:
      position = "Graduate"
  return position

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

def get_dept_code(dept, stat, edu, office, resdept):
  # replace the department name with an abbreviation
  trans = {'CHEMISTRY':'CHEM', 'PSYCHOLOGY':'PSYCH','GENOMICS':'LSI'}
  if ((dept.startswith('Undergraduate Class of ') or dept == 'Unspecified Department' \
      or edu == 'affiliate') and office):
    odept = office.split(',')[0].upper()
    return odept if odept not in trans else trans[odept]
  elif (dept in depts):
    if dept == "Unspecified Department" and resdept in depts:
      return depts[resdept]
    else:
      return depts[dept]
  else:
    print(f"No entry in dictionary for {dept}")
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

def ldap_plus(netids, level=0):
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
      # could also look for multiple occurrences of campusid
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
      resdept = record['puresidentdepartment']
      title = record['title']
      stat = record['pustatus']
      aca = record['puacademiclevel']
      phone = record['telephoneNumber']
      edu = record['eduPersonPrimaryAffiliation']
      #street = record['street']
      #addr = record['puinterofficeaddress']

      office = get_office_from_finger(netid_true)
      sponsor = format_sponsor(get_sponsor_from_getent(netid_true))
      #position = infer_position(edu, aca, title, stat, dept)
      position = get_position(netid_true)
      if level > 0: position = clean_position(position, level)
      dept_code = get_dept_code(dept, stat, edu, office, resdept)
      #addr = addr.replace('$', ', ')

      people.append([name, dept_code, stat, position, title, aca, office, sponsor, \
                     netid, netid_true])
  #if (not_found): print('Number of netids not found: %d' % not_found)
  return people
