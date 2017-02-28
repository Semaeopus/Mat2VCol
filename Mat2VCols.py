#! /usr/bin/python

# MIT License

# Copyright (c) 2017 Harry Rose - Semaeopus Ltd.

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import bpy
import re

# Enable name cleaning here
CleanUpName = False

class Mat2Col(bpy.types.Operator):
    bl_idname = "object.convert_to_vcolors"
    bl_label = "Mat2Col"

    def Log(self, s):
        self.report({'INFO'}, s)
    
    def Error(self, s):
        self.report({'ERROR'}, s)

    def Warning(self, s):
        self.report({'WARNING'}, s)       

    def CleanUpName(self, currentName):
        name    = "Untitled"
        num     = 1
        nameRE  = re.match('^\D+', currentName)
        numRe   = re.match('.*?([0-9]+)$', currentName)

        if nameRE != None:
            name = nameRE.group(0)
            name = name[0].upper() + name[1:]
            name = name.rstrip("_")

        if numRe != None:
            num = int(numRe.group(1))

        # Loop around until we find the correct next number 
        newName = "{}_0{}".format(name, num)
        if(newName != currentName):
            while newName in bpy.data.objects:
                num = num + 1
                newName = "{}_0{}".format(name, num)

        return newName

    def execute(self, context):
        obj             = context.active_object
        if obj == None:
            self.Error("No Object selected")
            return {'FINISHED'}

        if obj.parent != None:
            self.Warning("Selected child object")
            
        mesh            = obj.data
        faces           = mesh.polygons
        
        # Clean up mesh
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.remove_doubles()
        bpy.ops.mesh.faces_shade_flat()
        bpy.ops.mesh.mark_sharp(clear=True)
        bpy.ops.uv.smart_project()
        bpy.ops.object.mode_set(mode='OBJECT')

        if CleanUpName:
        # Clean up mesh name
            self.Log("Cleaning up names for " + obj.name)
            obj.name = self.CleanUpName(obj.name)
            self.Log("New name: " + obj.name)
    
            if obj.type == 'MESH':
                self.Log("Cleaning up mesh name " + obj.data.name)
                obj.data.name = obj.name + "_mesh"
                self.Log("New mesh name " + obj.data.name)
        

        # color map required to create vertex colors
        color_map_collection = mesh.vertex_colors
        if len(color_map_collection) == 0:
            color_map_collection.new()
            
        color_map = color_map_collection['Col']
        
        i = 0
        for f in mesh.polygons:  # iterate over faces
            print("face", f.index, "material_index", f.material_index)
            slot = obj.material_slots[f.material_index]
            mat = slot.material
            print(mat.name)
            print(mat.diffuse_color)
            (rgb) = mat.diffuse_color # get material color for that face
            for idx in f.loop_indices:
                color_map.data[i].color = rgb
                i += 1
        
        obj.active_material_index = 0
        for i in range(len(obj.material_slots)):
            bpy.ops.object.material_slot_remove({'object': obj})
            
        print ("Assigning to Vertex Colour")
        bpy.ops.object.mode_set(mode='VERTEX_PAINT')
        return {'FINISHED'}


def register():
    bpy.utils.register_class(Mat2Col)

if __name__ == "__main__":
    register()
