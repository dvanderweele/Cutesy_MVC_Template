class Suite:
  def __init__(self, name, tests):
    print(f'Test Suite Name: {name}')
    self.__passes = 0
    self.__fails = 0
    for test in tests:
      print(test[0])
      if test[1]():
        self.__passes += 1
      else:
        self.__fails += 1
    print(f"Tests Passing: {self.__passes}")
    print(f'Tests Failing: {self.__fails}')
    print(f'Percent Passing: {(self.__passes / (self.__passes + self.__fails)) * 100}%')
    if self.__fails == 0:
      self.__status = True
    else:
      self.__status = False
  def allPass(self):
    return self.__status