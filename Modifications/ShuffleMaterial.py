import bpy
import random
import bmesh
import mathutils
import math
from mathutils.bvhtree import BVHTree
from Modifications.Modification import Modification
import os
from numpy.random import choice


class ShuffleMaterial(Modification):
	def performAction(self):
		for obj in self.Objects:
			self.Action(obj)

# shuffles through object materials 1 to n - 0 is a placeholder and the active material

# Preprocessing: duplicate the material in slot 0 if there is no duplicate already 
# (otherwise it will get overwritten so you'll "lose" a material)

# Action: select and set a random material to position 0
class ShuffleMaterials(ShuffleMaterial):

    def PreProcessing(self, obj):
        try:
            all_materials  = obj.data.materials	
            print(all_materials)		
            if obj.data.materials[0] in all_materials[1:]:
                print(obj.name, ": Placeholder material already set up")

            else:  	
                obj.data.materials.append(obj.data.materials[0])	    
                print(obj.name, ": Inserted new placeholder material")

        except:
            print("Unable to shuffle materials of ", obj.name, "\n The object might have no materials.")


    def Action(self, obj):
        try:
            # these are all materials of this object
            # use 'all_materials = bpy.data.materials' to get all materials in the whole scene
            all_materials  = obj.data.materials				
            random_material = random.choice(all_materials[1:])
            obj.data.materials[0] = random_material
            bpy.context.view_layer.update()
        except:
            print("Unable to shuffle materials of ", obj.name, "\n The object might have no materials.")


### Shuffles given proterty of a specific node of a given material with a float value range
### Each material consists of a number of nodes, for example two RGB Nodes and a Mix Shader
### Different nodes can be accessed with the respective node names, those can be set or viewed through the UI
### Each Node has a list of properties, the Pricipled BSDF node for example has "Metallic", "Specular" and so on
class ShuffleMaterialProperties(ShuffleMaterial):
    def __init__(self,  objects=[], node_name="", property_name="", value_range=[0.0, 1.0], material_name = ""):
        self.node_name  = node_name
        self.property_name = property_name
        self.value_range = value_range
        self.material_name =material_name
        super(ShuffleMaterialProperties, self).__init__(objects)

    def Action(self, obj):
        try:
            if self.material_name != "":
                mat = obj.data.materials[self.material_name] #bpy.data.materials[material_name]
            else:
                mat = obj.data.materials[0]

            nodes = mat.node_tree.nodes

            if self.property_name == "":
                nodes[self.node_name].inputs[0].default_value = random.uniform(self.value_range[0], self.value_range[1])  
            else:
                nodes[self.node_name].inputs[self.property_name].default_value = random.uniform(self.value_range[0], self.value_range[1])                

        except Exception as e: 
            print(e)
            print("Unable to shuffle value of ", self.property_name, " for object ",  obj.name, "\n")
