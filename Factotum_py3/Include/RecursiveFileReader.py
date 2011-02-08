

class RecursiveFileReaderException(Exception): pass

class RecursiveFileReader:

	def __init__(self,filename,parent=None):
		self.filename = filename
		self.parent = parent
		self.position = 0
		self.f = None
		self.includeFileReader = None
		self.f = open(self.filename)

	def readline(self):
		if self.includeFileReader != None:
			result = self.includeFileReader.readline()
			if result != "":
				return result
			self.includeFileReader.close()
			self.includeFileReader = None
			self.f = open(self.filename)
			self.f.seek(self.position)

		result = self.f.readline()
		if result == "":
			self.f.close()
		return result

	def include(self,includeFileName):
		if self.includeFileReader != None:
			return self.includeFileReader.include(includeFileName)
		self._checkForRecursionLoop(includeFileName)
		self.position = self.f.tell()
		self.f.close()
		self.includeFileReader = RecursiveFileReader(includeFileName,self)

	def close(self):
		self.f.close()

	def _checkForRecursionLoop(self,filename):
		if filename == self.filename:
			raise RecursiveFileReaderException("Recursion loop detected. File: %s" % (filename,))
		if self.parent != None:
			self.parent._checkForRecursionLoop(filename)




		
			

	