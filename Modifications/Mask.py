import bpy
import bmesh
import mathutils
import math
import os
from Modifications.Modification import Modification
import colorsys

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

class MaskComposition(Modification):
    def __init__(self, objects = [], index_dict = {}, init_comp = True, init_obj_ids = True, base_path = "", folder = "labels"):
        self.init_comp = init_comp
        self.base_path = base_path
        self.path = base_path + folder + '/'
        self.init_obj_ids = init_obj_ids
        self.index_dict = index_dict
        self.init_done = False
        super(MaskComposition, self).__init__(objects)

    def PreProcessing(self, obj):
        if (self.init_done):
            return
        if (self.init_comp):
            bpy.context.scene.use_nodes = True
            bpy.context.scene.view_layers["RenderLayer"].use_pass_object_index = True
            tree = bpy.context.scene.node_tree
            # clear default nodes
            for node in tree.nodes:
                tree.nodes.remove(node)

            output_node = tree.nodes.new(type='CompositorNodeOutputFile')
            output_node.base_path = self.path
            output_node.file_slots[0].format.color_mode = "RGB"

            math_node_divide = tree.nodes.new(type='CompositorNodeMath')
            math_node_divide.operation = "DIVIDE"
            math_node_divide.inputs[1].default_value = 255
            render_layers_node = tree.nodes.new(type='CompositorNodeRLayers')

            # comment this in if you want to add 1 to all values (background is (1,1,1) in that case)
            """
            math_node_add = tree.nodes.new(type='CompositorNodeMath')
            math_node_add.operation = "ADD"
            math_node_add.inputs[1].default_value = 1/255
            """

            links = tree.links
            link_index_to_math = links.new(render_layers_node.outputs["IndexOB"], math_node_divide.inputs[0])
            link_math_to_out = links.new(math_node_divide.outputs[0], output_node.inputs[0])

            # also comment this in to add 1 to all values
            #link_divide_to_add = links.new(math_node_divide.outputs[0], math_node_add.inputs[0])
            #link_add_to_out = links.new(math_node_add.outputs[0], output_node.inputs[0])

        if (self.init_obj_ids):
            for obj in self.Objects:
                obj.pass_index = self.index_dict[obj.name]
                print("Set pass index of ", obj.name, " to ", self.index_dict[obj.name])
        self.init_done = True

    def Action(self, filename):
        bpy.context.scene.use_nodes = True
        output_node = bpy.context.scene.node_tree.nodes.get("File Output")
        output_node.file_slots[0].path = filename
        #output_node.file_slots[0].use_node_format = False

    def performAction(self, filename):
        self.Action(filename)

    def PostProcessing(self, obj):
        bpy.context.scene.use_nodes = False
        for filename in os.listdir(self.path):
            new_name = filename.replace("0001.png", ".png")
            os.rename(self.path +filename, self.path +new_name)


class Mask(Modification):
    def __init__(self, objects=[], material_name="Mask", base_material_name="", base_color_node = "", color=[0,0,0,1], mask_world = False, mode="rgb"):
        self.mode = mode
        if self.mode == "rgb":
            self.color = [srgb2lin(color[0]), srgb2lin(color[1]), srgb2lin(color[2]), 1]
        if self.mode == "hsv":
            col = colorsys.hsv_to_rgb(color[0], color[1], color[2])
            self.color = [srgb2lin(col[0]), srgb2lin(col[1]), srgb2lin(col[2]), 1]
        self.material_name = material_name
        self.base_material = base_material_name
        self.base_color_node = base_color_node
        self.mask_world = mask_world
        self.color_backup = dict()
        self.createColorBackup()
        super(Mask, self).__init__(objects)

    def performAction(self):
        self.createMaskMaterials()
        for obj in self.Objects:
            self.Action(obj)

        if self.mask_world:
            try:
                links = bpy.context.scene.world.node_tree.links
                nodes = bpy.context.scene.world.node_tree.nodes
                # get specific link
                from_s = nodes.get("Environment Texture").outputs[0]
                to_s = nodes.get("Background").inputs[0]
                link = next(l for l in links if l.from_socket == from_s and l.to_socket == to_s)

                # remove links
                links.remove(link)
                #nodes = bpy.context.scene.world.node_tree.nodes
                #nodes.remove(nodes.get("Environment Texture"))
                #nodes.get("Background").inputs[0].default_value = self.mask_true_color
            except Exception as e:
                print("Background already disconnected")


    def Action(self, obj):
        obj.cycles_visibility.shadow = False
        mat = bpy.data.materials.get(self.material_name)
        #test = obj.data.materials.get(self.material_name)
        #if test is None:
        #    obj.data.materials.append(mat)

        obj.active_material = mat
        for poly in obj.data.polygons:
            poly.material_index = obj.active_material_index
        #print("Set ", obj.name, " material to ", self.material_name)
        bpy.context.view_layer.update()

    def createMaskMaterials(self):
        mat = bpy.data.materials.get(self.material_name)
        if mat is None:
            # create material
            if self.base_material:
                base = bpy.data.materials.get(self.base_material)
                mat = base.copy()
                mat.name = self.material_name
                nodes = mat.node_tree.nodes
                nodes[self.base_color_node].inputs[0].default_value = self.color
            else:
                mat = bpy.data.materials.new(name=self.material_name)
                mat.diffuse_color = self.color

    def createColorBackup(self):
        for obj in self.Objects:
            obj.cycles_visibility.shadow = True
            orig_mat = obj.active_material
            self.color_backup[obj.name] = orig_mat

        if self.mask_world:
            try:
                links = bpy.context.scene.world.node_tree.links
                nodes = bpy.context.scene.world.node_tree.nodes
                # get specific link
                from_s = nodes.get("Environment Texture").outputs[0]
                to_s = nodes.get("Background").inputs[0]
                link = next(l for l in links if l.from_socket == from_s and l.to_socket == to_s)
                self.color_backup["world"] = link
            except Exception as e:
                print(e)
                print("Background already backed up")

    def PostProcessing(self, obj):        
        orig_mat = self.color_backup[obj.name]
        obj.active_material = orig_mat
        #print("Restored from Mask ", obj.name)
        if self.mask_world:
            try:
                links = bpy.context.scene.world.node_tree.links
                nodes = bpy.context.scene.world.node_tree.nodes
                # get specific link
                from_s = nodes.get("Environment Texture").outputs[0]
                to_s = nodes.get("Background").inputs[0]
                links.new(from_s, to_s)
                #bpy.context.scene.world.node_tree = self.color_backup["world"]
            except Exception as e:
                print(e)
                print("Background already restored")