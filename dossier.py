import subprocess
from collections import defaultdict
from base64 import b64decode

depts = {'Advanced Projects, Princeton Plasma Physics Laboratory':'PPPL',
'Applied and Computational Mathematics':'PACM',
'Andlinger Center for Energy and the Environment':'ACEE',
'Analytics & Data Management, University Advancement':'ANALYTICS',
'Anthropology':'ANTHRO',
'Architecture':'ARCHIT',
'Art and Archaeology':'ART-ARCH',
'Art Museum':'ART-MUSEUM',
'Astrophysical Sciences':'ASTRO',
'Astrophysical Sciences, Plasma Physics Laboratory':'PPPL',
'Atmospheric and Oceanic Sciences':'AOS',
'Bendheim Center for Finance':'FINANCE',
'Center for Digital Humanities':'CDH',
'Center for Information Technology Policy':'CITP',
'Center for Policy Research on Energy and the Environment':'C-PREE',
'Center for Language and Intelligence':'CLI',
'Center for Statistics and Machine Learning':'CSML',
'Chemical and Biological Engineering':'CBE',
'Chemistry':'CHEM',
'Civil and Environmental Engineering':'CEE',
'Classics':'CLASSICS',
'Comparative Literature':'COMP-LIT',
'Computational Science, Princeton Plasma Physics Laboratory':'PPPL',
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
'Facilities Finance and Administrative Services':'FACFIN-ADMINSERV',
'Financial Services, Office of the VP for Finance and Treasurer':'FIN-SERVICE',
'French and Italian':'FRENCH-ITALIAN',
'Fusion Simulation Program, Princeton Plasma Physics Laboratory':'PPPL',
'Geosciences':'GEO',
'German':'GERMAN',
'High Meadows Environmental Institute':'HMEI',
'History':'HISTORY',
'History of Science':'HIST-SCI',
'Industrial Relations':'INDUST-REL',
'Information Security Office':'ISO',
'International Economics Section':'ECON',
'ITER and Tokamaks, Princeton Plasma Physics Laboratory':'PPPL',
'Information Technology, Princeton Plasma Physics Laboratory':'PPPL',
'Lewis-Sigler Institute for Integrative Genomics':'LSI',
'Library - Information Technology':'LIBRARY',
'Library - Scholarly Collections and Research Services':'LIBRARY',
'Library - Special Collections':'LIBRARY',
'Library-Data, Research and Teaching Services':'LIBRARY',
'Library - Collections and Access Services':'LIBRARY',
'Library - Deputy University Library':'LIBRARY',
'Library - Office of the Deputy University Librarian':'LIBRARY',
'Music':'MUSIC',
'Mathematics':'MATH',
'McGraw Center for Teaching and Learning':'MCGRAW',
'Mechanical and Aerospace Engineering':'MAE',
'Molecular Biology':'MOLBIO',
'Near Eastern Studies':'NES',
'Office of the Dean for Research':'DEAN-RES',
'Office of the Dean of the College':'DEAN-COL',
'Office of the Dean of the Faculty':'DEAN-FAC',
'Office of the Dean of the Graduate School':'DEAN-GRAD',
'Office of the Dean of Undergraduate Students':'DEAN-UND',
'Office of the Vice Dean for Innovation':'VD-INNOVATION',
'Office of the Vice President for Information Technology':'VP-IT',
'Other Affiliates':'AFFIL',
'Office of the Director, Princeton Plasma Physics Laboratory':'PPPL',
'Operations and Planning, Office of Information Technology':'OIT',
'Operations Research and Financial Engineering':'ORFE',
'Pace Center for Civic Engagement':'PACE',
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
'Princeton Materials Institute':'PMI',
'Princeton Neuroscience Institute':'PNI',
'Princeton School of Public and International Affairs':'SPIA',
'Programs in Access & Opportunity':'ACCESS-OPP',
'Psychology':'PSYCH',
'Religion':'RELIGION',
'Research Computing, Office of Information Technology':'CSES',
'Research Integrity and Assurance':'RES-INTEG-ASSUR',
'Special Student':'SPEC-STUDENT',
'Service Management Office, Office of Information Technology':'OIT',
'Slavic Languages and Literatures':'SLAVIC',
'Sociology':'SOCIO',
'Software and Application Services, Office of Information Technol':'OIT',
'Spanish and Portuguese':'SPANISH-PORT',
'Theory Department, Princeton Plasma Physics Laboratory':'PPPL',
'Tokamak Experimental Sciences, Princeton Plasma Physics Laborato':'PPPL',
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

def get_full_title(lines: list) -> str:
    """Extract full title which may span multiple lines."""
    title = ""
    found_title = False
    for line in lines:
        if "title:" in line:
            title = line.split("title:")[-1].lstrip()
            found_title = True
        if found_title and (":" not in line):
            title += line[1:]
        if found_title and (((":" in line) and (not "title:" in line)) or line == ""):
            return title
    return title

def make_dict(lines: list) -> defaultdict:
    """Make dictionary from a list of strings where a string may contain
       a key-value pair. The values for a given key are stored in a list
       so that multiple values associated with the same key can be stored.
    """
    record = defaultdict(list)
    for line in lines:
        if (":" in line):
            idx = line.find(":")
            field = line[:idx].replace('#', '').strip()
            value = line[idx + 1:].strip()
            if field == "cn" and value.startswith(": "):
               value = b64decode(value).decode("utf-8")
            record[field].append(value)
    record["title"] = [get_full_title(lines)]
    return record

def get_position(netid: str) -> str:
    """Return the position of the individual for the given netid. The netid is
       assumed to be a true netid and not an alias. Otherwise call ldap_plus
       to get position which will deal with the alias.
    """
    try:
        cmd = f"ldapsearch -x uid={netid}"
        output = subprocess.run(cmd, capture_output=True, shell=True, timeout=5)
    except:
        return "NETID_NOT_FOUND"
    lines = output.stdout.decode("utf-8").split('\n')
    if lines != [] and lines[-1] == "": lines = lines[:-1]
    return get_position_from_lines(lines)

def get_position_from_lines(lines: list) -> str:
    """For the given netid, return the position of the individual."""
    dean = False
    faculty = False
    faculty_edu = False
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
    xmiscaffil = False
    rcu = False
    dcu = False
    ru = False
    xdcu = False
    sps = False
    xstf = False
    cas = False
    stp = False
    retired = False
    intern_or_assist = False
    alumg = False
    visitor = False
    sta = False
    for line in lines:
        if line.startswith("#"): continue
        line = line.lower()
        if "dean" in line and "title:" in line: dean = True
        if "professor" in line and "title:" in line: prof_in_title = True
        if "pustatus: fac" in line or "puaffiliation: fac" in line: faculty = True
        if "edupersonaffiliation: faculty" in line: faculty_edu = True
        if "pustatus: xfac" in line or "puaffiliation: xfac" in line: xfaculty = True
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
        if "pustatus: xmiscaffil" in line: xmiscaffil = True
        if "pustatus: alumg" in line: alumg = True
        if "pustatus: cas" in line: cas = True
        if "pustatus: ret" in line: retired = True
        if "pustatus: stp" in line: stp = True
        if "pustatus: shorttermaffiliate" in line: sta = True
        if ("intern" in line or "assist" in line) and "title" in line: intern_or_assist = True

    # cleaning
    if faculty and (postdoc_in_title or lecturer or scholar) and not prof_in_title:
        faculty = False
    if xfaculty and (postdoc_in_title or lecturer or scholar):
        xfaculty = False

    visiting = " (visiting)" if visitor else ""
    former_gx = f" (formerly {Gx.upper()})" if Gx else ""

    other = [rcu, dcu, ru, xdcu, sps, xstf, cas, stp, sta]
    if dean and prof_in_title:
        return "Dean (and Faculty)"
    elif dean:
        return "Dean"
    elif (faculty or faculty_edu) and prof_in_title and not emeritus:
        return f"Faculty{visiting}"
    elif xfaculty and prof_in_title and not emeritus:
        return "XFaculty"
    elif emeritus:
        return "Faculty (emeritus)"
    elif lecturer and postdoc_in_title:
        return f"Postdoc{visiting}{former_gx}"
    elif lecturer and not scholar:
        return f"Lecturer{visiting}{former_gx}"
    elif scholar:
        return f"Scholar{visiting}{former_gx}"
    elif collaborator:
        return f"Collaborator{visiting}{former_gx}"
    elif fellow and not postdoc_in_title:
        return f"Fellow{visiting}{former_gx}"
    elif staff and not postdoc_in_title:
        return f"Staff{visiting}{former_gx}"
    elif staff and postdoc_in_title:
        return f"Postdoc{visiting}{former_gx}"
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
        return f"Graduate{former_gx}"
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
        return f"SPS{visiting}{former_gx}"
    elif xstf:
        return f"XStaff{visiting}{former_gx}"
    elif cas:
        return f"Casual{former_gx}"
    elif stp:
        return f"Short-Term Professional{former_gx}"
    elif sta:
        return f"Short-Term Affiliate{former_gx}"
    elif retired:
        return "Retired"
    elif alumg:
        return f"Alumni{former_gx}"
    elif xmiscaffil:
        return f"XMiscAffil{visiting}{former_gx}"
    elif gradaccept:
        return "G0"
    else:
        return "UNKNOWN"

def clean_position(position: str, level: int=0) -> str:
    """Level 0: No modifications
       Level 1: Remove parenthetical labels such as (visiting)
       Level 2: Level 1 and Gx -> Graduate, U20xx -> Undergrad
       Level 3: Categories are Faculty, Staff, DCU/RCU/RU, Postdoc,
                Graduate, Undergraduate, Retired, G0, UNKNOWN
    """
    if level == 0:
        return position
    elif level == 1:
        return position.split(" (")[0]
    elif level == 2:
        position = position.split(" (")[0]
        if position.startswith("U20"):
            return "Undergrad"
        if position in [f"G{n}" for n in range(1, 10)]:
            return "Graduate"
        return position
    elif level == 3:
        if "XFaculty" in position:
            position = "Faculty"
        if "Alumni (G" in position or "XGraduate" in position:
            position = "Graduate"
        if position in [f"G{n}" for n in range(1, 10)]:
            position = "Graduate"
        staff = ("XStaff", "Casual", "Scholar", "Lecturer", "Collaborator", "Fellow")
        if any([p in position for p in staff]):
            position = "Staff"
        if any([p in position for p in ("DCU", "RCU", "RU", "XDCU")]):
            position = "DCU/RCU/RU"
        if position.startswith("U20") or "Alumni (U" in position or position == "U":
            position = "Undergrad"
        position = position.split(" (")[0]
        return position

def get_dept_code(dept: str, resdept: str, user: str) -> str:
    """Replace full department name with department code."""
    if dept == "Unspecified Department" and resdept in depts:
        return depts[resdept]
    elif dept in depts:
        return depts[dept]
    else:
        print(f"No entry for {dept} or {resdept} in dossier.py for {user}")
        return "NOT_FOUND_IN_DOSSIER_DEPTS"

def ldap_plus(netids: list, level=0) -> list:
    """Take a list of usernames (which may be aliases) and return information about
       each individual from ldap. Here is an example:

           import pandas as pd
           import dossier

           netids = ["aturing", "bill", "sg6615", "halverson"]
           df = pd.DataFrame(dossier.ldap_plus(netids))
           headers = df.iloc[0]
           df = pd.DataFrame(df.values[1:], columns=headers)
           dept = df.DEPT.value_counts().reset_index()
           dept.index += 1
           print(dept.rename(columns={"index":"Dept", "DEPT":"Count"}))
    """
    columns = ['NAME',
               'DEPT',
               'POSITION',
               'TITLE',
               'STATUS',
               'AFFIL',
               'ACAD_LEVEL',
               'NETID',
               'NETID_TRUE']
    people = [columns]
    not_found = 0
    for netid in netids:
        uid_except = False
        try:
            cmd = f"ldapsearch -x uid={netid}"
            output = subprocess.run(cmd, capture_output=True, shell=True, timeout=3)
        except:
            uid_except = True
            uid_success = False
        else:
            lines = output.stdout.decode("utf-8").split('\n')
            record = make_dict(lines)
            uid_success = (record['numResponses'] == [str(2)])

        mail_except = False
        mail_success = False
        if (not uid_success):
            # netid not found so assume it was an alias and search by mail (R. Knight)
            # could also look for multiple occurrences of campusid
            try:
                cmd = f"ldapsearch -x mail={netid}@princeton.edu"
                output = subprocess.run(cmd, capture_output=True, shell=True, timeout=3)
            except:
                mail_except = True
                mail_success = False
            else:
                lines = output.stdout.decode("utf-8").split('\n')
                record = make_dict(lines)
                mail_success = (record['numResponses'] == [str(2)])

        if ((not uid_success) and (not mail_success)):
            # both attempts failed
            people.append([None] * (len(columns) - 2) + [netid, None])
            not_found += 1
        elif (uid_except and mail_except):
            # both commands failed
            people.append([None] * (len(columns) - 2) + [netid, None])
        else:
            # netid_true is the true netid while netid may be an alias
            netid_true = record['uid'][0]
            name = record['cn'][0] if record['cn'] != [] else ""
            dept = record['ou'][0] if record['ou'] != [] else ""
            resdept = record['puresidentdepartment'][0] if record['puresidentdepartment'] != [] else ""
            dept_code = get_dept_code(dept, resdept, netid_true)
            title = record['title'][0] if record['title'] != [] else ""
            pustatus = ", ".join(record["pustatus"])
            puaffiliation = ", ".join(record["puaffiliation"])
            puacademiclevel = ", ".join(record["puacademiclevel"])
            position = get_position_from_lines(lines)
            position = clean_position(position, level)
            people.append([name,
                           dept_code,
                           position,
                           title,
                           pustatus,
                           puaffiliation,
                           puacademiclevel,
                           netid,
                           netid_true])
    if (not_found):
        print(f'Number of netids not found: {not_found}')
    return people
