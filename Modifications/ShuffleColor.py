import bpy
import random
import bmesh
import mathutils
import math
from mathutils.bvhtree import BVHTree
from Modifications.Modification import Modification
import os
import colorsys
from numpy.random import choice
from mathutils import Color

def srgb2lin(s):
    if s <= 0.0404482362771082:
        lin = s / 12.92
    else:
        lin = pow(((s + 0.055) / 1.055), 2.4)
    return lin


def lin2srgb(lin):
    if lin > 0.0031308:
        s = 1.055 * (pow(lin, (1.0 / 2.4))) - 0.055
    else:
        s = 12.92 * lin
    return s


class ShuffleColor(Modification):
	def performAction(self):
		for obj in self.Objects:
			self.Action(obj)

class ShuffleRGBColor(ShuffleColor):
	def __init__(self,  objects=[], node_name = "Principled BSDF", property_name = "Base Color", val_1 = [0.0, 1.0], val_2 = [0.0, 1.0], val_3 = [0.0, 1.0], mode = "rgb"):
		self.node_name  = node_name
		self.val1_range = val_1
		self.val2_range = val_2
		self.val3_range = val_3
		self.mode = mode
		self.node_name = node_name
		self.property_name = property_name
		super(ShuffleRGBColor, self).__init__(objects)

	def Action(self, obj):
		mat = obj.data.materials[0]
		nodes = mat.node_tree.nodes
		val1 = random.uniform(self.val1_range[0], self.val1_range[1])
		val2 = random.uniform(self.val2_range[0], self.val2_range[1])
		val3 = random.uniform(self.val3_range[0], self.val3_range[1])
		if self.mode == "rgb":
			nodes.get(self.node_name).inputs[self.property_name].default_value = srgb2lin(val1), srgb2lin(val2), srgb2lin(val3), 1
		if self.mode == "hsv":
			col = colorsys.hsv_to_rgb(val1, val2, val3)
			nodes.get(self.node_name).inputs[self.property_name].default_value = srgb2lin(col[0]), srgb2lin(col[1]), srgb2lin(col[2]), 1
		else:
			print("Mode unknown - unable to shuffle color")
		bpy.context.view_layer.update()

	def get_random_color(self,val_1 , val_2, val_3 ):
		first = random.uniform(val_1[0], val_1[1])
		sec = random.uniform(val_2[0], val_2[1])
		third = random.uniform(val_3[0], val_3[1])
		return first, sec, third

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

# shuffles through object materials 1 to n and sets the selected material to position 0
# therefore set a placeholder material to slot 0 and fill all the other slots with the desired materials
class ShuffleBackground(Modification):
	def __init__(self,  objects=[], image_paths=[], folder=False, shuffle_strength=[0.1, 1]):
		self.paths  = image_paths
		self.is_folder = folder
		self.shuffle_strength = shuffle_strength
		if self.is_folder:
				folder = self.paths
				self.paths = list()
				paths = os.listdir(folder)
				for path in paths:
					self.paths.append(folder+path)
		super(ShuffleBackground, self).__init__(objects)

	def Action(self, obj):
		try:
			nodes = obj.node_tree.nodes
			env = nodes.get("Environment Texture")
			path = random.choice(self.paths)
			env.image = bpy.data.images.load(path)
			if self.shuffle_strength:
				strength = round(random.uniform(self.shuffle_strength[0], self.shuffle_strength[1]), 2)
				background = nodes.get("Background")
				background.inputs[1].default_value = strength
				print("Set background strength to ", strength)

		except:
			print("Unable to shuffle environment texture of ", obj.name, "\n Please check the path in your conig file")

class ShuffleColorSpace(Modification):
	def __init__(self,  objects=[], node_name="Image Texture", modes=["sRGB"], probablilty=0.5):
		self.node_name  = node_name
		self.modes = modes
		self.probability = probablilty
		super(ShuffleColorSpace, self).__init__(objects)

	def Action(self, obj):
		try:
			chance = choice([0,1], 1,replace=False, p=[1-self.probability, self.probability] )
			if chance:
				mat = obj.data.materials[0]
				nodes = mat.node_tree.nodes
				env = nodes.get(self.node_name)
				env.image.colorspace_settings.name = random.choice(self.modes)

		except Exception as e: 
			print(e)
			print("Unable to shuffle color space of ", obj.name, "\n")


class ShuffleImageTexture(Modification):
	def __init__(self,  objects=[], image_paths=[], folder=False):
		self.paths  = image_paths
		self.is_folder = folder
		if self.is_folder:
				folder = self.paths
				self.paths = list()
				paths = os.listdir(folder)
				for path in paths:
					self.paths.append(folder+path)
		super(ShuffleImageTexture, self).__init__(objects)

	def Action(self, obj):
		try:
			mat = obj.data.materials[0]
			nodes = mat.node_tree.nodes
			env = nodes.get("Image Texture")
			path = random.choice(self.paths)
			env.image = bpy.data.images.load(path)
			env.image.colorspace_settings.name = 'Filmic Log'

		except Exception as e: 
			print(e)
			print("Unable to shuffle image texture of ", obj.name, "\n Please check the path in your conig file")
