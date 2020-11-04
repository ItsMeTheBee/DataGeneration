import bpy, os
from math import sin, cos, pi
import numpy as np
import sys
import random
from datetime import datetime
import toml

base_dir = os.path.dirname(bpy.data.filepath)
dir = base_dir

if not dir in sys.path:
    sys.path.append(dir)

import boundingBox
import checkVisibility
from Modifications.ShufflePos import ShuffleXPos, ShuffleYPos, ShuffleZPos
from Modifications.ShuffleRot import ShuffleXRot, ShuffleYRot, ShuffleZRot
from Modifications.ShuffleColor import ShuffleRGBColor, ShuffleBackground, ShuffleImageTexture, ShuffleColorSpace
from Modifications.MaskBlackNWhite import MaskBlackNWhite
from Modifications.RandomMods import RandomDisappear
from Modifications.CameraMods import ShuffleFocalLength
from Modifications.ShuffleMaterial import ShuffleMaterials, ShuffleMaterialProperties

## Global variables cause things are getting messy 
config = toml.load("/home/vision/atWork/DataGen/DataGenBBoxes/configTableDecoy.toml")

# ____________________________________________ Create image

def render(scene, camera_object, mesh_objects, file_prefix="render", folder="renders"):
	# Rendering
	# https://blender.stackexchange.com/questions/1101/blender-rendering-automation-build-script
	filename = str(file_prefix)
	bpy.context.scene.render.filepath = os.path.join(base_dir+ "/" + folder + "/", filename + '.png')
	bpy.ops.render.render(write_still=True)

# ____________________________________________ Create labels

def createYoloTxtFile(scene, camera_object, mesh_objects, config, file_prefix="render", bounds=None):
	#names_to_labels = { 'Cube': 0, 'Cube.001': 1, 'Cube.002': 2, 'Cube.003': 3, 'Cube.004': 4}
	#print("Creating labels")
	random.shuffle(mesh_objects)
	filename = str(file_prefix)
	path = os.path.join(base_dir+'/labels/', filename + '.txt')
	checkVisibility.prepare_visibility_check(scene, camera_object)
	with open(path, 'w+') as file:
		""" Get the bounding box coordinates for each mesh """
		for object in mesh_objects:
			print("labeling ", object.name)
			if object.hide_render == True:
				"""for child in object.children:
							child.hide_render = True
				object.parent.hide_render = True"""
				print(object.name + " is hidden - not labeling this!")
				continue
			name = config['Labels'][object.name]
			if checkVisibility.check_visibility(scene, camera_object, object) < config[object.name]["visibility_thresh"]:
				print(object.name, "visibilitiy is ", checkVisibility.check_visibility(scene, camera_object, object), " -> not visible in render - HIDING this!")
				object.hide_render = True
				continue
			bounding_box = boundingBox.camera_view_bounds_2d(scene, camera_object, object, bounds)
			if bounding_box:
				new_line = str(name) + " " + str(bounding_box[0])+ " " + str(bounding_box[1]) + " " + str(bounding_box[2]) + " " + str(bounding_box[3]) + '\n'
				file.write(new_line)
			else: 
				object.hide_render = True
				print("Hiding ", object.name)


# ____________________________________________ Create Modifications

def createCameraMods(camera):
	mods = list()
	cameras = list()
	cameras.append(camera)
	#modFocalLength = ShuffleFocalLength([11, 38], cameras)
	#mods.append(modFocalLength)
	modZRot = ShuffleZRot([0, 360], cameras, False)
	mods.append(modZRot)
	modXRot = ShuffleXRot([60, 110], cameras, False)
	mods.append(modXRot)
	modYRot = ShuffleYRot([-20, 20], cameras, False)
	mods.append(modYRot)
	return mods

def createLightMods(lights):
	mods = list()
	modXPos = ShuffleXPos([-200, 200], lights, False)
	mods.append(modXPos)
	modYPos = ShuffleYPos([-200, 200], lights, False)
	mods.append(modYPos)
	return mods

def createDecoyMods(decoy):
	mods = list()
	modXPos = ShuffleXPos([-40, 40], decoy, False, True)
	mods.append(modXPos)
	modYPos = ShuffleYPos([-80, 10], decoy, False, True)
	mods.append(modYPos)
	modZPos = ShuffleZPos([-40, -80], decoy, False, True)
	mods.append(modZPos)
	modXRot = ShuffleXRot([-25, 25], decoy, True, True)
	mods.append(modXRot)
	modYRot = ShuffleYRot([-25, 25], decoy, True, True)
	mods.append(modYRot)
	modZRot = ShuffleZRot([-25, 25], decoy, True, True)
	mods.append(modZRot)

	modDisappear = RandomDisappear(decoy, 0.3)
	mods.append(modDisappear)
	return mods

def createSpecialObjectMods(special):
	mods = list()
	modZRot = ShuffleZRot([0, 360], special, False)
	mods.append(modZRot)

	modDisappear = RandomDisappear(special, 0.3)
	mods.append(modDisappear)

	#mods.append(modZPos)
	for obj in special:
			obj_list = list()
			obj_list.append(obj)
			
			modMetallic = ShuffleMaterialProperties(obj_list, "Principled BSDF", "Metallic", config[obj.name]["PrincipledBSDF"]["Metallic"])
			mods.append(modMetallic)

			modSpecular = ShuffleMaterialProperties(obj_list, "Principled BSDF", "Specular", config[obj.name]["PrincipledBSDF"]["Specular"])
			mods.append(modSpecular)

			modSpecularTint = ShuffleMaterialProperties(obj_list, "Principled BSDF", "Specular Tint", config[obj.name]["PrincipledBSDF"]["SpecularTint"])
			mods.append(modSpecularTint)

			modRoughness = ShuffleMaterialProperties(obj_list, "Principled BSDF", "Roughness", config[obj.name]["PrincipledBSDF"]["Roughness"])
			mods.append(modRoughness)

			modAnisotropic = ShuffleMaterialProperties(obj_list, "Principled BSDF", "Anisotropic", config[obj.name]["PrincipledBSDF"]["Anisotropic"])
			mods.append(modAnisotropic)

			modAnisotropicRotation = ShuffleMaterialProperties(obj_list, "Principled BSDF", "Anisotropic Rotation", config[obj.name]["PrincipledBSDF"]["AnisotropicRotation"])
			mods.append(modAnisotropicRotation)

			modClearcoat = ShuffleMaterialProperties(obj_list, "Principled BSDF", "Clearcoat", config[obj.name]["PrincipledBSDF"]["Clearcoat"])
			mods.append(modClearcoat)

			modClearcoatRoughness = ShuffleMaterialProperties(obj_list, "Principled BSDF", "Clearcoat Roughness", config[obj.name]["PrincipledBSDF"]["ClearcoatRoughness"])
			mods.append(modClearcoatRoughness)
			if "Color" in config[obj.name]:
				color_config  = config[obj.name]["Color"]
				modShuffleColor = ShuffleRGBColor(obj_list, color_config["NodeName"], color_config["PropertyName"], color_config["value1"],color_config["value2"],color_config["value3"], color_config["mode"])
				mods.append(modShuffleColor)
			else:
				print("no color config for ", obj.name)

	
	return mods

def createObjectMods(objects):
	mods = list()
	modZRot = ShuffleZRot([0, 360], objects, False)
	mods.append(modZRot)
	modYRot = ShuffleYRot([-20, 20], objects, False)
	mods.append(modYRot)
	modXRot = ShuffleXRot([-20, 20], objects, False)
	mods.append(modXRot)
	modXPos = ShuffleXPos([-30, 30], objects, True, True)
	mods.append(modXPos)
	modYPos = ShuffleYPos([-20, 20], objects, True, True)
	mods.append(modYPos)
	modZPos = ShuffleZPos([-40, -70], objects, True, True)
	mods.append(modZPos)
	for obj in objects:
			obj_list = list()
			obj_list.append(obj)
			
			modMetallic = ShuffleMaterialProperties(obj_list, "Principled BSDF", "Metallic", config[obj.name]["PrincipledBSDF"]["Metallic"])
			mods.append(modMetallic)

			modSpecular = ShuffleMaterialProperties(obj_list, "Principled BSDF", "Specular", config[obj.name]["PrincipledBSDF"]["Specular"])
			mods.append(modSpecular)

			modSpecularTint = ShuffleMaterialProperties(obj_list, "Principled BSDF", "Specular Tint", config[obj.name]["PrincipledBSDF"]["SpecularTint"])
			mods.append(modSpecularTint)

			modRoughness = ShuffleMaterialProperties(obj_list, "Principled BSDF", "Roughness", config[obj.name]["PrincipledBSDF"]["Roughness"])
			mods.append(modRoughness)

			modAnisotropic = ShuffleMaterialProperties(obj_list, "Principled BSDF", "Anisotropic", config[obj.name]["PrincipledBSDF"]["Anisotropic"])
			mods.append(modAnisotropic)

			modAnisotropicRotation = ShuffleMaterialProperties(obj_list, "Principled BSDF", "Anisotropic Rotation", config[obj.name]["PrincipledBSDF"]["AnisotropicRotation"])
			mods.append(modAnisotropicRotation)

			modClearcoat = ShuffleMaterialProperties(obj_list, "Principled BSDF", "Clearcoat", config[obj.name]["PrincipledBSDF"]["Clearcoat"])
			mods.append(modClearcoat)

			modClearcoatRoughness = ShuffleMaterialProperties(obj_list, "Principled BSDF", "Clearcoat Roughness", config[obj.name]["PrincipledBSDF"]["ClearcoatRoughness"])
			mods.append(modClearcoatRoughness)
			if "Color" in config[obj.name]:
				color_config  = config[obj.name]["Color"]
				modShuffleColor = ShuffleRGBColor(obj_list, color_config["NodeName"], color_config["PropertyName"], color_config["value1"],color_config["value2"],color_config["value3"], color_config["mode"])
				mods.append(modShuffleColor)
			else:
				print("no color config for ", obj.name)

	
	return mods

def createWorldMods():
	world_obj= list()
	world_mods= list()
	if config['General']['ShuffleWorld']:
		world_obj.append(bpy.context.scene.world)
		world_mods.append(ShuffleBackground(world_obj, config['World']['Backgrounds'], True, shuffle_strength=[0.4, 1]))
	return world_mods

def createMods(camera, lamp, objects, special, decoy):
	mods = list()
	mods.extend(createWorldMods())
	mods.extend(createCameraMods(camera))
	mods.extend(createLightMods(lamp))
	mods.extend(createObjectMods(objects))
	mods.extend(createSpecialObjectMods(special))
	mods.extend(createDecoyMods(decoy))
	return mods

# ____________________________________________ Apply every modification and create image + labels

def batch_render(scene, camera, lamp, objects, special,decoy, steps, config, bounds):
	mods = createMods(camera, lamp, objects, special, decoy)
	for k in range(1, steps+1):
		print("Starting image no.", k)
		for mod in mods:
			mod.performAction()
		print("Performed mods - labeling")
		file_prefix=datetime.now().strftime('%Y-%m-%d-%H-%M-%S-%f')[:-3]
		createYoloTxtFile(scene, camera, objects, config, file_prefix, bounds)
		print("Created label - rendering")
		render(scene, camera, objects, file_prefix)
		print(k, " of ", steps, " done.")
	print("DONE! =)")

# ____________________________________________ Loop through each frame and create image + labels 

def path_render(scene, camera, objects, steps, config, bounds):
	worldMods = createWorldMods()
	for i in range(scene.frame_start,scene.frame_end):
		if i > steps:
			print("done - reached desired image count")
			return

		for worldMod in worldMods:
			worldMod.performAction()

		scene.frame_current = i
		file_prefix=datetime.now().strftime('%Y-%m-%d-%H-%M-%S-%f')[:-3]
		render(scene, camera, objects, file_prefix)
		createYoloTxtFile(scene, camera, objects, config, file_prefix, bounds)
	print("done - no frames left to render")

def mask_render(scene, camera, objects, steps, mod):
	worldMods = createWorldMods()
	print("rendering original images" )
	for i in range(scene.frame_start,scene.frame_end):
		if i > steps:
			print("done - reached desired image count")
			break

		for worldMod in worldMods:
			worldMod.performAction()

		scene.frame_current = i
		file_prefix=i
		render(scene, camera, objects, file_prefix)

	scene.frame_current = 0
	mod.performAction()

	print("rendering masked images" )
	for j in range(scene.frame_start,scene.frame_end):
		if j > steps:
			print("done - reached desired image count")
			break
		scene.frame_current = j
		file_prefix=j
		render(scene, camera, objects, file_prefix, "labels")

	print("done - no frames left to render")
	scene.frame_current = 0
	mod.restoreColor()

def load_objects(names, ignore_names=None, category=""):
	mesh_obj=list()
	if ignore_names != "" and ignore_names is not None:
		available = [obj.name for obj in bpy.data.objects]
		mesh_names = [x for x in available if x not in ignore_names]

	elif names is not None:
		mesh_names = names

	else:
		print("Unable to load ", category)
		return mesh_obj
	try:
		mesh_objects = [bpy.data.objects[name] for name in mesh_names]
		for mesh in mesh_objects:
			mesh_obj.append(mesh)
	except:
		print("Error loading objects")
	return mesh_obj


def test(obj):
	test_mod = ShuffleBackground(obj)
	test_mod.performAction()

# ____________________________________________ Read config values & Load objects

def main():
	bpy.context.view_layer.update()
	scene = bpy.data.scenes[config['General']['Scene']]
	camera_object = bpy.data.objects[config['General']['Camera']]
	mode = config['General']['Mode']
	print("MODE: ",mode)
	steps = config['General']['Steps']
	bounds = config['General']['Boundaries']
	print("BOUNDARIES ARE ",bounds)		

	lamp_obj = list()
	special_obj = list()
	mesh_obj = list()

	lamp_obj = load_objects(config['Objects']['Lamps'], category="Lamps")
	mesh_obj = load_objects(config['Objects']['Names'], config['Objects']['Ignore'], "Objects")
	special_obj = load_objects(config['Objects']['Special'], category="Special")
	decoy_obj = load_objects(config['Objects']['Decoy'], category="Decoy")

	if mode != "Mask":
		if mode == "Mods":	 
			batch_render(scene, camera_object, lamp_obj, mesh_obj, special_obj,decoy_obj, int(steps), config, bounds)
			return

		if mode == "Path":
			path_render(scene, camera_object, mesh_obj, int(steps), config, bounds)
			return

	if mode == "Mask":
		mask_true_obj = list()
		mask_false_obj = list()

		mask_true_obj = load_objects(config['Mask']['Mask_True_Objects'], category="Mask True Objects")
		mask_false_obj = load_objects(config['Mask']['Mask_False_Objects'], category="Mask False Objects")

		mask_true_material = config['Mask']['Mask_True_Mat']
		mask_false_material = config['Mask']['Mask_False_Mat']

		mask_false_color = config['Mask']['Mask_False_Color']
		#mask_false_color = list(map(int, mask_false_color))

		mask_true_color = config['Mask']['Mask_True_Color']
		#mask_true_color = list(map(int, mask_true_color))

		maskMod = MaskBlackNWhite(mask_true_obj, mask_false_obj, mask_true_color, mask_false_color, mask_true_material, mask_false_material)
		mask_render(scene, camera_object, mesh_obj, int(steps), maskMod)
		return

	else:
		print("Please select an available Mode")


if __name__ == '__main__':
	main()

