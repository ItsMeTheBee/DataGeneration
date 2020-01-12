import bpy
import bmesh
import mathutils
import math
from Modifications.Modification import Modification

class MaskBlackNWhite(Modification):
    def __init__(self, mask_true_objects=[], mask_false_objects=[], mask_true_color=[44,44,44,1], mask_false_color=[66,66,66,1], mask_true_material="Mask_True", mask_false_material="Mask_False"):
        self.mask_true_color = mask_true_color
        self.mask_false_color = mask_false_color
        self.mask_true_material = mask_true_material
        self.mask_false_material = mask_false_material
        self.mask_true_objects = mask_true_objects
        self.mask_false_objects = mask_false_objects
        self.color_backup = dict()
        self.createColorBackup()
        super(MaskBlackNWhite, self).__init__()

    def performAction(self):
        self.createMaskMaterials()
        for obj in self.mask_true_objects:
            self.Action(obj, True)

        for obj in self.mask_false_objects:
            self.Action(obj, False)

    def Action(self, obj, mask):
        mat_true = bpy.data.materials.get(self.mask_true_material)
        mat_false = bpy.data.materials.get(self.mask_false_material)

        if mask:
            test_true = obj.data.materials.get(self.mask_true_material)
            if test_true is None:
                obj.data.materials.append(mat_true)

            obj.active_material = mat_true
            print("Set ", obj.name, " material to ", self.mask_true_material)
            bpy.context.view_layer.update()

        else:
            test_false = obj.data.materials.get(self.mask_false_material)
            if test_false is None:
                obj.data.materials.append(mat_false)
            obj.active_material = mat_false
            print("Set ", obj.name, " material to ", self.mask_false_material)
            bpy.context.view_layer.update()

    def createMaskMaterials(self):
        mat = bpy.data.materials.get(self.mask_true_material)
        if mat is None:
            # create material
            mat = bpy.data.materials.new(name=self.mask_true_material)
            mat.diffuse_color = self.mask_true_color

        mat = bpy.data.materials.get(self.mask_false_material)
        if mat is None:
            # create material
            mat = bpy.data.materials.new(name=self.mask_false_material)
            mat.diffuse_color = self.mask_false_color

    def createColorBackup(self):
        for obj in self.mask_false_objects:
            orig_mat = obj.active_material
            self.color_backup[obj.name] = orig_mat

        for obj in self.mask_true_objects:
            orig_mat = obj.active_material
            self.color_backup[obj.name] = orig_mat

    def restoreColor(self):
        for obj in self.mask_false_objects:
            orig_mat = self.color_backup[obj.name]
            obj.active_material = orig_mat

        for obj in self.mask_true_objects:
            orig_mat = self.color_backup[obj.name]
            obj.active_material = orig_mat