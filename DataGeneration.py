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
from Modifications.Mask import Mask, MaskComposition
from Modifications.RandomMods import RandomDisappear
from Modifications.CameraMods import ShuffleFocalLength
from Modifications.ShuffleMaterial import ShuffleMaterials, ShuffleMaterialProperties
from Modifications.MeshMods import CreateHull

## Global variables cause things are getting messy 
config = toml.load("/mnt/Storage/work/DataGen/DataGeneration/config.toml")

def calcVisibilityThresh(obj, config):
	visibility_thresh = config[obj.name]["visibility_thresh_factor"]
	factor = obj.location.z / 2 + visibility_thresh
	return min(factor, 0.8)

# ____________________________________________ Create image

def render(scene, camera_object, mesh_objects, file_prefix="render", folder=None):
	# Rendering
	# https://blender.stackexchange.com/questions/1101/blender-rendering-automation-build-script
	if folder:
		folder = "renders/" + str(folder)
	else:
		 folder = "renders"
	filename = str(file_prefix)
	bpy.context.scene.render.filepath = os.path.join(base_dir+ "/" + folder + "/", filename + '.png')
	bpy.ops.render.render(write_still=True)

# ____________________________________________ Create labels

def createYoloTxtFile(scene, camera_object, visibility_camera, mesh_objects, config, file_prefix="label", folder=None, bounds=None):
	random.shuffle(mesh_objects)
	filename = str(file_prefix)
	if folder:
		folder = "labels/" + str(folder)
	else:
		 folder = "labels"
	path = os.path.join(base_dir+ "/" + folder + "/", filename + '.txt')
	with open(path, 'w+') as file:
		""" Get the bounding box coordinates for each mesh """
		for object in mesh_objects:
			if not object.name in config['Labels']:
				print(object.name + " has no label - not labeling this!")
				continue

			if object.hide_render == True:
				print(object.name + " is hidden - not labeling this!")
				continue
			
			name = config['Labels'][object.name]
			checkVisibility.select_camera_view(scene, visibility_camera, object)
			visibility = checkVisibility.check_visibility(scene, visibility_camera, object)
			checkVisibility.restore_camera(scene, camera_object)

			if visibility < calcVisibilityThresh(object, config):
				print(object.name, "visibilitiy is ", visibility, " -> not visible in render - HIDING this!")
				object.hide_render = True
				continue

			bounding_box = boundingBox.camera_view_bounds_2d(scene, camera_object, object, bounds)
			if bounding_box:
				new_line = str(name) + " " + str(bounding_box[0])+ " " + str(bounding_box[1]) + " " + str(bounding_box[2]) + " " + str(bounding_box[3]) + '\n'
				file.write(new_line)

			else: 
				object.hide_render = True
				print("Hiding ", object.name)


# ____________________________________________ Create Modification

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

def createObjectMods(objects):
	mods = list()
	for obj in objects:
			obj_list = list()
			obj_list.append(obj)

			if "Rotation" in config[obj.name]:
				if "Z" in config[obj.name]["Rotation"]:
					modZRot = ShuffleZRot(config[obj.name]["Rotation"]["Z"], obj_list, False)
					mods.append(modZRot)

				if "Y" in config[obj.name]["Rotation"]:
					modYRot = ShuffleYRot(config[obj.name]["Rotation"]["Y"], obj_list, False)
					mods.append(modYRot)

				if "X" in config[obj.name]["Rotation"]:
					modXRot = ShuffleXRot(config[obj.name]["Rotation"]["X"], obj_list, False)
					mods.append(modXRot)

			if "Position" in config[obj.name]:
				if "Z" in config[obj.name]["Position"]:
					modZPos = ShuffleZPos(config[obj.name]["Position"]["Z"], obj_list, False, False)
					mods.append(modZPos)

				if "Y" in config[obj.name]["Position"]:
					modYPos = ShuffleYPos(config[obj.name]["Position"]["Y"], obj_list, False, False)
					mods.append(modYPos)

				if "X" in config[obj.name]["Position"]:
					modXPos = ShuffleXPos(config[obj.name]["Position"]["X"], obj_list, False, False)
					mods.append(modXPos)
			
			if "PrincipledBSDF" in config[obj.name]:
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

	
def createMaskMods(objects, folder):
	mods = list()

	index_dict = {}
	for obj in objects:
			print(obj.name, " ID ", config[obj.name]["id"])
			index_dict[obj.name] = config[obj.name]["id"]
	
	if folder:
		folder = "labels/" + str(folder)
	else:
		 folder = "labels"
	modMask = MaskComposition(objects, index_dict, base_path = "/mnt/Storage/work/DataGen/DataGeneration/", folder = folder)
	mods.append(modMask)
	return mods

def createWorldMods():
	world_obj= list()
	world_mods= list()
	if config['General']['ShuffleWorld']:
		world_obj.append(bpy.context.scene.world)
		world_mods.append(ShuffleBackground(world_obj, config['World']['Backgrounds'], True, shuffle_strength=[0.4, 1]))
	return world_mods

def createMods(camera, lamp, objects):
	mods = list()
	mods.extend(createWorldMods())
	mods.extend(createCameraMods(camera))
	mods.extend(createLightMods(lamp))
	mods.extend(createObjectMods(objects))
	return mods

# ____________________________________________ Apply every modification and create image + labels

def batch_render(scene, camera, visibility_camera_object, lamp, objects, steps, config, bounds, folder=None, label = False, mask = False, path = False):
	mods = createMods(camera, lamp, objects)
	maskMods = list()

	if mask:
		maskMods = createMaskMods(objects, folder)
		for maskMod in maskMods:
			maskMod.performPreProcessing()
	
	available_steps = range(1, steps+1)
	if path:
		available_steps = range(scene.frame_start,scene.frame_end)

	for k in available_steps:
		print("Starting image no.", k)

		if path: 
			scene.frame_current = i

		for mod in mods:
			mod.performAction()

		file_prefix=datetime.now().strftime('%Y-%m-%d-%H-%M-%S-%f')[:-3]

		if mask:
			for maskMod in maskMods:
				maskMod.performAction(file_prefix)        
				render(scene, camera, objects, file_prefix, folder)

		if label:
			createYoloTxtFile(scene, camera, visibility_camera_object, objects, config, file_prefix, folder, bounds)
			# dont render the image again if it was already created with the segmentation mask composition
			if not mask:
				render(scene, camera, objects, file_prefix, folder)

		if mask:
			for maskMod in maskMods:
				maskMod.performPostProcessing()

		print(k, " of ", steps, " done.")

	print("DONE! =)")


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
		print("Error loading objects of ", category)
	return mesh_obj

# ____________________________________________ Helper methods

def hideAllObjects(Objs):
	for obj in Objs:
		obj.hide_render = True


# ____________________________________________ Read config values & Load objects

def main():
	bpy.context.view_layer.update()
	scene = bpy.data.scenes[config['General']['Scene']]
	camera_object = bpy.data.objects[config['General']['Camera']]
	visibility_camera_object = bpy.data.objects[config['General']['Visibility_Check']]
	steps = config['General']['Steps']
	if 'Boundaries' in config['General']:
		bounds = config['General']['Boundaries']
	else:
		bounds = None
	print("BOUNDARIES ARE ",bounds)		

	lamp_obj = list()
	mesh_obj = list()

	lamp_obj = load_objects(config['Objects']['Lamps'], category="Lamps")
	mesh_obj = load_objects(config['Objects']['Names'], config['Objects']['Ignore'], "Objects")

	#scene, camera, lamp, objects, steps, config, bounds, folder = None, label = False, mask = False, path = False

	if config['General']['SingleObjects']:
		for obj in mesh_obj:
			hideAllObjects(mesh_obj)
			current_obj = list()
			current_obj.append(obj)
			batch_render(scene, camera_object, visibility_camera_object,lamp_obj, current_obj, int(steps), config, bounds, folder = config['Labels'][obj.name], label = config['General']['CreateYoloLabels'], mask = config['General']['CreateSegmentationMask'], path = config['General']['AnimateAlongPath'])
	else:
		batch_render(scene, camera_object, visibility_camera_object, lamp_obj, mesh_obj, int(steps), config, bounds, label = config['General']['CreateYoloLabels'], mask = config['General']['CreateSegmentationMask'], path = config['General']['AnimateAlongPath'])
	return


if __name__ == '__main__':
	main()
