import bpy
import random
from Modifications.Modification import Modification
from numpy.random import choice
from . import Utils

### Randomly hides the objects
class RandomDisappear(Modification):
    def __init__(self,  objects=[], probability=0.5):
        self.probability  = probability
        super(RandomDisappear, self).__init__(objects)

    def Action(self, obj):
        chance = choice([0,1], 1,replace=False, p=[1-self.probability, self.probability] )
        if chance:
            Utils.hide_obj_and_children(obj)

    def PostProcessing(self, obj):
        Utils.show_obj_and_children(obj)