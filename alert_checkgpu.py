# send an email if there are cases of low utilization

import subprocess

def low_utilization():
  cmd = "/scratch/gpfs/jdh4/gpustat/checkgpu -d 2 -c 10 -g 24"
  output = subprocess.run(cmd, shell=True, capture_output=True)
  lines = output.stdout.decode("utf-8").split('\n')

  if "No results were found" in lines[5]:
    return []
  else:
    cases = []
    skip = ['mcmuniz', 'dongdong']
    lines = lines[8:-3]
    for line in lines:
      parts = line.split()
      user = parts[0]
      util = parts[1]
      std = parts[2]
      hours = parts[3]
      if int(util) == 0 and int(std) == 0:
        cases.append([user, util, std, hours])
      elif user not in skip:
        cases.append([user, util, std, hours])
      else:
        pass
    return cases

if __name__ == '__main__':
  cases = low_utilization()
  if cases:
    SERVER = "localhost"
    FROM = "jdh4@princeton.edu"
    TO = ["halverson@princeton.edu"]
    SUBJECT = "Alert: checkgpu"
    TEXT = "\n".join([" ".join(case) for case in cases])

    # prepare actual message
    message = """\
    From: %s
    To: %s
    Subject: %s

    %s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)

    import smtplib
    server = smtplib.SMTP(SERVER)
    server.sendmail(FROM, TO, message)
    server.quit()
