import bpy
import random
import bmesh
from Modifications.Modification import Modification
import os
import colorsys
from numpy.random import choice
from mathutils import Color
from . import Utils


class ShuffleColor(Modification):
	def performAction(self):
		for obj in self.Objects:
			self.Action(obj)


### Randomly choose colors in the rbg or hsv color space
class ShuffleRGBColor(ShuffleColor):
	def __init__(self,  objects=[], node_name = "Principled BSDF", property_name = "Base Color", val_1 = [0.0, 1.0], val_2 = [0.0, 1.0], val_3 = [0.0, 1.0], mode = "rgb", material_name = ""):
		self.node_name  = node_name
		self.val1_range = val_1
		self.val2_range = val_2
		self.val3_range = val_3
		self.mode = mode
		self.node_name = node_name
		self.property_name = property_name
		self.material_name = material_name
		super(ShuffleRGBColor, self).__init__(objects)

	def Action(self, obj):
		if self.material_name != "":
			mat = obj.data.materials[self.material_name] #bpy.data.materials[material_name]
		else:
			print(obj.name, " no material name! - defaulting to material in slot 0")
			mat = obj.data.materials[0]
		nodes = mat.node_tree.nodes

		val1 = random.uniform(self.val1_range[0], self.val1_range[1])
		val2 = random.uniform(self.val2_range[0], self.val2_range[1])
		val3 = random.uniform(self.val3_range[0], self.val3_range[1])

		if self.property_name == "":
			if self.mode == "rgb":
				nodes.get(self.node_name).inputs[0].default_value = Utils.srgb2lin(val1), Utils.srgb2lin(val2), Utils.srgb2lin(val3), 1
			if self.mode == "hsv":
				col = colorsys.hsv_to_rgb(val1, val2, val3)
				nodes.get(self.node_name).inputs[0].default_value = Utils.srgb2lin(col[0]), Utils.srgb2lin(col[1]), Utils.srgb2lin(col[2]), 1
			else:
				print("Mode unknown - unable to shuffle color")

		else:
			if self.mode == "rgb":
				nodes.get(self.node_name).inputs[self.property_name].default_value = Utils.srgb2lin(val1), Utils.srgb2lin(val2), Utils.srgb2lin(val3), 1
			if self.mode == "hsv":
				col = colorsys.hsv_to_rgb(val1, val2, val3)
				nodes.get(self.node_name).inputs[self.property_name].default_value = Utils.srgb2lin(col[0]), Utils.srgb2lin(col[1]), Utils.srgb2lin(col[2]), 1
			else:
				print("Mode unknown - unable to shuffle color")
		bpy.context.view_layer.update()

	def get_random_color(self,val_1 , val_2, val_3 ):
		first = random.uniform(val_1[0], val_1[1])
		sec = random.uniform(val_2[0], val_2[1])
		third = random.uniform(val_3[0], val_3[1])
		return first, sec, third


### Randomly set an HDRI background from the given folder image_paths
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

### Shuffle the color space of an image texture
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

### Shuffle image textures using a given folder image_paths
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
