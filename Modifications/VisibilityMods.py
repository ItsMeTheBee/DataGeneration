import bpy
from Modifications.Modification import Modification

### If used as part of the mask mod list, this mod hides the object in the rgb image 
### but makes it visible in the masked image
### Usefull for labeling "holes" without using see-through materials (--> less rendering compexity)
class HideInRGB(Modification):
    def __init__(self, objects = []):
        super(HideInRGB, self).__init__(objects)

    def PreProcessing(self, obj):
        for obj in self.Objects:
            obj.hide_render = True

    def performAction(self, obj):
        for obj in self.Objects:
            if obj.parent.hide_render == False:
                obj.hide_render = False

    def PostProcessing(self, obj):
        for obj in self.Objects:
            obj.hide_render = True