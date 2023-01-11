import bpy
import random
import bmesh
import mathutils
import math
from mathutils import Matrix, Vector, Euler
from Modifications.Modification import Modification
import os
from numpy.random import choice

# Shuffles values of a vector propertry using a dict with key = property index and value = randomized value range
# This can be used when a texture is mapped to an object to change the mapping location, rotation and scale

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
            cur_values = nodes[self.node_name].inputs[self.property_name].default_value
            for key, value in self.values.items():
                if type(cur_values) is mathutils.Euler:
                    cur_values[int(key)] = math.radians(random.uniform(int(value[0]), int(value[1])))
                else:
                    cur_values[int(key)] = random.uniform(int(value[0]), int(value[1]))
            nodes[self.node_name].inputs[self.property_name].default_value = cur_values

        except Exception as e: 
            print(e)
            print("Unable to shuffle vector values of ", self.property_name, " for object ",  obj.name, "\n")
