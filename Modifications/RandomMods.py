import bpy
import random
import bmesh
import mathutils
import math
from mathutils.bvhtree import BVHTree
from Modifications.Modification import Modification
from numpy.random import choice


class RandomDisappear(Modification):
    def __init__(self,  objects=[], probability=0.5):
        self.probability  = probability
        super(RandomDisappear, self).__init__(objects)

    def Action(self, obj):
        chance = choice([0,1], 1,replace=False, p=[1-self.probability, self.probability] )
        #print("CHANCE ", chance)
        if chance:
            obj.hide_render = True