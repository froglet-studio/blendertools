bl_info = {
    "name": "Marker manager - Froglet Studio Blender Tools",
    "author" : "Julius Hilker, Froglet Sudio",
    "version": (0 , 2),
    "blender": (3, 2, 2),
    "location": "Timeline + Dopesheet + Graph + Sequencer",
    "description": "Marker manager in a tab. Store markers in collections.",
    "warning": "Work in Progress",
    "category": "Markers",
    "doc_url": "https://github.com/froglet-studio/blendertools/wiki/Blendertools-by-Froglet-Studio"
}

import bpy
from bpy.app.handlers import persistent

def FRGLT_marker_select(self,context):
    scene = context.scene
    ops = bpy.ops
    collections = scene.LIST_FRGLT_MarkerCollections
    collection_index = scene.FRGLT_MarkerCollectionsIndex   
    current_collection = collections[collection_index]  
    markers = current_collection.items

    if len(markers) == 0:
        return
    
    current_marker = current_collection.items[current_collection.index]
    if len(scene.timeline_markers) > 0:
        ops.marker.select_all(action="DESELECT")
    
    for i in scene.timeline_markers:
        if current_marker.frame == i.frame:
            i.select = True
    
def FRGLT_collection_select(self,context):
    scene = context.scene
    ops = bpy.ops
    collections = scene.LIST_FRGLT_MarkerCollections
    collection_index = scene.FRGLT_MarkerCollectionsIndex   

    if collection_index < 0:
        collection_index = 0

    if len(collections) < 1:
        return

    current_collection = collections[collection_index]
    
    if len(scene.timeline_markers) > 0:
       scene.timeline_markers.clear()

    for i in current_collection.items:
        
        for window in context.window_manager.windows:
            screen = window.screen
            for area in screen.areas:
                if area.type == 'DOPESHEET_EDITOR':
                    with context.temp_override(window=window, area=area):
                        ops.marker.add()
                    break        
        
        current_marker = scene.timeline_markers[len(scene.timeline_markers)-1]
        current_marker.frame = i.frame
        current_marker.name = i.name

        if i.camera and bpy.data.objects[i.camera]:
            current_marker.camera = bpy.data.objects[i.camera]

    current_collection.index = current_collection.index

def rename_marker(self,context):
    context.scene.FRGLT_MarkerCollectionsIndex = context.scene.FRGLT_MarkerCollectionsIndex

class PROPS_FRGLT_Markers(bpy.types.PropertyGroup):
    """Group of properties representing an item in the list."""
    name : bpy.props.StringProperty(name="Name", default="Marker", update=rename_marker)
    frame : bpy.props.IntProperty(name="Frame",update=FRGLT_collection_select)
    camera : bpy.props.StringProperty(name="Camera",update=FRGLT_collection_select)

class PROPS_FRGLT_MarkerCollections(bpy.types.PropertyGroup):
    """Group of properties representing an item in the list."""
    name : bpy.props.StringProperty(name="Base Name", default="New Collection")
    use_frame_step: bpy.props.BoolProperty(name="Use Frame Step", default=False)
    frame_step: bpy.props.IntProperty(name="Frame Step",default=10)
    items: bpy.props.CollectionProperty(type = PROPS_FRGLT_Markers)
    index: bpy.props.IntProperty(name="index",default=0,update=FRGLT_marker_select)

class MARKERS_UL_FRGLT_MarkerCollections(bpy.types.UIList):
    """List of Marker Collections"""

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            icon = "OUTLINER_COLLECTION"
            #items = len(item.items)
            #if items < 1:
            #    icon = "COLLECTION_NEW"
            layout.prop(item, "name", text="", emboss=False, icon=icon)
           # layout.label(text=str(items))

        elif self.layout_type in {'GRID'}:

            layout.alignment = 'CENTER'
            layout.prop(item,"name")

class MARKERS_UL_FRGLT_Markers(bpy.types.UIList):
    """List of Markers"""

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):

        # We could write some code to decide which icon to use here...
        custom_icon = 'MARKER_HLT'
        if item.camera:
            custom_icon = 'OUTLINER_OB_CAMERA'

        if self.layout_type in {'DEFAULT', 'COMPACT'}:

            layout.prop(item, "name", text="", emboss=False, icon = custom_icon)
            op = layout.operator("frglt.set_frame", text="", icon='RESTRICT_SELECT_OFF').index = index
          
            #layout.prop(item, "name", text="", emboss=False, icon = custom_icon)
            layout.prop(item,"frame", text="")
            layout.prop_search(item,"camera", bpy.data, "cameras",text="")
        elif self.layout_type in {'GRID'}:

            layout.alignment = 'CENTER'
            layout.label(text=item.name, icon = custom_icon)

class PANEL_FRGLT_MarkerCollections(bpy.types.Panel):
    """Baseclass for Marker Collection Panel"""
    bl_region_type = "UI"
    bl_label = "Marker Collections"
    bl_category = "Markers"

    def draw(self, context):
      
        scene = context.scene
        collections = scene.LIST_FRGLT_MarkerCollections
        collection_count = len(collections)
 
        layout = self.layout
        row = layout.row()
        row.template_list("MARKERS_UL_FRGLT_MarkerCollections", "", scene, "LIST_FRGLT_MarkerCollections", scene, "FRGLT_MarkerCollectionsIndex",rows=9, type="DEFAULT")
        
        if collection_count < 0:
            return
        col = row.column(align=True)
        col.operator("frglt.new_collection", text="", icon='ADD')

        collection_index = context.scene.FRGLT_MarkerCollectionsIndex
        collection = collections[collection_index]          
        col.operator("frglt.delete_collection", text="", icon='REMOVE')

        list_sidebar_delete = col.row(align=True)
        list_sidebar_delete.operator("frglt.delete_marker", text="", icon='TRASH').delete_all = True

class PANEL_FRGLT_MarkerCollections_Dopesheet(PANEL_FRGLT_MarkerCollections):
    """Marker Collection Panel in the Dopesheet Editor"""
    bl_idname = "OBJECT_PT_frglt_marker_manager_collections_dopesheet"
    bl_space_type = "DOPESHEET_EDITOR"

class PANEL_FRGLT_MarkerCollections_Graph(PANEL_FRGLT_MarkerCollections):
    """Marker Collection Panel in the Dopesheet Editor"""
    bl_idname = "OBJECT_PT_frglt_marker_manager_collections_graph"
    bl_space_type = "GRAPH_EDITOR"

class PANEL_FRGLT_MarkerCollections_NLA(PANEL_FRGLT_MarkerCollections):
    """Marker Collection Panel in the NLA Editor"""
    bl_idname = "OBJECT_PT_frglt_marker_manager_collections_NLA"
    bl_space_type = "NLA_EDITOR"

class PANEL_FRGLT_MarkerCollections_Sequencer(PANEL_FRGLT_MarkerCollections):
    """Marker Collection Panel in the Video Sequencer"""
    bl_idname = "OBJECT_PT_frglt_marker_manager_collections_sequencer"
    bl_space_type = "SEQUENCE_EDITOR"

class PANEL_FRGLT_Markers(bpy.types.Panel):
    """Baseclass for Markers Panel"""
    bl_region_type = "UI"
    bl_label = "Markers"
    bl_category = "Markers"

    def draw(self, context):

        layout = self.layout
        scene = context.scene
        collections = scene.LIST_FRGLT_MarkerCollections
        collection_index = scene.FRGLT_MarkerCollectionsIndex        
        current_collection = collections[collection_index]  
        markers = current_collection.items
        current_frame = scene.frame_current
        
        row = layout.row()
        col = row.column()
        col.prop(current_collection,"use_frame_step",text="")
        
        col = row.column()
        if current_collection.use_frame_step == False:
            col.enabled = False
        col.prop(current_collection,"frame_step", text="Frame Step", icon='ADD')

        list = layout.row()
        list.template_list("MARKERS_UL_FRGLT_Markers", "", current_collection, "items", current_collection, "index", rows=9, type="DEFAULT")

        list_sidebar = list.column(align=True)
        list_sidebar_add = list_sidebar.row(align=True)
        list_sidebar_add.operator("frglt.new_marker", text="", icon='ADD')
        
        if len(current_collection.items) > 0 and current_collection.use_frame_step==False:
            for i in current_collection.items:
                if i.frame==current_frame:
                    list_sidebar_add.enabled = False

        list_sidebar_add = list_sidebar.row(align=True)

        list_sidebar.separator()
        if len(markers) > 0:
            list_sidebar_delete = list_sidebar.row(align=True)
            current_marker = current_collection.items[current_collection.index]
            list_sidebar_delete.operator("frglt.delete_marker", text="", icon='REMOVE')

      
            marker_details = layout.row().column()     
            if bpy.context.scene.tool_settings.lock_markers == True:
                marker_details.enabled = False

            marker_details.prop(current_marker, "name", text="Name", emboss=True)

            marker_details.prop(current_marker, "frame", text="Frame", emboss=True)

            marker_details.prop_search(current_marker,"camera", bpy.data, "cameras")

class PANEL_FRGLT_Markers_Dopesheet(PANEL_FRGLT_Markers):
    """Markers Panel in the Dopesheet Editor"""
    bl_idname = "OBJECT_PT_frglt_marker_manager_dopesheet"
    bl_space_type = "DOPESHEET_EDITOR"

class PANEL_FRGLT_Markers_Graph(PANEL_FRGLT_Markers):
    """Markers Panel in the Graph Editor"""
    bl_idname = "OBJECT_PT_frglt_marker_manager_graph"
    bl_space_type = "GRAPH_EDITOR"

class PANEL_FRGLT_Markers_NLA(PANEL_FRGLT_Markers):
    """Markers Panel in the NLA Editor"""
    bl_idname = "OBJECT_PT_frglt_marker_manager_nla"
    bl_space_type = "NLA_EDITOR"

class PANEL_FRGLT_Markers_Sequencer(PANEL_FRGLT_Markers):
    """Markers Panel in the Sequencer Editor"""
    bl_idname = "OBJECT_PT_frglt_marker_manager_sequencer"
    bl_space_type = "SEQUENCE_EDITOR"

class OP_FRGLT_Set_Frame(bpy.types.Operator):
    """Set frame of marker."""

    bl_idname = "frglt.set_frame"
    bl_label = "Set current Frame"

    frame: bpy.props.IntProperty(default=0)
    index: bpy.props.IntProperty(default=0)

    def execute(self, context):
        scene = context.scene
        collections = scene.LIST_FRGLT_MarkerCollections
        collection_index = scene.FRGLT_MarkerCollectionsIndex        
        current_collection = collections[collection_index]
      
        scene.frame_current = current_collection.items[self.index].frame
        current_collection.index = self.index
        
        return{'FINISHED'}

class OP_FRGLT_Marker_Select(bpy.types.Operator):
    """Select marker."""

    bl_idname = "FRGLT.marker_select"
    bl_label = "Set current Frame"

    frame: bpy.props.IntProperty(default=0)

    def execute(self, context):
        scene = context.scene
       
        scene.frame_current = self.frame
        scene.FRGLT_MarkerCollectionsIndex = scene.FRGLT_MarkerCollectionsIndex 
        return{'FINISHED'}

class OP_FRGLT_MarkerCollection_Select(bpy.types.Operator):
    """Select Marker collection"""

    bl_idname = "FRGLT.markerCollection_select"
    bl_label = "Set current Frame"

    frame: bpy.props.IntProperty(default=0)

    def execute(self, context):
        scene = context.scene
       
        scene.frame_current = self.frame
        scene.FRGLT_MarkerCollectionsIndex = scene.FRGLT_MarkerCollectionsIndex 
        return{'FINISHED'}

class OP_FRGLT_Marker_New(bpy.types.Operator):
    """Add a new marker to the list."""

    bl_idname = "frglt.new_marker"
    bl_label = "Add a new item"
    
    frame: bpy.props.IntProperty(default=-1)
    def execute(self, context):
        scene = context.scene
        collections = scene.LIST_FRGLT_MarkerCollections
        collection_index = scene.FRGLT_MarkerCollectionsIndex
        current_collection = scene.LIST_FRGLT_MarkerCollections[collection_index]
        ops = bpy.ops

        current_frame = scene.frame_current

        if len(collections) == 0:
            ops.frglt.new_collection()
        
        if collection_index < 0:
            collection_index = 0
   
        if current_collection.index < 0:
            current_collection.index = 0
        
        if current_collection.use_frame_step == True:
            scene.frame_current += current_collection.frame_step

        if len(current_collection.items)>0:
            for i in current_collection.items:
                if i.frame==current_frame:
                    
                    return{'FINISHED'}

        marker_index = current_collection.index
        new_marker = current_collection.items.add()
        current_collection.items[-1].name = "F_"+str(current_frame)
        if(self.frame == -1):
            
            new_marker.frame = current_frame
        else:
            
            new_marker.frame = self.frame

        current_collection.index = len(current_collection.items) - 1
          
        scene.FRGLT_MarkerCollectionsIndex = scene.FRGLT_MarkerCollectionsIndex 
        return{'FINISHED'}


class OP_FRGLT_Marker_Delete(bpy.types.Operator):
    """Delete marker from collection."""

    bl_idname = "frglt.delete_marker"    
    bl_label = ""
    
    delete_all: bpy.props.BoolProperty(default=False)

    @classmethod
    def description(cls, context, operator):
        if operator.delete_all==True:
            return "Clear Collection"    

    def execute(self, context):
        scene = context.scene
       
        collections = scene.LIST_FRGLT_MarkerCollections
        collection_index = scene.FRGLT_MarkerCollectionsIndex
        
        current_collection = collections[collection_index]

        markers = current_collection.items

        if len(markers) > 0:
            if self.delete_all == True:
         
                current_collection.items.clear()
            else: 
                
                current_collection.items.remove(current_collection.index)
                scene.FRGLT_MarkerCollectionsIndex = scene.FRGLT_MarkerCollectionsIndex 
  
        return{'FINISHED'}

class OP_FRGLT_MarkerCollections_New(bpy.types.Operator):
    """Create a new marker collection."""

    bl_idname = "frglt.new_collection"
    bl_label = "Add a new item"

    def execute(self, context):
        scene = context.scene
        collections = bpy.context.scene.LIST_FRGLT_MarkerCollections
      
        new_collection = collections.add()
        collection_count = len(collections)

        new_name = new_collection.name
        new_index = 0  

        if collection_count > 1:
            new_index = collection_count-1            
            new_name += "."+str(new_index)

        scene.FRGLT_MarkerCollectionsIndex = new_index
        new_collection.name = new_name    

        return{'FINISHED'}

class OP_FRGLT_MarkerCollections_Delete(bpy.types.Operator):
    """Delete marker collection and all markers in it."""

    bl_idname = "frglt.delete_collection"
    bl_label = "Add a new item"

    def execute(self, context):
        scene = context.scene
        ops = bpy.ops
        collection_index = context.scene.FRGLT_MarkerCollectionsIndex
        collections = scene.LIST_FRGLT_MarkerCollections

        markers = scene.timeline_markers
        old_len = len(collections)-1

        collections.remove(collection_index)



        if len(markers) > 0:
            ops.marker.select_all(action="SELECT")
            ops.marker.delete()
        
        if collection_index == old_len:
            scene.FRGLT_MarkerCollectionsIndex = collection_index-1
        
        if len(collections)==0:
            ops.frglt.new_collection()
            scene.FRGLT_MarkerCollectionsIndex = 0
        #else:
        #    scene.FRGLT_MarkerCollectionsIndex = collection_index

        return{'FINISHED'}


register_classes = [ 
    PROPS_FRGLT_Markers,
    PROPS_FRGLT_MarkerCollections,    
    MARKERS_UL_FRGLT_Markers,
    MARKERS_UL_FRGLT_MarkerCollections,
    OP_FRGLT_Marker_New,
    OP_FRGLT_Marker_Delete, 
    OP_FRGLT_MarkerCollections_New,
    OP_FRGLT_MarkerCollections_Delete,
    OP_FRGLT_Set_Frame,
    PANEL_FRGLT_MarkerCollections_Dopesheet,
    PANEL_FRGLT_MarkerCollections_Graph,
    PANEL_FRGLT_MarkerCollections_NLA,
    PANEL_FRGLT_MarkerCollections_Sequencer,
    PANEL_FRGLT_Markers_Dopesheet,
    PANEL_FRGLT_Markers_Graph,
    PANEL_FRGLT_Markers_NLA,
    PANEL_FRGLT_Markers_Sequencer

]

space_types = (
    bpy.types.SpaceGraphEditor,
    bpy.types.SpaceDopeSheetEditor,
    bpy.types.SpaceNLA,
    bpy.types.SpaceSequenceEditor
    
)

spaces = []      # Handle for spaces

def set_default_collection():

    if len(bpy.context.scene.LIST_FRGLT_MarkerCollections) < 1:
        new_markers = []
        
        for i in bpy.context.scene.timeline_markers:
            new_markers.append({"name": i.name , "frame" : i.frame})
        

   
        bpy.context.scene.timeline_markers.clear()
        bpy.ops.frglt.new_collection()
        current_collection = bpy.context.scene.LIST_FRGLT_MarkerCollections[bpy.context.scene.FRGLT_MarkerCollectionsIndex]
        
        for ex in new_markers:
            bpy.context.scene.frame_set(ex["frame"])
            
            bpy.ops.frglt.new_marker()
            current_collection.items[-1].name = ex["name"]
            #current_collection.items[-1].frame = e.frame
        bpy.context.scene.FRGLT_MarkerCollectionsIndex = bpy.context.scene.FRGLT_MarkerCollectionsIndex    


    bpy.app.timers.unregister(set_default_collection)

    return 2.0

def listen_for_new_marker(context):
    current_collection = bpy.context.scene.LIST_FRGLT_MarkerCollections[bpy.context.scene.FRGLT_MarkerCollectionsIndex]
    markers = bpy.context.scene.timeline_markers
    m_len = len(markers)
    c_len = len(current_collection.items)

    if m_len > c_len:
        bpy.context.scene.timeline_markers.clear()
        
        bpy.ops.frglt.new_marker()
        bpy.context.scene.FRGLT_MarkerCollectionsIndex = bpy.context.scene.FRGLT_MarkerCollectionsIndex

@persistent
def load_handler(dummy):
    set_default_collection()

def register():

    for cls in register_classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.LIST_FRGLT_MarkerCollections = bpy.props.CollectionProperty(type = PROPS_FRGLT_MarkerCollections)
    bpy.types.Scene.FRGLT_MarkerIndex = bpy.props.IntProperty(name = "Index for Froglet Marker Manager", default = 0,update=FRGLT_marker_select)
    bpy.types.Scene.FRGLT_MarkerCollectionsIndex = bpy.props.IntProperty(name = "Index for Froglet Marker Manager Collections", default = 0, update=FRGLT_collection_select)
    bpy.app.handlers.load_post.append(set_default_collection)

    if bpy.app.timers.is_registered(set_default_collection) == False:
            bpy.app.timers.register(set_default_collection)
      
    bpy.app.handlers.load_post.append(load_handler)

    for space in space_types:
        spaces.append(
            space.draw_handler_add(listen_for_new_marker, (bpy.context,), "WINDOW", "POST_PIXEL"))

    # Redraw editors with a timeline
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type in {"DOPESHEED_EDITOR", "GRAPH_EDITOR", "NLA_EDITOR", "SEQUENCER"}:
                area.tag_redraw()

    print("Welcome to the fantastic world of markers! Blender for the win...")

def unregister():

    bpy.app.handlers.load_post.remove(load_handler)

    if bpy.app.timers.is_registered(set_default_collection) == True:
        bpy.app.timers.unregister(set_default_collection)    
    
    for cls in register_classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.LIST_FRGLT_MarkerCollections
    del bpy.types.Scene.FRGLT_MarkerIndex
    del bpy.types.Scene.FRGLT_MarkerCollectionsIndex

    for owner, space in zip(spaces, space_types):
        space.draw_handler_remove(owner, "WINDOW")
    spaces.clear()

    print("Goodbye and good night! See you soon in Blender Heaven!")

if __name__ == "__main__":
    register()
