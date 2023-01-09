import bpy
import random
import bmesh
import mathutils
import math
from mathutils import Matrix, Vector, Euler
from Modifications.Modification import Modification
import os
from numpy.random import choice

"""
class ShuffleMaterial(Modification):
	def performAction(self):
		for obj in self.Objects:
			self.Action(obj)

# shuffles through object materials 1 to n and sets the selected material to position 0
# therefore set a placeholder material to slot 0 and fill all the other slots with the desired materials
class ShuffleMaterials(ShuffleMaterial):
	def Action(self, obj):
		try:
			# these are all materials of this object
			all_materials  = obj.data.materials				# use this to get all materials in the whole scene: all_materials = bpy.data.materials
			random_material = random.choice(all_materials[1:])
			obj.data.materials[0] = random_material
		except:
			print("Unable to shuffle materials of ", obj.name, "\nThe object might have no materials.")

"""

class ShuffleVector(Modification):
    def __init__(self,  objects=[], node_name="", property_name="", values=dict()):
        self.node_name  = node_name
        self.property_name = property_name
        self.values = values
        super(ShuffleVector, self).__init__(objects)

    def Action(self, obj):
        try:
            mat = obj.data.materials[0]
            nodes = mat.node_tree.nodes
            orig_values = nodes[self.node_name].inputs[self.property_name].default_value
            for key, value in self.values.items():
                print(int(key))
                if type(orig_values) is mathutils.Euler:
                    orig_values[int(key)] = math.radians(random.uniform(int(value[0]), int(value[1])))
                    print("rot")
                else:
                    orig_values[int(key)] = random.uniform(int(value[0]), int(value[1]))
                    print("num")
            #nodes[self.node_name].inputs[self.property_name].default_value = random.uniform(self.value_range[0], self.value_range[1])
            #print(obj.name," ", self.property_name, " set to ", nodes[self.node_name].inputs[self.property_name].default_value)

        except Exception as e: 
            print(e)
            print("Unable to shuffle vector values of ", self.property_name, " for object ",  obj.name, "\n")
