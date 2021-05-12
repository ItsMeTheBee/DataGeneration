import bpy
import bmesh
from Modifications.Modification import Modification


class CreateHull(Modification):
    def __init__(self,  objects=[]):
        self.backup = dict()
        super(CreateHull, self).__init__(objects)

    def Action(self, obj):
        self.backup[obj.name] = obj.data.copy()
        bm = bmesh.new()
        me = obj.data
        bm.from_mesh(me)
        bmesh.ops.convex_hull(bm, input=bm.verts)
        bm.to_mesh(me)
        me.update()
        bm.clear()

    def PostProcessing(self, obj):
        orig_data= self.backup[obj.name]
        obj.data = orig_data
        #obj.data.update()
        print("Restored from Hull ", obj.name)