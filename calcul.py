class DictionnarySparseMatrix:
	def __init__(self):
		self.elements = {}

	def addValue(self, tuple, value):
		self.elements[tuple] = value

	def deleteValue(self, tuple):
		value = self.elements.pop(tuple, None)
		return value

	def readValue(self, tuple):
		try:
			value = self.elements[tuple]
		except KeyError:
			# could also be 0.0 if using floats...
			value = None
		return value

	def readDict(self):
		return self.elements

sparse = DictionnarySparseMatrix()
sparse.addValue((1, 2, 3), 15.7)
print(sparse.readValue((1, 2, 3)))
