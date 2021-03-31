from ..helpers import config
from ..helpers import path

class File:
  def __init__(self, disk = "default"):
    self.__disk = config.get('disks.'+disk)
    self.__file = None
  def __buildTarget(self, filename):
    disk = path.appendDirToRootDir(self.__disk)
    target = path.appendFileToDir(disk,filename)
    return target
  def disk(self, target):
    self.__disk = target
    return self
  def get(self, filename):
    target = self.__buildTarget(filename)
    self.__file = open(target, 'r')
    result = self.__file.read()
    self.__file.close()
    return result
  def put(self, filename, contents):
    target = self.__buildTarget(filename)
    self.__file = open(target, 'w')
    self.__file.write(contents)
    self.__file.close()
  def prependContent(self, filename, content):
    contents = self.get(filename)
    target = self.__buildTarget(filename)
    self.__file = open(target, 'w')
    self.__file.write(content)
    self.__file.write(contents)
    self.__file.close()
  def appendContent(self, filename, content):
    target = self.__buildTarget(filename)
    self.__file = open(target, "a")
    self.__file.write(content)
    self.__file.close()
  def getLines(self, filename):
    target = self.__buildTarget(filename)
    self.__file = open(target, "r")
    results = []
    for ln in self.__file:
      ln != "\n" and results.append(ln.rstrip('\n'))
    self.__file.close()
    return results