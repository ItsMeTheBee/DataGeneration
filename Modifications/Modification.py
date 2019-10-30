class Modification:
	def __init__(self, objects=[]):
		self.Objects = objects

	def performAction(self):
		for object in self.Objects:
			self.Action(object)

	def Action(self, obj):
		pass