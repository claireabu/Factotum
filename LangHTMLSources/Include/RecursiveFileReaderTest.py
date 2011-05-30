from RecursiveFileReader import RecursiveFileReader


f = RecursiveFileReader("test1.txt")
line = f.readline()
while(line):
	if line.startswith("#include"):
		f.include(line.split(' ',1)[1].strip())
		line = f.readline()
	print line.rstrip()
	line = f.readline()

