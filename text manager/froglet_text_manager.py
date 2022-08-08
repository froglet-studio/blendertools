bl_info = {
    "name": "Text manager - Froglet Studio Blender Tools",
    "author" : "Julius Hilker, Froglet Sudio",
    "version": (0 , 1),
    "blender": (3, 2, 0),
    "location": "Texteditor > Panel > Textmanager",
    "description": "Text manager/Browser in a Tab. Auto reload external files. Auto run on reload.",
    "category": "Text Editor",
    "warning": "work in progress",
    "doc_url": "https://github.com/froglet-studio/blendertools/wiki/Blendertools-by-Froglet-Studio"
}
import bpy
from pathlib import Path
from bpy.app.handlers import persistent

class TEXT_UL_Froglet_Text_List(bpy.types.UIList):
    """List of textblocks"""

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):

        # We could write some code to decide which icon to use here...

        if item.filepath:
            custom_icon = 'FILE_HIDDEN'
        else:
            custom_icon = 'FILE_BLEND'

        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:

            layout.prop(item, "name", text="", emboss=False, icon = custom_icon)

        elif self.layout_type in {'GRID'}:

            layout.alignment = 'CENTER'
            layout.label(text=item.name, icon = custom_icon)



class FrogletTextManagerPanel(bpy.types.Panel):
    """Creates a Panel in the Text Editor window"""
    bl_idname = "OBJECT_PT_froglet_text_manager"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"
    bl_label = "Text Manager"
    bl_category = "Texteditor"

    def draw(self, context):

        layout = self.layout
        scene = context.scene
        data = bpy.data
        index = context.scene.froglet_text_manager_list_index



        row = layout.row()
        row.template_list("TEXT_UL_Froglet_Text_List", "", data, "texts", scene, "froglet_text_manager_list_index",rows=9, type="DEFAULT")

        col = row.column(align=True)
        col.operator("text.run_script", text="", icon='PLAY')
        col.separator()
        col.operator('text.new',icon="ADD", text="")
        col.operator('text.unlink',icon="REMOVE", text="")
        col.separator()
        col.operator("text.save", text="", icon='FILE_TICK')
        col.operator("text.save_as", text="", icon='FILE_NEW')

        col.separator()
        col.operator('text.open',icon="FILE_FOLDER", text="")


        if len(bpy.data.texts) > 0:

            current = bpy.data.texts[index];

            if current.filepath:

                filename = Path(current.filepath)

                row = layout.row()

                #if not filename.exists():
                #    row.label(text="file doesn#t exist", icon = custom_icon)

                row.prop(current, "filepath", text="Path", emboss=True)

                row = layout.row()
                row.alignment = 'RIGHT'
                row.prop(current, "auto_refresh", text="Auto Refresh ", emboss=True)
                row.prop(current, "auto_run", text="Run on refresh", emboss=True)
                row = layout.row()
                row.operator("text.make_internal", text="Make Internal", icon='FILE_3D')
                row = layout.row()
                row.operator("text.resolve_conflict", text="Resolve Conflict", icon='ERROR')
                row = layout.row()
                row.operator("text.reload", text="Reload", icon='FILE_REFRESH')






def froglet_text_manager_updater():
    #print("looking for update   ")
    scene = bpy.context.scene
    data = bpy.data.texts
    index = 0

    for t in bpy.data.texts:
        if t.is_modified and t.auto_refresh==True and not t.is_in_memory:
            old_index = scene.froglet_text_manager_list_index
            scene.froglet_text_manager_list_index = index

            ctx = bpy.context.copy()
            #Ensure  context area is not None
            ctx['area'] = ctx['screen'].areas[0]

            for t in bpy.data.texts:
                if t.is_modified and t.auto_refresh==True and not t.is_in_memory:
                    #print("  * Warning: Updating external script", t.name)
                    # Change current context to contain a TEXT_EDITOR
                    oldAreaType = ctx['area'].type
                    ctx['area'].type = 'TEXT_EDITOR'
                    ctx['edit_text'] = t
                    bpy.ops.text.resolve_conflict(ctx, resolution='RELOAD')
                    #Restore context
                    ctx['area'].type = oldAreaType

                    if t.auto_run==True:
                        bpy.ops.text.run_script(ctx)

            scene.froglet_text_manager_list_index = old_index

        index = index + 1

    return 2.0


def setText(self,context):
    index = bpy.context.scene.froglet_text_manager_list_index
    name = bpy.data.texts[index].name
    if bpy.context.space_data:
        bpy.context.space_data.text = bpy.data.texts[name]


def froglet_text_manager_failsave():
    if bpy.app.timers.is_registered(froglet_text_manager_updater) == False:
        bpy.app.timers.register(froglet_text_manager_updater)
    return 2.0


@persistent
def load_handler(dummy):
    bpy.app.timers.register(froglet_text_manager_updater)
    bpy.app.timers.register(froglet_text_manager_failsave)







def register():
    bpy.app.handlers.load_post.append(load_handler)

    if bpy.app.timers.is_registered(froglet_text_manager_failsave) == False:
            bpy.app.timers.register(froglet_text_manager_failsave)


    bpy.types.Scene.froglet_text_manager_list_index = bpy.props.IntProperty(name = "Index for Froglet Text Manager", default = 0, update = setText)
    bpy.types.Text.auto_refresh = bpy.props.BoolProperty(name = "Auto refresh", default = False)
    bpy.types.Text.auto_run = bpy.props.BoolProperty(name = "Auto run after Refresh", default = False)

    bpy.utils.register_class(FrogletTextManagerPanel)
    bpy.utils.register_class(TEXT_UL_Froglet_Text_List)




def unregister():

    if bpy.app.timers.is_registered(froglet_text_manager_updater) == True:
        bpy.app.timers.unregister(froglet_text_manager_updater)

    if bpy.app.timers.is_registered(froglet_text_manager_failsave) == True:
            bpy.app.timers.unregister(froglet_text_manager_failsave)

    bpy.app.handlers.load_post.remove(load_handler)

    del bpy.types.Scene.froglet_text_manager_list_index
    del bpy.types.Text.auto_refresh
    del bpy.types.Text.auto_run


    bpy.utils.unregister_class(FrogletTextManagerPanel)
    bpy.utils.unregister_class(TEXT_UL_Froglet_Text_List)

if __name__ == "__main__":
    register()
