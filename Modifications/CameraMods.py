import bpy
import random
from Modifications.Modification import Modification

# shuffles the focal length of every assigned camera
# ! lens unit is millimeters!
class ShuffleFocalLength(Modification):
    def __init__(self, range=[], objects=[]):
        self.Range = range
        super(ShuffleFocalLength, self).__init__(objects)

    def Action(self, obj):
        bpy.data.cameras[obj.name].lens = random.uniform(self.Range[0], self.Range[1])
        bpy.context.view_layer.update()