bl_info = {
    "name": "Addon Loader - Froglet Studio Blender Tools",
    "author" : "Julius Hilker, Froglet Sudio",
    "version": (0 , 1),
    "blender": (3, 4, 1),
    "location": "Settings -> Addons",
    "description": "Load and quickly reinstall single file addons from an external file.",
    "warning": "Work in Progress",
    "category": "Addons",
    "doc_url": "https://github.com/froglet-studio/blendertools/wiki/Blendertools-by-Froglet-Studio"
}

import addon_utils
import bpy 
from bpy.props import (StringProperty)
from bpy.types import (Operator,AddonPreferences)
from bpy_extras.io_utils import ImportHelper
from bpy.utils import (register_class, unregister_class)


class FRGLT_install(Operator):
    bl_idname = "frglt.install"
    bl_label = "Installs Addon"

    def execute(self, context):
        preferences = bpy.context.preferences.addons[__name__].preferences
        bpy.ops.preferences.addon_install(filepath=preferences.file, overwrite=True)

        return {'FINISHED'}

class FRGLT_load_file(Operator, ImportHelper):

    bl_idname = "frglt.load_file"
    bl_label = "Load a .py file."
    
    filter_glob: StringProperty(
        default='*.py;',
        options={'HIDDEN'}
    )

    def execute(self, context):
        """Do something with the selected file(s)."""
        preferences = bpy.context.preferences.addons[__name__].preferences
        preferences.file = self.filepath

        return {'FINISHED'}

class FRGLT_manager_addon_preferences(AddonPreferences):
    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __name__


    file: StringProperty(
        name="file",
        default=""

    )


   
    def draw(self, context):
        layout = self.layout
        layout.label(text="Load and Install an Addon from an external file. (Single File Addons Only)")
        
        row = layout.row()  

        row.label(text=self.file)
        row.operator("frglt.load_file",text="Load")

        if self.file != "":
            row = layout.row()     
            row.operator("frglt.install",text="Install")

classes = [ 
    FRGLT_install,
    FRGLT_load_file,
    FRGLT_manager_addon_preferences

]

def register():

    for cls in classes:
        register_class(cls)

def unregister():

    for cls in classes:
        unregister_class(cls)
    
if __name__ == "__main__":
    register()