def printWithTabs(file):
	file = open(file, 'r')
	print(repr(file.read()))
	file.close()