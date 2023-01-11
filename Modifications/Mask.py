import bpy
import bmesh
import mathutils
import math
import os
from Modifications.Modification import Modification
import colorsys


### Uses the composition function to create segmentation mask images
### If init_obj_ids is set to true, the pass index of every object will be set according to the config file
### If init_comp is set to true, a new composition will be created (deleting the current one)
### In this composition the IndexOB output of the rendering process is coupled with the divide function, which generates a segmentation mask with 0 being the background and 1 - 255 being the object pixel values
### For some reason, the compositor sometimes uses the given file path but adds four numbers to the file (in my case 0134) - they are deleted in the postprocessing step
class MaskComposition(Modification):
    def __init__(self, objects = [], index_dict = {}, init_comp = True, init_obj_ids = True, path = "/home/data", file_ending = "0134.png"):
        self.init_comp = init_comp
        self.path = path
        self.init_obj_ids = init_obj_ids
        self.index_dict = index_dict
        self.init_done = False
        self.current_file = ""
        self.file_ending = file_ending
        super(MaskComposition, self).__init__(objects)

    def PreProcessing(self, obj):
        bpy.context.scene.use_nodes = True
        if (self.init_done):
            return
        if (self.init_comp):
            #bpy.context.scene.use_nodes = True
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
            
            #math_node_add = tree.nodes.new(type='CompositorNodeMath')
            #math_node_add.operation = "ADD"
            #math_node_add.inputs[1].default_value = 1/255
            

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
        print("Setting filename to ", filename)
        self.current_file = filename
        bpy.context.scene.use_nodes = True
        output_node = bpy.context.scene.node_tree.nodes.get("File Output")
        output_node.file_slots[0].path = filename
        #output_node.file_slots[0].use_node_format = False

    def performAction(self, filename):
        self.Action(filename)

    def PostProcessing(self, obj):
        bpy.context.scene.use_nodes = False
        try:
            os.rename(os.path.join(self.path, self.current_file + "0134.png"), os.path.join(self.path, self.current_file + ".png"))
        except:
            pass