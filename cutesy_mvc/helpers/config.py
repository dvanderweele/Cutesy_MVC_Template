from ..configuration import options

def drill(obj, key):
  return obj[key]

def get(target):
  current = options
  elements = target.split('.')
  while len(elements) > 0:
    current = drill(current, elements[0])
    del elements[0]
  return current