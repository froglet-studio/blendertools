bl_info = {
    "name": "Settings Manager - Froglet Studio Blender Tools",
    "author" : "Julius Hilker, Froglet Sudio",
    "version": (0 , 1),
    "blender": (3, 4, 1),
    "location": "3Dview + Scene",
    "description": "Manage complex setting chains",
    "warning": "Work in Progress",
    "category": "Settings",
    "doc_url": "https://github.com/froglet-studio/blendertools/wiki/Blendertools-by-Froglet-Studio"
}

import bpy 
import os
import json 
from datetime import datetime
from bpy.types import (Menu,Operator,PropertyGroup,UIList,Panel,Scene)
from bpy.props import (IntProperty, BoolProperty, StringProperty, CollectionProperty,FloatProperty,EnumProperty,PointerProperty)
from bpy.utils import (register_class, unregister_class)

# FUNCTIONS

def populate_enum_viewlayers(scene, context):

    current_view_layers = []

    for view_layer in bpy.context.scene.view_layers.items():
        current_view_layers.append((view_layer[0],view_layer[0], ""),)
 
    return current_view_layers

def traverse_tree(t):
    yield t
    for child in t.children:
        yield from traverse_tree(child)

def get_setting_types():
    item_types = {
    "Frames" : {
        "start" : {"default":""},
        "end" : {"default":""},
        "frame_step" : {"default":"1"},
        "current_frame" : {"default":""},
    },
    "Output" : {
        "output": {"default":""},
        "filename" : {"default":""},
        "format": {"default":""},
        "image_quality": {"default":""},
        "image_compression": {"default":""},
        "overwrite": {"default":""}
    },
    "Scene123" : {
         "camera": {"default":""},
         "view_layer": {"default":""}
    }, 
    "resolution":{
        "resolution_x": {"default":""},
        "resolution_y": {"default":""},
        "resolution_percentage": {"default":""}
    },
    "cycles":{


        "cycles_samples_render_min": {"default":""},
        "cycles_samples_render_max": {"default":""},
        "cycles_samples_viewport_min": {"default":""},
        "cycles_samples_viewport_max": {"default":""}


    },
    "evee": {
        "evee_samples_render": {"default":""},
        "evee_samples_viewport": {"default":""}

    },
        "Renderer": {
        "render_engine": {"default":""}

    }

    } 



    return item_types

def get_settings(current,out,check):
    settings = bpy.context.scene.FRGLT_settings
    current = settings.get_by_id(current.id)
    


    if current.parent != 0 and current.id not in check:   
        check.append(current.id)     
        for i in settings.settings:
            if current.parent == i.id:           
                out = get_settings(i,out,check)
    
    for item in current.items:
        out[item.name]=getattr(item,item.name)

    return out

def set_settings(items):


        scene = bpy.context.scene
        layer_coll_master = bpy.context.view_layer.layer_collection
        lc = bpy.context.view_layer.layer_collection
        print(dir(lc))
        for i in lc.children:
            print(i)
        

        for c in scene.FRGLT_settings.current().collections:
            if c.collection is not None:
                bpy.data.collections[c.collection.name].hide_viewport = c.viewport_disable
                bpy.data.collections[c.collection.name].hide_render = c.render_disable
                #bpy.data.collections[c.collection.name].hide_render = c.exclude
                bpy.data.collections[c.collection.name].hide_select = c.selection_disable
                bpy.data.collections[c.collection.name].hide_viewport = c.viewport_hide
                #bpy.data.collections[c.collection.name].hide_render = c.holdout
                #bpy.data.collections[c.collection.name].hide_render = 

                coll_name = c.collection.name


                for layer_coll in traverse_tree(layer_coll_master):
                    if layer_coll.collection.name == coll_name:
                        layer_coll.indirect_only = c.indirect_only
                        layer_coll.holdout = c.holdout
                        layer_coll.exclude = c.exclude
                        break
           
          
            
        for c in scene.FRGLT_settings.current().objects:
            if c.object is not None:
                bpy.data.objects[c.object.name].hide_viewport = c.viewport_disable
                bpy.data.objects[c.object.name].hide_render = c.render_disable
                bpy.data.objects[c.object.name].hide_select = c.selection_disable
                

                #coll_name = c.collection.name


                #for layer_coll in traverse_tree(layer_coll_master):
                #    if layer_coll.collection.name == coll_name:
                #        layer_coll.indirect_only = c.indirect_only
                #        layer_coll.holdout = c.holdout
                #        layer_coll.exclude = c.exclude
                #        break
           
          
                
       
            

        output = ""
        format = ""
        for item in items:
            if item == "view_layer":
                #scene.frame_start = items[item]

                vl = scene.view_layers[items[item]]
                bpy.context.window.view_layer = vl
                #print(items[item])

            if item == "start":
                scene.frame_start = items[item]
            
            if item == "end":
                scene.frame_end = items[item]
            if item == "current_frame":
                scene.frame_current = items[item]

            if item == "frame_step":
                scene.frame_step = items[item]            

            if item == "camera":
                scene.camera = items[item]

            if item == "overwrite":
                scene.render.use_overwrite = items[item]
            if item == "image_quality":
                scene.render.image_settings.quality = items[item]
            if item == "image_compression":
                scene.render.image_settings.compression = items[item]
            if item == "resolution_percentage":
                bpy.context.scene.render.resolution_percentage = items[item]
            if item == "resolution_x":
                bpy.context.scene.render.resolution_x= items[item]
            if item == "resolution_y":
                bpy.context.scene.render.resolution_y= items[item]

            if item == "evee_samples_render":
                bpy.context.scene.eevee.taa_render_samples= items[item]
            if item == "evee_samples_viewport":
                bpy.context.scene.eevee.taa_samples= items[item]
            if item == "cycles_samples_render_min":
                bpy.context.scene.cycles.adaptive_min_samples= items[item]
            if item == "cycles_samples_render_max":
                bpy.context.scene.cycles.samples= items[item]
            if item == "cycles_samples_viewport_min":
                bpy.context.scene.cycles.preview_adaptive_min_samples= items[item]
            if item == "cycles_samples_viewport_max":
                bpy.context.scene.cycles.preview_samples= items[item]
            if item == "render_engine":
                bpy.context.scene.render.engine = items[item]
        


        if "output" in items:
            scene.render.filepath = items["output"]
            output = items["output"]+"/"

        if "format" in items:
            scene.render.image_settings.file_format = items["format"]
            format = "."+items["format"]

        if "filename" in items:
            scene.render.filepath = output+items["filename"]+format

def FRGLT_settings_select(self,context):
    
    settings = context.scene.FRGLT_settings
    current = settings.current()
    items = current.items 
    set_settings(get_settings(current,{},[]))

def prop_unique_name(self,context):

    scene = bpy.context.scene
    settings = scene.LIST_FRGLT_settings
    names = []
    for setting in settings:       
        names.append(setting.name)
        if self.name in names:
            print("duplicate name")

def filter_cameras(self, object):
    return object.type == 'CAMERA'

def filter_scene(self, scene):
    for i in bpy.context.scene.LIST_FRGLT_settings:
        print(i.name)
    #print(len(scene.FRGLT_settings_index))
    return "papa"

def set_category(self,value):
    print(bpy.context.scene.FRGLT_settings)
    print("Set Cat",value)

def category_items(general=True):

    items = [
        ("edit","Edit",""),
        ("render","Render","")
    ]

    if general != False:
        items.append(("other","Other","For base settings"))
    return items

#Menu

class FRGLT_MENU_settings_parent(Menu):
    bl_idname = "FRGLT_MT_settings_parent_menu"
    bl_label = "Select a parent"
    index: IntProperty(default=0) 

    def draw(self, context):
        scene = context.scene 
        settings = context.scene.FRGLT_settings
        current = settings.current()

        row = self.layout.row()
        row.operator("frglt.settings_add_parent",text="None").id = 0
        row = self.layout.row()
        row.separator()
        for item in settings.settings:
            if item.id != current.id:     
                #if item.parent != current.id:                
                row = self.layout.row()
                row.operator("frglt.settings_add_parent",text=item.name+" ("+str(item.id)+") ").id = item.id

class FRGLT_MENU_settings_format(Menu):
    bl_idname = "FRGLT_MT_settings_format_menu"
    bl_label = "Select Image Format"
    index: IntProperty(default=0) 

    def draw(self, context):
        scene = context.scene 
        render = scene.render.image_settings

        image_formats = ["BMP","Iris","PNG","JPEG","JPEG 2000","Targe","Targa Raw","Cineon","DPX","OpenEXR MultiLayer","OpenEXR","Radiance HDR","TIFF","WebP"]
        video_formats = ["AVI JPEG","AVI RAW","FFmpeg Video"]
        layout = self.layout
        
        base_row = layout.row()
        col = base_row.column()


        for format in image_formats:
        
            row = col.row()
            opr = row.operator("frglt.settings_format_apply",text=format).format = format  
            opr.index = self.index
        

        row = col.row()
        row.label(text="Image")  

        col = base_row.column()

        for format in video_formats:
         
            row = col.row()
            opr = row.operator("frglt.settings_format_apply",text=format).format = format   
            opr.index = self.index 

        row = col.row()
        row.label(text="Movie")  
    
class FRGLT_settings_menu(Menu):
    bl_idname = "FRGLT_MT_settings_menu"
    bl_label = "Add"

    def draw(self, context):
        scene = context.scene 

        settings = scene.FRGLT_settings 

        types = get_setting_types()

        current = settings.current()
        exclude = []
        
        for i in current.items:
            exclude.append(i.name)
        
        layout = self.layout
       
        
        for category in types:
            cat_items = []

            for item in types[category]: 
                          
                if item not in exclude:
                    cat_items.append(item)

            if len(cat_items)>0:
                col = layout.column()
                #layout.label(text=current.name)  

                for i in cat_items:
                    row = col.row()  
                    row.operator("frglt.settings_add_item",text="  "+i).item_id=i   
                
                col.label(text=category)
                col.separator()            
                
#Operators


class FRGLT_OP_settings_render_animation(Operator):
    """render this settings"""

    bl_idname = "frglt.settings_render_animation"
    bl_label = "Apply current Settings"
    index: IntProperty(default=0)

    def execute(self, context):
        scene = context.scene  
        old_index = scene.FRGLT_settings.index
        scene.FRGLT_settings.index = self.index
        #bpy.ops.render.render(animation=True, use_viewport=True)   
        bpy.ops.render.render({'dict': "override"},'INVOKE_DEFAULT',animation=True)
        #scene.FRGLT_settings.index = old_index  
        #print(self.index)
        return{'FINISHED'}

class FRGLT_OP_settings_render_frame(Operator):
    """render this settings"""

    bl_idname = "frglt.settings_render_frame"
    bl_label = "Apply current Settings"
    index: IntProperty(default=0)

    def execute(self, context):
        scene = context.scene  
        old_index = scene.FRGLT_settings.index
        scene.FRGLT_settings.index = self.index
        bpy.ops.render.render({'dict': "override"},'INVOKE_DEFAULT',use_viewport=True)
        #bpy.ops.render.render(animation=False,write_still=True,use_viewport=True)   
        #scene.FRGLT_settings.index = old_index  
        #print(self.index)
        return{'FINISHED'}

class FRGLT_OP_settings_format_apply(Operator):
    """Apply current Settings"""

    bl_idname = "frglt.settings_format_apply"
    bl_label = "Apply current Settings"
    index: IntProperty(default=0)   
    format: StringProperty(default="")

    def execute(self, context):
        scene = context.scene
        
        

        return{'FINISHED'}

class FRGLT_OP_settings_apply_current(Operator):
    """Apply current Settings"""

    bl_idname = "frglt.apply_current_settings"
    bl_label = "Apply current Settings"
    index: IntProperty(default=0)   

    def execute(self, context):
        scene = context.scene
        
        

        return{'FINISHED'}

class FRGLT_OP_settings_set_item(Operator):
    """Set settings item"""

    bl_idname = "frglt.settings_set_item"
    bl_label = "Add a set"
    index: IntProperty(default=0)

    def execute(self, context):
        scene = context.scene
        
        scene.LIST_FRGLT_settings.add()
        scene.FRGLT_settings_index = len(context.scene.LIST_FRGLT_settings)-1

        return{'FINISHED'}

class FRGLT_OP_settings_add(Operator):
    """Create a set"""

    bl_idname = "frglt.settings_add"
    bl_label = "Add a set"
    mode : StringProperty(default="set")

    def execute(self, context):
        scene = context.scene
        
        if self.mode=="set":
            scene.FRGLT_settings.add_settings()       
        elif self.mode=="collections":
            scene.FRGLT_settings.current().collections.add()
        elif self.mode=="objects":
            scene.FRGLT_settings.current().objects.add()



       
        return{'FINISHED'}

class FRGLT_OP_settings_remove(Operator):
    """Remove a set"""

    bl_idname = "frglt.settings_remove"
    bl_label = "Remove current set"
    mode: StringProperty(default="set")
    def execute(self, context):
        scene = context.scene
        
        if self.mode=="set":
            print("remove set")
            scene.FRGLT_settings.remove_settings()
        elif self.mode=="collections":
            scene.FRGLT_settings.current().collections.remove(scene.FRGLT_settings.current().collections_index)


            
        return{'FINISHED'}

class FRGLT_OP_settings_add_item(Operator):
    """Adds a new item to the current set."""

    bl_idname = "frglt.settings_add_item"
    bl_label = "Add"
    item_id: StringProperty(default="peter")

    def execute(self, context):
        
        #print(self.item_id)
        context.scene.FRGLT_settings.add_item(self.item_id)

            
        return{'FINISHED'}

class FRGLT_OP_settings_remove_item(Operator):
    """Removes this item from the current set"""

    bl_idname = "frglt.settings_remove_item"
    bl_label = "Remove"
    index: IntProperty(default=0)

    def execute(self, context):

        current = context.scene.FRGLT_settings.remove_item(self.index)       
        
            
        return{'FINISHED'}

class FRGLT_OP_settings_add_parent(Operator):
    """Removes this item from the current set"""

    bl_idname = "frglt.settings_add_parent"
    bl_label = "Add Parent"
    id : IntProperty()

    def execute(self, context):
        settings = context.scene.FRGLT_settings
        settings.current().parent=self.id
        

        return{'FINISHED'}

#Property Groups


class FRGLT_settings_collections(PropertyGroup):
    collection: PointerProperty(type=bpy.types.Collection, name="My Collection")
    viewport_hide: BoolProperty(name="Show in Viewport",default=True)
    viewport_disable: BoolProperty(name="Show in Viewport",default=True)
    selection_disable: BoolProperty(name="Show in Viewport",default=True)
    exclude:  BoolProperty(name="Show in Viewport",default=True)
    holdout: BoolProperty(name="Show in Viewport",default=False)
    indirect_only: BoolProperty(name="Show in Viewport",default=False)
    render_disable: BoolProperty(name="Show in Viewport",default=True)

class FRGLT_settings_objects(PropertyGroup):
    object: PointerProperty(type=bpy.types.Object, name="My Collection")
    viewport_hide: BoolProperty(name="Show in Viewport",default=True)
    viewport_disable: BoolProperty(name="Show in Viewport",default=True)
    selection_disable: BoolProperty(name="Show in Viewport",default=True)
    render_disable: BoolProperty(name="Show in Viewport",default=True)


class FRGLT_settings_categories(PropertyGroup):
    name: StringProperty(name="Category Name",default="Test Category")

 

class FRGLT_settings_item(PropertyGroup):
    name: StringProperty(name="name")
    start : IntProperty(name="frames - start")
    end : IntProperty(name="frames - endx")
    frame_step: IntProperty(name="Frame Step",max=100,min=1)
    current_frame: IntProperty(name="Current Frame")
    camera: PointerProperty(name = "my pointer", description = "my descr", type=bpy.types.Object, poll=filter_cameras) 
    #camera: StringProperty(name="scene - camera", default=bpy.context.scene.camera.name)
    output: StringProperty(name="output folder",subtype='DIR_PATH')
    filename: StringProperty(name="Filename",subtype='FILE_NAME')
    format: EnumProperty("PNG",items=[
                        ("BMP","BMP",""),
                        ("IRIS","Iris",""),
                        ("PNG","PNG",""),
                        ("JPEG","JPEG",""),
                        ("JPEG2000","JPEG 2000",""),
                        ("TARGA","Targa",""),
                        ("TARGA_RAW","Targa Raw",""),
                        ("CINEON","Cineon",""),
                        ("DPX","DPX",""),
                        ("OPEN_EXR_MULTILAYER","OpenEXR MultiLayer",""),
                        ("OPEN_EXR","OpenEXR",""),
                        ("HDR","Radiance HDR",""),
                        ("TIFF","TIFF",""),
                        ("WEBP","WebP",""),
                        ("AVI_JPEG","AVI JPEG",""),
                        ("AVI_RAW","AVI RAW",""),
                        ("FFMPEG","FFmpeg Video",".mp4")])
    image_quality: IntProperty(name="Image quality",default=100,max=100,min=0,subtype='PERCENTAGE')
    image_compression: IntProperty(name="Image compression",max=100,min=0,subtype='PERCENTAGE')
    overwrite: BoolProperty(name="Overwrite images when render")
    resolution_x:IntProperty(name="frames - start") 
    resolution_y:IntProperty(name="frames - start")
    resolution_percentage: IntProperty(name="frames - start",max=100,min=0,subtype='PERCENTAGE')
    evee_samples_render: IntProperty(name="frames - start")
    evee_samples_viewport: IntProperty(name="frames - start")
    cycles_samples_render_min: IntProperty(name="frames - start")
    cycles_samples_render_max: IntProperty(name="frames - start")
    cycles_samples_viewport_min: IntProperty(name="frames - start")
    cycles_samples_viewport_max: IntProperty(name="frames - start")
    render_engine: EnumProperty("BLENDER_EVEE",items=[
                        ("BLENDER_EEVEE","EVEE",""),
                        ("BLENDER_WORKBENCH","Workbench",""),
                        ("CYCLES","Cycles","")])
    view_layer: EnumProperty(items=populate_enum_viewlayers)

class FRGLT_settings(PropertyGroup): 
    """Group of properties representing an item in the list."""
      
    name : StringProperty(name="Name", default="Settings")
    id : IntProperty(name="id")
    items : CollectionProperty(type = FRGLT_settings_item) 
    collections_index : IntProperty(name="Index for collections",default=0) 
    collections: CollectionProperty(type = FRGLT_settings_collections)
    objects_index : IntProperty(name="Index for collections",default=0) 
    objects: CollectionProperty(type = FRGLT_settings_objects)
    parent: IntProperty(name="parent id")
    #parent: StringProperty(name="parent")
    quick: BoolProperty(name="quick",default=False)
    category: EnumProperty("edit", items=category_items())
     
    
 

class FRGLT_settings_manager(PropertyGroup):
    settings: CollectionProperty(type = FRGLT_settings)
    id: IntProperty(name = "Settings id index", default = 1)
    index: IntProperty(name = "Settings list index", default = 0, update=FRGLT_settings_select)
    #types: StringProperty(name="Item Types", default=get_setting_types())
    category: EnumProperty("edit", items=category_items())
    category_types: CollectionProperty(type = FRGLT_settings_categories)  



    def get_by_id(self,id):
        for i in self.settings:
            if i.id == id:
                return i
        return False
    
    def current(self):
        return self.settings[self.index]

    def len(self):
        return len(self.settings)

    def add_settings(self):

        self.settings.add().id = self.id
        self.index = len(self.settings)-1        
        self.current().name = self.current().name
        self.current().category = bpy.context.scene.FRGLT_settings.category
        self.id += 1
    
    def remove_settings(self):
        
        self.settings.remove(self.index)
        
        if self.index == self.len():
            self.index = self.len()-1
        
        if self.len() == 0:
            self.id = 1

    def add_item(self,item_id):
        self.current().items.add().name = item_id

    def remove_item(self,item_id): 
        self.current().items.remove(item_id)

#UIList
class FRGLT_UL_settings_collections(UIList):
    """List of settings"""

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        
        settings = context.scene.FRGLT_settings
        if self.layout_type in {'DEFAULT', 'COMPACT'}:

            if index==settings.current().collections_index:
                layout.prop(item,"collection",text="",emboss=True)
            else:
                if item.collection is not None:
                    layout.label(text=item.collection.name,icon="OUTLINER_COLLECTION")
                else:
                    layout.label(text="Select Collection",icon="COLLECTION_NEW")

            
            if item.viewport_hide == True:
                viewport_hide_icon = "HIDE_ON"
            else:
                viewport_hide_icon= "HIDE_OFF"

            if item.render_disable == True:
                render_disable_icon = "RESTRICT_RENDER_ON"
            else:
                render_disable_icon= "RESTRICT_RENDER_OFF"
            
            if item.exclude == False:
                exclude_icon = "CHECKBOX_HLT"
            else:
                exclude_icon = "CHECKBOX_DEHLT"

            if item.selection_disable == False:
                selection_disable_icon = "RESTRICT_SELECT_OFF"
            else:
                selection_disable_icon = "RESTRICT_SELECT_ON"

            if item.viewport_disable == False:
                viewport_disable_icon = "RESTRICT_VIEW_OFF"
            else:
                viewport_disable_icon = "RESTRICT_VIEW_ON"

            if item.holdout == False:
                holdout_icon = "HOLDOUT_OFF"
            else:
                holdout_icon = "HOLDOUT_ON"

            if item.indirect_only == False:
                indirect_only_icon = "INDIRECT_ONLY_OFF"
            else:
                indirect_only_icon = "INDIRECT_ONLY_ON"







            layout.prop(item,"exclude",text="",icon=exclude_icon,emboss=False)
            layout.prop(item,"selection_disable",text="",icon=selection_disable_icon,emboss=False)
            layout.prop(item,"viewport_hide",text="",icon=viewport_hide_icon,emboss=False)
            layout.prop(item,"viewport_disable",text="",icon=viewport_disable_icon,emboss=False)
            layout.prop(item,"render_disable",text="",icon=render_disable_icon,emboss=False)
            layout.prop(item,"holdout",text="",icon=holdout_icon,emboss=False)

            row = layout.row()
            if item.holdout == True:
               row.enabled = False 
            row.prop(item,"indirect_only",text="",icon=indirect_only_icon,emboss=False)
          

        elif self.layout_type in {'GRID'}:

            layout.alignment = 'CENTER'
            layout.prop(item,"name")
    

class FRGLT_UL_settings_objects(UIList):
    """List of settings"""

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        
        settings = context.scene.FRGLT_settings
        if self.layout_type in {'DEFAULT', 'COMPACT'}:

            if index==settings.current().objects_index:
                layout.prop(item,"object",text="",emboss=True)
            else:
                if item.object is not None:
                    layout.label(text=item.object.name,icon="OUTLINER_COLLECTION")
                else:
                    layout.label(text="Select Object",icon="COLLECTION_NEW")

            
            if item.viewport_hide == True:
                viewport_hide_icon = "HIDE_ON"
            else:
                viewport_hide_icon= "HIDE_OFF"

            if item.render_disable == True:
                render_disable_icon = "RESTRICT_RENDER_ON"
            else:
                render_disable_icon= "RESTRICT_RENDER_OFF"
         
    

            if item.selection_disable == False:
                selection_disable_icon = "RESTRICT_SELECT_OFF"
            else:
                selection_disable_icon = "RESTRICT_SELECT_ON"

            if item.viewport_disable == False:
                viewport_disable_icon = "RESTRICT_VIEW_OFF"
            else:
                viewport_disable_icon = "RESTRICT_VIEW_ON"

        







           
            layout.prop(item,"selection_disable",text="",icon=selection_disable_icon,emboss=False)
            layout.prop(item,"viewport_hide",text="",icon=viewport_hide_icon,emboss=False)
            layout.prop(item,"viewport_disable",text="",icon=viewport_disable_icon,emboss=False)
            layout.prop(item,"render_disable",text="",icon=render_disable_icon,emboss=False)

          

        elif self.layout_type in {'GRID'}:

            layout.alignment = 'CENTER'
            layout.prop(item,"name")
    


class FRGLT_UL_settings(UIList):
    """List of settings"""

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        
        settings = context.scene.FRGLT_settings
        if self.layout_type in {'DEFAULT', 'COMPACT'}:

            icon = "OUTLINER_COLLECTION"
            row = layout.row()
            ic = "BLANK1"

            
            if item.id == settings.current().parent:
                ic = "DECORATE_LINKED"
            
            
            row.prop(item,"name",text="",emboss=False,icon=ic)
            row.label(text="id: "+str(item.id))
            if item.parent != "":
                
                if item.name == item.parent:
                    use_icon = "ERROR"

                parent = settings.get_by_id(item.parent)
                if parent != False:
                    row.label(text=parent.name+" (id: "+str(parent.id)+" category: "+parent.category+")",icon="FILE_PARENT")
                
                elif parent == False and item.parent != 0:

                    row.label(text="parent not found",icon="ERROR")
                else:
                    row.label(text="")
                    
                

        elif self.layout_type in {'GRID'}:

            layout.alignment = 'CENTER'
            layout.prop(item,"name")
    
    def filter_items(self, context, data, propname):
        """Filter and order items in the list."""
        settings = context.scene.FRGLT_settings
        category = settings.category
        items = getattr(data, propname)
        filtered = []
        ordered = []

        filtered = [self.bitflag_filter_item] * len(items)

        i = 0
        for item in items:        

            if item.category != category:
                
                filtered[i] &= ~self.bitflag_filter_item    

                        
            i += 1

        return filtered,ordered

class FRGLT_UL_settings_quick(UIList):
    """List of settings"""

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
                   

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            
            icon = "OUTLINER_COLLECTION"
            row = layout.row()
            row.label(text=item.name)   
            row.operator("frglt.settings_render_animation",text="",icon="RENDER_ANIMATION").index = index
            row.operator("frglt.settings_render_frame",text="",icon="IMAGE_DATA").index = index

        elif self.layout_type in {'GRID'}:

            layout.alignment = 'CENTER'
            row.label(text=item.name)
    
    def filter_items(self, context, data, propname):
        """Filter and order items in the list."""
        settings = context.scene.FRGLT_settings
        category = settings.category
        items = getattr(data, propname)
        filtered = []
        ordered = []

        filtered = [self.bitflag_filter_item] * len(items)

        i = 0
        for item in items:        

            if item.quick != True or item.category != category:
                
                filtered[i] &= ~self.bitflag_filter_item    

                        
            i = i+1

        return filtered,ordered

#PANELS



class FRGLT_PANEL_settings_quick(Panel):
    """Creates a Panel in the 3D_VIEW properties window"""
    bl_label = "Settings Manager Quick Acces"
    bl_idname = "FRGLT_PT_settings_quick"
    bl_category = "Settings"

    def draw(self, context):        
        scene = context.scene
        settings = context.scene.FRGLT_settings
        layout = self.layout
        list = layout.row()
        list.prop(settings,"category",text="Select Category",expand=True)
        list = layout.row()
        list.template_list("FRGLT_UL_settings_quick", "", scene.FRGLT_settings, "settings", scene.FRGLT_settings, "index",rows=9, type="DEFAULT")

class FRGLT_PANEL_settings_quick_3D(FRGLT_PANEL_settings_quick): 
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'




class FRGLT_settings_panel:
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene" 
#comment

class FRGLT_settings_panel_main(FRGLT_settings_panel, bpy.types.Panel):
    bl_idname = "FRGLT_settings_panel_main"
    bl_label = "Settings Manager"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene" 

    def draw(self, context):
       
        layout = self.layout
        scene = context.scene
        settings = scene.FRGLT_settings
        list = layout.row()
        list.prop(settings,"category",text="Select Category",expand=True)
        list = layout.row()
        list.template_list("FRGLT_UL_settings", "", settings, "settings", settings, "index",rows=9, type="DEFAULT")
        
        list_sidebar = list.column(align=True)
        list_sidebar_add = list_sidebar.row(align=True)
        list_sidebar_add.operator("frglt.settings_add", text="", icon='ADD')
        list_sidebar_add = list_sidebar.row(align=True)
        list_sidebar_add.operator("frglt.settings_remove", text="", icon='REMOVE').mode="set"
        

class FRGLT_settings_panel_cfg(FRGLT_settings_panel, bpy.types.Panel):
    bl_parent_id = "FRGLT_settings_panel_main"
    bl_label = "Configure"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.FRGLT_settings
        
        if settings.len()>0: 
            
            box = layout.box()

            current = settings.current()

            row = box.row()
            
            row.prop(current,"quick",text="Show in quick panel")
            row.label(text="category")
            row.prop(current,"category",text="Category",expand=True)
            row = box.row()
            use_icon = "FILE_PARENT"
            if current.parent == current.name:
                use_icon = "ERROR" 
            
            parent = settings.get_by_id(current.parent)
            ICON = "FILE_PARENT"
            if parent != False:
                label = parent.name
            
            elif parent == False and current.parent != 0:
                label = "ERROR: Parent not Found"+str(current.parent)
                ICON = "ERROR"
                
            elif parent == 0:
                label = "Select Parent"


            
            row.menu("FRGLT_MT_settings_parent_menu",text=label,icon=ICON)


class FRGLT_settings_panel_collections(FRGLT_settings_panel, bpy.types.Panel):
    bl_parent_id = "FRGLT_settings_panel_main"
    bl_label = "Collections"

    def draw(self, context):
        layout = self.layout
        current = context.scene.FRGLT_settings.current()
    

        list = layout.row()
        list.template_list("FRGLT_UL_settings_collections", "", current, "collections", current, "collections_index",rows=9, type="DEFAULT")
        
        list_sidebar = list.column(align=True)
        list_sidebar_add = list_sidebar.row(align=True)
        list_sidebar_add.operator("frglt.settings_add", text="", icon='ADD').mode = "collections"
        list_sidebar_add = list_sidebar.row(align=True)
        list_sidebar_add.operator("frglt.settings_remove", text="", icon='REMOVE').mode = "collections"


class FRGLT_settings_panel_objects(FRGLT_settings_panel, bpy.types.Panel):
    bl_parent_id = "FRGLT_settings_panel_main"
    bl_label = "Objects"

    def draw(self, context):
        layout = self.layout
        current = context.scene.FRGLT_settings.current()
    

        list = layout.row()
        list.template_list("FRGLT_UL_settings_objects", "", current, "objects", current, "objects_index",rows=9, type="DEFAULT")
        
        list_sidebar = list.column(align=True)
        list_sidebar_add = list_sidebar.row(align=True)
        list_sidebar_add.operator("frglt.settings_add", text="", icon='ADD').mode = "objects"
        list_sidebar_add = list_sidebar.row(align=True)
        list_sidebar_add.operator("frglt.settings_remove", text="", icon='REMOVE').mode = "objects"



class FRGLT_settings_panel_attr(FRGLT_settings_panel, bpy.types.Panel):
    bl_parent_id = "FRGLT_settings_panel_main"
    bl_label = "Attributes"

    def draw(self, context):
        settings = context.scene.FRGLT_settings
        item_stack = {}
        types = get_setting_types()
        for cat in types:
            for i in types[cat]:
                item_stack[i] = types[cat][i]
        layout = self.layout
        
        current = settings.current()

        box = layout.box()

        box_row = box.row()
        box_row.menu("FRGLT_MT_settings_menu",text="Add Attribute")
        item_index = 0
        
        for item in current.items:
            box_row = box.box() 
            box_row = box_row.column()     
            box_row = box_row.row()   
            #box_row.label(text=item.name)  
            if "prop" in item_stack[item.name]:
                print("Special prop",item_stack[item.name]["prop"])
            else:
                box_row.prop(item,item.name,text=item.name)


            box_row.operator("frglt.settings_remove_item", text="", icon='REMOVE').index = item_index
            item_index = item_index+1     


#Register Variables

register_operators = [ 
    FRGLT_OP_settings_add_item,
    FRGLT_OP_settings_remove_item,
    FRGLT_OP_settings_add,
    FRGLT_OP_settings_remove,
    FRGLT_settings_menu,
    FRGLT_MENU_settings_format,
    FRGLT_OP_settings_apply_current,
    FRGLT_OP_settings_format_apply,
    FRGLT_MENU_settings_parent,
    FRGLT_OP_settings_add_parent,
    FRGLT_OP_settings_render_animation,
    FRGLT_OP_settings_render_frame

]
 
register_properties = [ 
    FRGLT_settings_collections,
    FRGLT_settings_objects,
    FRGLT_settings_categories,
    FRGLT_settings_item,
    FRGLT_settings,
    FRGLT_settings_manager   
]
 
register_list = [
    FRGLT_UL_settings_collections,
    FRGLT_UL_settings_objects,
    FRGLT_UL_settings,
    FRGLT_UL_settings_quick
]
 
register_panels= [
    FRGLT_PANEL_settings_quick_3D,
    FRGLT_settings_panel_main,
    FRGLT_settings_panel_cfg,
    FRGLT_settings_panel_collections,
    FRGLT_settings_panel_objects,
    FRGLT_settings_panel_attr,
   
    
]

#Item Type Definitions

#Register Functions

def register():

    for cls in register_operators:
        register_class(cls)

    for cls in register_properties:
        register_class(cls)
    

    Scene.FRGLT_settings = PointerProperty(type=FRGLT_settings_manager,name="The Manager")
   

    for cls in register_list:
        register_class(cls)
     
    for cls in register_panels:
        register_class(cls) 
            
def unregister():

    for cls in register_operators:
        unregister_class(cls)

    for cls in register_properties:
        unregister_class(cls)
    
    
    del Scene.FRGLT_settings
        
    for cls in register_list:
        unregister_class(cls)
    
    for cls in register_panels:
        unregister_class(cls)
    
if __name__ == "__main__":
    register()