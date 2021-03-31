import os

class Input:
  def __init__(self, conditionTest, casterFn, collectionStr, errStr):
    self.__conditionTest = conditionTest
    self.__casterFn = casterFn
    self.__collectionStr = collectionStr
    self.__errStr = errStr
    self.__collect()
  def __collect(self):
    isValid = False
    userInput = ""
    while not isValid:
      userInput = input(self.__collectionStr)
      if self.__conditionTest(userInput):
        isValid = True
        self.__validData = self.__casterFn(userInput)
      else:
        isValid = False
        print(self.__errStr)
  def get(self):
    return self.__validData

def clear():
    os.system('cls' if os.name=='nt' else 'clear')

def getConsoleLines():
  return os.get_terminal_size().lines

def getConsoleColumns():
  return os.get_terminal_size().columns

# setConsoleSize = Windows Only
def setConsoleSize(lines, columns):
  os.system(f'mode {lines},{columns}')
