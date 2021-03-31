import os

def getRootDir():
  return os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

def appendDirToRootDir(path):
  return os.path.join(getRootDir(),path,'')

def appendFileToRootDir(file):
  return os.path.join(getRootDir(),file)

def appendDirToDir(dr, path):
  return os.path.join(dr,path,'')

def appendFileToDir(dr, file):
  return os.path.join(dr,file)