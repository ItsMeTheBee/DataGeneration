import bpy
import random
import bmesh
import mathutils
import math
from mathutils.bvhtree import BVHTree
from Modifications.Modification import Modification

class ShuffleColor(Modification):
	def performAction(self):
		for obj in self.Objects:
			self.Action(obj)

class ShuffleRGBColor(ShuffleColor):
	def Action(self, obj):
		mat = obj.data.materials[0]
		nodes = mat.node_tree.nodes
		principled = nodes.get("Principled BSDF")
		principled.inputs[0].default_value = self.get_random_color()
		bpy.context.scene.update()

	def get_random_color(self):
		r, g, b = [random.random() for i in range(3)]
		return r, g, b, 1

# shuffles through object materials 1 to n and sets the selected material to position 0
# therefore set a placeholder material to slot 0 and fill all the other slots with the desired materials
class ShuffleMaterial(ShuffleColor):
	def Action(self, obj):
		try:
			# these are all materials of this object
			all_materials  = obj.data.materials				# use this to get all materials in the whole scene: all_materials = bpy.data.materials
			random_material = random.choice(all_materials[1:])
			obj.data.materials[0] = random_material
		except:
			print("Unable to shuffle materials of ", obj.name, "\nThe object might have no materials.")
