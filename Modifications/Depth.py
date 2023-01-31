import bpy
import bmesh
import mathutils
import math
import os
from Modifications.Modification import Modification
import colorsys


### Uses the composition function to create depth images
### If init_comp is set to true, a new composition will be created (either by adding to the current one or by setting a new one)
### In this composition the Depth output of the rendering process is coupled with the divide function, which generates a depth image that SHOULD relate to a Realsense depth image
### For some reason, the compositor sometimes uses the given file path but adds four numbers to the file (in my case 0134) - they are deleted in the postprocessing step
class DepthComposition(Modification):
    def __init__(self, objects = [], index_dict = {}, init_comp = True, path = "/home/data", file_ending = "0134.png"):
        self.init_comp = init_comp
        self.path = path
        self.index_dict = index_dict
        self.init_done = False
        self.current_file = ""
        self.file_ending = file_ending
        self.output_node = None
        super(DepthComposition, self).__init__(objects)

    def performPostProcessing(self):
        self.PostProcessing()

    def performPreProcessing(self):
        self.PreProcessing()

    def PreProcessing(self):
        bpy.context.scene.use_nodes = True
        if (self.init_done):
            return
        if (self.init_comp):
            #bpy.context.scene.use_nodes = True
            bpy.context.scene.use_nodes = True
            bpy.context.scene.view_layers["RenderLayer"].use_pass_object_index = True
            tree = bpy.context.scene.node_tree

            output_node = tree.nodes.new(type='CompositorNodeOutputFile')
            output_node.base_path = self.path
            output_node.file_slots[0].format.color_mode = "RGB"
            self.output_node = output_node

            math_node_divide = tree.nodes.new(type='CompositorNodeMath')
            math_node_divide.operation = "DIVIDE"
            math_node_divide.inputs[0].default_value = 0.015
            render_layers_node = tree.nodes.new(type='CompositorNodeRLayers')            

            links = tree.links
            link_index_to_math = links.new(render_layers_node.outputs["Depth"], math_node_divide.inputs[1])
            link_math_to_out = links.new(math_node_divide.outputs[0], output_node.inputs[0])

        self.init_done = True

    def Action(self, filename):
        print("Setting filename to ", filename)
        self.current_file = filename
        bpy.context.scene.use_nodes = True
        #self.output_node = bpy.context.scene.node_tree.nodes.get("File Output")
        self.output_node.file_slots[0].path = filename
        #output_node.file_slots[0].use_node_format = False

    def performAction(self, filename):
        self.Action(filename)

    def PostProcessing(self):
        bpy.context.scene.use_nodes = False
        try:
            os.rename(os.path.join(self.path, self.current_file + "0134.png"), os.path.join(self.path, self.current_file + ".png"))
        except:
            pass