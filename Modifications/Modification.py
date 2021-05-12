class Modification:
	def __init__(self, objects=[]):
		self.Objects = objects

	def performAction(self):
		for object in self.Objects:
			self.Action(object)

	def Action(self, obj):
		pass

	def performPostProcessing(self):
		for object in self.Objects:
			self.PostProcessing(object)
	
	def PostProcessing(self, obj):
		pass

	def performPreProcessing(self):
		for object in self.Objects:
			self.PreProcessing(object)
	
	def PreProcessing(self, obj):
		pass