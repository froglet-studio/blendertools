bl_info = {
    "name": "Marker Manager - Froglet Studios Blender Tools",
    "author" : "Julius Hilker, Froglet Sudios",
    "version": (0 , 1),
    "blender": (3, 2, 0),
    "location": "Timeline + Dopesheet + Graph",
    "description": "Marker Manager in a Tab. Store and set different collections of markers,",
    "warning": "preview of early alpha... ",
    "category": "Markers",
    "doc_url": "https://github.com/froglet-studio/blendertools/blob/main/marker%20manager/froglet_marker_manager.py"
}
import bpy
from bpy.app.handlers import persistent

print("start")
def FRGLT_marker_select(self,context):
    scene = context.scene
    ops = bpy.ops
    collections = scene.LIST_FRGLT_MarkerCollections
    collection_index = scene.FRGLT_MarkerCollectionsIndex   
    current_collection = collections[collection_index]
    markers = current_collection.items

    if len(markers) == 0:
        return
    print("select")

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
        ops.marker.add()
        current_marker = scene.timeline_markers[len(scene.timeline_markers)-1]
        current_marker.frame = i.frame
        current_marker.name = i.name
        if i.camera and bpy.data.objects[i.camera]:
            current_marker.camera = bpy.data.objects[i.camera]
    current_collection.index = current_collection.index



def rename_marker(self,context):
    context.scene.FRGLT_MarkerCollectionsIndex = context.scene.FRGLT_MarkerCollectionsIndex
    print("xo1")

class PROPS_FRGLT_Markers(bpy.types.PropertyGroup):
    """Group of properties representing an item in the list."""
    name : bpy.props.StringProperty(name="Name", default="Marker", update=rename_marker)
    frame : bpy.props.IntProperty(name="Frame",update=FRGLT_collection_select)
    camera : bpy.props.StringProperty(name="Camera",update=FRGLT_collection_select)

class PROPS_FRGLT_MarkerCollections(bpy.types.PropertyGroup):
    """Group of properties representing an item in the list."""
    name : bpy.props.StringProperty(name="Base Name", default="New Collection")
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
            #print(index)
            #layout.prop(item, "name", text="", emboss=False, icon = custom_icon)
            layout.prop(item,"frame", text="")
            layout.prop_search(item,"camera", bpy.data, "cameras",text="")
        elif self.layout_type in {'GRID'}:

            layout.alignment = 'CENTER'
            layout.label(text=item.name, icon = custom_icon)

class PANEL_FRGLT_MarkerCollections(bpy.types.Panel):
    """Baseclass for Marker Collection Panels"""
    bl_region_type = "UI"
    bl_label = "Marker Collections"
    bl_category = "Marker Manager"

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
        col.operator("marker_manager.new_collection", text="", icon='ADD')

        collection_index = context.scene.FRGLT_MarkerCollectionsIndex
        collection = collections[collection_index]          
        col.operator("marker_manager.delete_collection", text="", icon='REMOVE')

        list_sidebar_delete = col.row(align=True)
        list_sidebar_delete.operator("marker_manager.delete_marker", text="", icon='TRASH').delete_all = True



class PANEL_FRGLT_MarkerCollections_Dopesheet(PANEL_FRGLT_MarkerCollections):
    """Marker Collection Panel in the Dopesheet Editor"""
    bl_idname = "OBJECT_PT_froglet_marker_manager_collections_dopesheet"
    bl_space_type = "DOPESHEET_EDITOR"

class PANEL_FRGLT_Markers(bpy.types.Panel):
    """Baseclass for Panels"""
    bl_region_type = "UI"
    bl_label = "Marker Manager"
    bl_category = "Marker Manager"

    def draw(self, context):

        layout = self.layout
        scene = context.scene
        collections = scene.LIST_FRGLT_MarkerCollections
        collection_index = scene.FRGLT_MarkerCollectionsIndex        
        current_collection = collections[collection_index]  
        markers = current_collection.items
        current_frame = scene.frame_current
        
        row = layout.row()
        row.prop(current_collection,"frame_step", text="Frame Step", icon='ADD')

        list = layout.row()
        list.template_list("MARKERS_UL_FRGLT_Markers", "", current_collection, "items", current_collection, "index", rows=9, type="DEFAULT")

        list_sidebar = list.column(align=True)
        list_sidebar_add = list_sidebar.row(align=True)
        list_sidebar_add.operator("frglt.new_marker", text="", icon='ADD').step = 0

        
        if len(current_collection.items)>0:
            for i in current_collection.items:
                if i.frame==current_frame:
                    list_sidebar_add.enabled = False
        
        list_sidebar_add = list_sidebar.row(align=True)
        list_sidebar_add.operator("frglt.new_marker", text="", icon='TRACKING_FORWARDS_SINGLE').step = current_collection.frame_step
        
        list_sidebar.separator()
        if len(markers) > 0:
            list_sidebar_delete = list_sidebar.row(align=True)
            current_marker = current_collection.items[current_collection.index]
            list_sidebar_delete.operator("marker_manager.delete_marker", text="", icon='REMOVE')

      
            marker_details = layout.row().column()     
            if bpy.context.scene.tool_settings.lock_markers == True:
                marker_details.enabled = False

            marker_details.prop(current_marker, "name", text="Name", emboss=True)

            marker_details.prop(current_marker, "frame", text="Frame", emboss=True)

            marker_details.prop_search(current_marker,"camera", bpy.data, "cameras")
 

class PANEL_FRGLT_Markers_Dopesheet(PANEL_FRGLT_Markers):
    """Panel in the Dopesheet Editor"""
    bl_idname = "OBJECT_PT_froglet_marker_manager_dopesheet"
    bl_space_type = "DOPESHEET_EDITOR"

class PANEL_FRGLT_Markers_Graph(PANEL_FRGLT_Markers):
    """Panel in the Graph Editor"""
    bl_idname = "OBJECT_PT_froglet_marker_manager_graph"
    bl_space_type = "GRAPH_EDITOR"

class PANEL_FRGLT_Markers_NLA(PANEL_FRGLT_Markers):
    """Panel in the NLA Editor"""
    bl_idname = "OBJECT_PT_froglet_marker_manager_nla"
    bl_space_type = "NLA_EDITOR"

class PANEL_FRGLT_Markers_Sequencer(PANEL_FRGLT_Markers):
    """Panel in the Sequencer Editor"""
    bl_idname = "OBJECT_PT_froglet_marker_manager_sequencer"
    bl_space_type = "SEQUENCE_EDITOR"


class OP_FRGLT_Set_Frame(bpy.types.Operator):
    """Add a new item to the list. """

    bl_idname = "frglt.set_frame"
    bl_label = "Set current Frame"

    frame: bpy.props.IntProperty(default=0)
    index: bpy.props.IntProperty(default=0)

    def execute(self, context):
        scene = context.scene
        collections = scene.LIST_FRGLT_MarkerCollections
        collection_index = scene.FRGLT_MarkerCollectionsIndex        
        current_collection = collections[collection_index]  

        print("set current Frame",self.frame)
        scene.frame_current = current_collection.items[self.index].frame
        current_collection.index = self.index
        
        return{'FINISHED'}

class OP_FRGLT_Marker_Select(bpy.types.Operator):
    """Add a new item to the list."""

    bl_idname = "FRGLT.marker_select"
    bl_label = "Set current Frame"

    frame: bpy.props.IntProperty(default=0)

    def execute(self, context):
        scene = context.scene
        print("set current Frame",self.frame)
        scene.frame_current = self.frame
        scene.FRGLT_MarkerCollectionsIndex = scene.FRGLT_MarkerCollectionsIndex 
        return{'FINISHED'}

class OP_FRGLT_MarkerCollection_Select(bpy.types.Operator):
    """Add a new item to the list."""

    bl_idname = "FRGLT.markerCollection_select"
    bl_label = "Set current Frame"

    frame: bpy.props.IntProperty(default=0)

    def execute(self, context):
        scene = context.scene
        print("set current Frame",self.frame)
        scene.frame_current = self.frame
        scene.FRGLT_MarkerCollectionsIndex = scene.FRGLT_MarkerCollectionsIndex 
        return{'FINISHED'}

class OP_FRGLT_Marker_New(bpy.types.Operator):
    """Add a new item to the list."""

    bl_idname = "frglt.new_marker"
    bl_label = "Add a new item"

    step: bpy.props.IntProperty(default=0)

    def execute(self, context):
        scene = context.scene
        collections = scene.LIST_FRGLT_MarkerCollections
        ops = bpy.ops
        scene.frame_current += self.step
        current_frame = scene.frame_current

        if len(collections) == 0:
            ops.marker_manager.new_collection()
        
        collection_index = scene.FRGLT_MarkerCollectionsIndex
        
        if collection_index < 0:
            collection_index = 0
        
        current_collection = scene.LIST_FRGLT_MarkerCollections[collection_index]

        if current_collection.index < 0:
            current_collection.index = 0
        


        if len(current_collection.items)>0:
            for i in current_collection.items:
                if i.frame==current_frame:
                    return{'FINISHED'}


        marker_index = current_collection.index
        n = current_collection.items.add()
        n.frame = current_frame

        current_collection.index = len(current_collection.items) - 1
        
        
        scene.FRGLT_MarkerCollectionsIndex = scene.FRGLT_MarkerCollectionsIndex 
        return{'FINISHED'}


class OP_FRGLT_Marker_Delete(bpy.types.Operator):
    """Add a new item to the list."""

    bl_idname = "marker_manager.delete_marker"
    bl_label = "Delete Markers"

    delete_all: bpy.props.BoolProperty(default=False)

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
                print("delete Single") 
                current_collection.items.remove(current_collection.index)
                scene.FRGLT_MarkerCollectionsIndex = scene.FRGLT_MarkerCollectionsIndex 
        
   

        return{'FINISHED'}

class OP_FRGLT_MarkerCollections_New(bpy.types.Operator):
    """Add a new item to the list."""

    bl_idname = "marker_manager.new_collection"
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
    """Add a new item to the list."""

    bl_idname = "marker_manager.delete_collection"
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
            ops.marker_manager.new_collection()
            scene.FRGLT_MarkerCollectionsIndex = 0
        #else:
        #    scene.FRGLT_MarkerCollectionsIndex = collection_index

        return{'FINISHED'}


#test



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
    PANEL_FRGLT_Markers_Dopesheet,
   # FrogletMarkerManagerPanel_Graph,
   # FrogletMarkerManagerPanel_NLA,
   # FrogletMarkerManagerPanel_Sequencer,

]

def set_default_collection():
    print("set default collection")
    if len(bpy.context.scene.LIST_FRGLT_MarkerCollections) < 1:
        bpy.ops.marker_manager.new_collection()

    bpy.app.timers.unregister(set_default_collection)

    return 2.0


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

def unregister():
    
    for cls in register_classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.LIST_FRGLT_MarkerCollections
    del bpy.types.Scene.FRGLT_MarkerIndex
    del bpy.types.Scene.FRGLT_MarkerCollectionsIndex
    bpy.app.handlers.load_post.remove(set_default_collection)

if __name__ == "__main__":
    register()
