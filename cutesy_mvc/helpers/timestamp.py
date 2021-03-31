from datetime import datetime


def getNixTs():
  return datetime.now().timestamp()
  
def nixTsToDateTime(ts):
  return datetime.fromtimestamp(ts)

def hyphenatedTsStr():
  parts = str(datetime.now().timestamp()).split('.')
  return f'{parts[0]}-{parts[1]}'
  
def floatTsFromHyphenFormat(tstring):
  parts = tstring.split('-')
  joined = f'{parts[0]}.{parts[1]}'
  return float(joined)