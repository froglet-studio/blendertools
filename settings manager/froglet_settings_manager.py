bl_info = {
    "name": "Settings Manager - Froglet Studio Blender Tools",
    "author" : "Julius Hilker, Froglet Sudio",
    "version": (0 , 5),
    "blender": (3, 4, 1),
    "location": "3Dview + Scene",
    "description": "Manage complex setting chains",
    "warning": "Work in Progress",
    "category": "Settings",
    "doc_url": "https://github.com/froglet-studio/blendertools/wiki/Blendertools-by-Froglet-Studio"
}
import pprint
from bpy_extras.io_utils import (ExportHelper,ImportHelper)
import json
import bpy 
import os
import json 
import platform
from bpy.app.handlers import persistent
from bpy.types import UI_UL_list
from datetime import datetime
from bpy.types import (Menu,Operator,PropertyGroup,UIList,Panel,Scene,AddonPreferences)
from bpy.props import (IntProperty, BoolProperty, StringProperty, CollectionProperty,FloatProperty,EnumProperty,PointerProperty)
from bpy.utils import (register_class, unregister_class)

# FUNCTIONS

_item_map = dict()

def _make_item(id, name, descr, icon, uid):
    lookup = f"{str(id)}\0{str(name)}\0{str(descr)}\0{str(icon)}\0{str(uid)}"
    if not lookup in _item_map:
        _item_map[lookup] = (id, name, descr, icon, uid)
    return _item_map[lookup]

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
    print("get settings",current.id)
    manager = bpy.context.scene.FRGLT_manager
    
    if current.parent != -1 and current.id not in check:   
        check.append(current.id)     
        for i in manager.sets:
            if current.parent == i.id:           
                out = get_settings(i,out,check)

    if current.default.collections.use_default == True:
        out["default_collections"] = {
            "exclude": current.default.collections.exclude,
            "selection_disable": current.default.collections.selection_disable,
            "viewport_hide": current.default.collections.viewport_hide,
            "viewport_disable": current.default.collections.viewport_disable,
            "render_disable": current.default.collections.render_disable,
            "holdout":current.default.collections.holdout,
            "indirect_only":current.default.collections.indirect_only
        }
    


    if current.default.objects.use_default == True:
        out["default_objects"] = {
            "object": current.default.objects.object,
            "viewport_hide": current.default.objects.viewport_hide,
            "viewport_disable": current.default.objects.viewport_disable,
            "selection_disable": current.default.objects.selection_disable,
            "render_disable": current.default.objects.render_disable
            
        }

    if "attrs" not in out and len(current.attrs)>0:
        out["attrs"] = {}
    
    if "collections" not in out and len(current.collections)>0:
        out["collections"] = {}
    
    if "objects" not in out and len(current.objects)>0:
        out["objects"] = {}

    
    for item in current.objects:
        if item.object is not None:
            out["objects"][item.object.name] = {
                "object": item.object,
                "viewport_hide": item.viewport_hide,
                "viewport_disable": item.viewport_disable,
                "selection_disable": item.selection_disable,
                "render_disable": item.render_disable

            }

    for item in current.collections:
        if item.collection is not None:
            out["collections"][item.collection.name] = {
                "collection": item.collection,
                "viewport_hide": item.viewport_hide,
                "viewport_disable": item.viewport_disable,
                "selection_disable": item.selection_disable,
                "exclude": item.exclude,
                "holdout":item.holdout,
                "indirect_only":item.indirect_only,
                "render_disable":item.render_disable

            }





    for item in current.attrs:
        out["attrs"][item.name]=getattr(item,item.name)

    #print(out)
    return out

def set_settings(items):
        #print(items)
        scene = bpy.context.scene
        manager = scene.FRGLT_manager
        current_set = manager.sets[manager.index.active]
       
        layer_coll_master = bpy.context.view_layer.layer_collection
        lc = bpy.context.view_layer.layer_collection

        output = ""
        format = ""
        
        if "default_collections" in items:
           
            for current_collection in bpy.data.collections:
                current_collection.hide_viewport = items["default_collections"]["viewport_disable"]
                current_collection.hide_render = items["default_collections"]["render_disable"]
                current_collection.hide_select = items["default_collections"]["selection_disable"]
                
                
                for layer_coll in traverse_tree(layer_coll_master):
                        layer_coll.indirect_only = items["default_collections"]["indirect_only"]
                        layer_coll.holdout = items["default_collections"]["holdout"]
                        layer_coll.exclude = items["default_collections"]["exclude"]
                        layer_coll.hide_viewport = items["default_collections"]["viewport_hide"]
                        pass
         
        
        if "default_objects" in items:
            for current_object in bpy.data.objects:
                current_object.hide_viewport = items["default_objects"]["viewport_disable"]
                current_object.hide_render = items["default_objects"]["render_disable"]
                current_object.hide_select = items["default_objects"]["selection_disable"]                    
                current_object.hide_set(items["default_objects"]["viewport_hide"])
            pass
        if "attrs" in items:
            #print("SET ATTRS")
            for item in items["attrs"]:
                print(item)
                value = items["attrs"][item]
                if item == "view_layer":
                    #scene.frame_start = items[item]

                    vl = scene.view_layers[value]
                    bpy.context.window.view_layer = vl
                    #print(items[item])

                if item == "start":
                    scene.frame_start = value
                
                if item == "end":
                    scene.frame_end = value
                if item == "current_frame":
                    scene.frame_current = value

                if item == "frame_step":
                    scene.frame_step = value            

                if item == "camera":
                    scene.camera = value

                if item == "overwrite":
                    scene.render.use_overwrite = value
                if item == "image_quality":
                    scene.render.image_settings.quality = value
                if item == "image_compression":
                    scene.render.image_settings.compression = value
                if item == "resolution_percentage":
                    bpy.context.scene.render.resolution_percentage = value
                if item == "resolution_x":
                    bpy.context.scene.render.resolution_x= value
                if item == "resolution_y":
                    bpy.context.scene.render.resolution_y= value

                if item == "evee_samples_render":
                    bpy.context.scene.eevee.taa_render_samples= value
                if item == "evee_samples_viewport":
                    bpy.context.scene.eevee.taa_samples= value
                if item == "cycles_samples_render_min":
                    bpy.context.scene.cycles.adaptive_min_samples= value
                if item == "cycles_samples_render_max":
                    bpy.context.scene.cycles.samples= value
                if item == "cycles_samples_viewport_min":
                    bpy.context.scene.cycles.preview_adaptive_min_samples= value
                if item == "cycles_samples_viewport_max":
                    bpy.context.scene.cycles.preview_samples= value
                if item == "render_engine":
                    bpy.context.scene.render.engine = value
            

            
                if "output" in items["attrs"]:
                
                    scene.render.filepath = items["attrs"]["output"]
                    output = items["attrs"]["output"]+"/"

                if "format" in items["attrs"]:
                    scene.render.image_settings.file_format = items["attrs"]["format"]
                    format = "."+items["attrs"]["format"]

                if "filename" in items["attrs"]:
                    print("FILENAME IS here")
                    scene.render.filepath = output+items["attrs"]["filename"]+format

        if "collections" in items:
            
            collections = items["collections"]
            for i in items["collections"]:
                
                collection = collections[i]             
                name = i
                bpy.data.collections[name].hide_viewport = collection["viewport_disable"]
                bpy.data.collections[name].hide_render = collection["render_disable"]
                bpy.data.collections[name].hide_select = collection["selection_disable"]
                
                
                for layer_coll in traverse_tree(layer_coll_master):
                    if layer_coll.collection.name == name:
                        layer_coll.indirect_only = collection["indirect_only"]
                        layer_coll.holdout = collection["holdout"]
                        layer_coll.exclude = collection["exclude"]
                        layer_coll.hide_viewport = collection["viewport_hide"]
                        break

        if "objects" in items:
                
                for c in items["objects"]:
                    current_item = items["objects"][c]
                    current_object = current_item["object"]
                    print(current_object)
                    if current_object is not None:
                        current_object.hide_viewport = current_item["viewport_disable"]
                        current_object.hide_render = current_item["render_disable"]
                        current_object.hide_select = current_item["selection_disable"]                    
                        current_object.hide_set(current_item["viewport_hide"])
                            
def FRGLT_manager_apply_set(self,context):  
    manager = bpy.context.scene.FRGLT_manager
    print("ACTIVE")
    
    if len(manager.sets)>0:
        
        current_set = manager.sets[manager.index.active]
      
        set_settings(get_settings(current_set,{},[]))
    
def filter_cameras(self, object):
    return object.type == 'CAMERA'

def category_items_quick(self,context):
    manager = context.scene.FRGLT_manager
    preferences = bpy.context.preferences.addons[__name__].preferences
    categories = manager.categories
    items = []

    
    if manager.default_category.hide != True:
            
       
        if preferences.labelAs == "icons":
            icon = manager.default_category.icon
            label = ""
        elif preferences.labelAs == "texticons":
            label = manager.default_category.name
            icon = manager.default_category.icon
        elif preferences.labelAs == "text":
            label = manager.default_category.name
            icon = "None"

        if manager.cfg.categories.overwrite.label==True:
            if manager.cfg.categories.label == "icons":
                icon = manager.default_category.icon
                label = ""
            elif manager.cfg.categories.label == "texticons":
                label = manager.default_category.name
                icon = manager.default_category.icon
            elif manager.cfg.categories.label == "text":
                label = manager.default_category.name
                icon = "None"
   


        
        items.append(_make_item(str(-1), label, "description", icon, 0))

    if len(categories)>0:

        i = 1
        for category in categories:
            category_length = len([i for i in manager.sets if i.category==category.id])
            
            if category.hide != True and category_length > 0:
                if preferences.labelAs == "icons":
                    icon = category.icon
                    label = ""
                elif preferences.labelAs == "texticons":
                    label = category.name
                    icon = category.icon
                elif preferences.labelAs == "text":
                    label = category.name
                    icon = "None"
                if manager.cfg.categories.overwrite.label==True:
                    if manager.cfg.categories.label == "icons":
                        icon = category.icon
                        label = ""
                    elif manager.cfg.categories.label == "texticons":
                        label = category.name
                        icon = category.icon
                    elif manager.cfg.categories.label == "text":
                        label = category.name
                        icon = "None"

                id = str(category.id)

                items.append(_make_item(str(i-1), label, "habala", icon, i))
            i += 1

    return items

def category_items(self, context):
    manager = context.scene.FRGLT_manager
    preferences = bpy.context.preferences.addons[__name__].preferences
    categories = manager.categories
    items = []


    if preferences.labelAs == "icons":
        icon = manager.default_category.icon
        label = ""
    elif preferences.labelAs == "texticons":
        label = manager.default_category.name
        icon = manager.default_category.icon
    elif preferences.labelAs == "text":
        label = manager.default_category.name
        icon = "None"

    if manager.cfg.categories.overwrite.label==True:
        if manager.cfg.categories.label == "icons":
            icon = manager.default_category.icon
            label = ""
        elif manager.cfg.categories.label == "texticons":
            label = manager.default_category.name
            icon = manager.default_category.icon
        elif manager.cfg.categories.label == "text":
            label = manager.default_category.name
            icon = "None"


    items.append(_make_item(str(-1), label, "Contains all Sets without a Category.", icon, 0))


    if len(categories)>0:

        i = 1
        for category in categories:
            
            
            if preferences.labelAs == "icons":
                icon = category.icon
                label = ""
            elif preferences.labelAs == "texticons":
                label = category.name
                icon = category.icon
            elif preferences.labelAs == "text":
                label = category.name
                icon = "None"
            if manager.cfg.categories.overwrite.label==True:
                if manager.cfg.categories.label == "icons":
                    icon = category.icon
                    label = ""
                elif manager.cfg.categories.label == "texticons":
                    label = category.name
                    icon = category.icon
                elif manager.cfg.categories.label == "text":
                    label = category.name
                    icon = "None"

            if type(self).__name__ == "FRGLT_PROP_manager":
                id = str(i-1)
            else:
                id = str(category.id)
            
            #category_length = len([i for i in manager.sets if i.category==category.id])
            #label += " ["+str(category_length)+"]"
            
            #if category.hide == True:
            #    label += " (Hidden)"
            
            items.append(_make_item(str(id), label, "habala", icon, i))
            i += 1

    return items

def get_icons(scene,context):
        
        icons = bpy.types.UILayout.bl_rna.functions["prop"].parameters["icon"].enum_items.keys()
        items = []
        i = 0
        for icon in icons:
             #print(i)
             items.append((icon,icon,"",icon,i))
             i += 1
        
        return items

def set_category(self,context):
    print(context)
    pass

def set_item_category(self,value):
    self.category = int(self.categories_list)
    #print(self.categories_list)

def set_current_category(self,value):
    
    self.index.sets = -1
    self.index.categories = int(self.categories_list)
    
    pass

def set_current_category_quick(self,value):

    self.index.categories_quick = int(self.categories_list_quick)
    print(self.categories_list_quick,self.index.categories_quick)
    #self.categories_list = self.categories_list_quick

def FRGLT_manager_set_active(self,value):
    
    self.active = self.sets_quick

#Menu

class FRGLT_MENU_manager_sets_parent(Menu):
    bl_idname = "FRGLT_MT_settings_parent_menu"
    bl_label = "Select a parent"
    index: IntProperty(default=0) 

    def draw(self, context):
        scene = context.scene 
        manager = context.scene.FRGLT_manager
        current = manager.sets[manager.index.sets]

        row = self.layout.row()
        row.operator("frglt.manager_add_parent",text="None").id = -1
        row = self.layout.row()
        row.separator()
        for item in manager.sets:
            if item.id != current.id:     
                #if item.parent != current.id:                
                row = self.layout.row()
                row.operator("frglt.manager_add_parent",text=item.name+" ("+str(item.id)+") ").id = item.id

class FRGLT_MENU_manager_items_format(Menu):
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
            opr = row.operator("frglt.manager_format_apply",text=format).format = format  
            opr.index = self.index
        

        row = col.row()
        row.label(text="Image")  

        col = base_row.column()

        for format in video_formats:
         
            row = col.row()
            opr = row.operator("frglt.manager_format_apply",text=format).format = format   
            opr.index = self.index 

        row = col.row()
        row.label(text="Movie")  
    
class FRGLT_MENU_manager_items(Menu):
    bl_idname = "FRGLT_MT_manager_items"
    bl_label = "Add"

    def draw(self, context):
        scene = context.scene 

        manager = scene.FRGLT_manager 

        types = get_setting_types()

        current = manager.sets[manager.index.sets]
        exclude = []
        
        for i in current.attrs:
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
                    row.operator("frglt.manager_add_item",text="  "+i).item_id=i   
                
                col.label(text=category)
                col.separator()            

class FRGLT_MENU_icons(Menu):
    bl_idname = "FRGLT_MT_icons"
    bl_label = "Add"
    index: IntProperty(default=0) 

    def draw(self, context):
        scene = context.scene 

        manager = scene.FRGLT_manager
        layout = self.layout
        icons = bpy.types.UILayout.bl_rna.functions["prop"].parameters["icon"].enum_items.keys()
        for i in icons:
            layout.operator("frglt.category_set_icon",text="",icon=i).icon=i

#Operators
class FRGLT_OP_manager_select_category(Operator):
    bl_idname = "frglt.select_category"
    bl_label = "Select Category"
    index: IntProperty(default=0)
    
    def execute(self, context):
        scene = context.scene  
        manager = scene.FRGLT_manager
        manager.index.categories = self.index
        
        return{'FINISHED'}

class FRGLT_OP_manager_start_batch(Operator):
    bl_idname = "frglt.start_batch_operation"
    bl_label = "Search Enum Operator"
    index: IntProperty(name="index",default=0)
    def execute(self, context):
        print("FRGLT Manager: Start Batch Operation")
        manager = bpy.context.scene.FRGLT_manager
        manager.index.sets_quick = self.index
        bpy.ops.render.render(animation=True, use_viewport=False)
        return {'FINISHED'}

class FRGLT_OP_manager_icon_search(Operator):
    bl_idname = "frglt.search_enum_operator"
    bl_label = "Search Enum Operator"
    bl_property = "my_search"
    index: IntProperty(name="target index")

    my_search: EnumProperty(
        name="Icon Searcg",
        items=get_icons,
    )

    def execute(self, context):
        manager = bpy.context.scene.FRGLT_manager
        manager.categories[manager.index.categories].icon = self.my_search

        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'RUNNING_MODAL'}

class FRGLT_OP_manager_duplicate(Operator):
    bl_idname = "frglt.duplicate_item"
    bl_label = "duplicate"
    mode: StringProperty(name="mode")

    def execute(self, context):
        manager = bpy.context.scene.FRGLT_manager
        if self.mode == "set":
            
            object_attrs = ["object","viewport_hide","viewport_disable","selection_disable","render_disable"]
            collection_attrs = ["collection","viewport_hide","viewport_disable","selection_disable","exclude","holdout","indirect_only","render_disable"]




            old_set = manager.sets[manager.index.sets]
            if old_set != False:           
                attrs = []
                objects = []
                collections = []
                for i in old_set.attrs:
                    attrs.append({"name":i.name,"value":getattr(i,i.name)})
                
                for i in old_set.objects:
                    duplicate_object_attrs = {}
                    for a in object_attrs:
                        duplicate_object_attrs[a] = getattr(i,a)

                    objects.append(duplicate_object_attrs)    

                for i in old_set.collections:
                    duplicate_collection_attrs = {}
                    for a in collection_attrs:
                        duplicate_collection_attrs[a] = getattr(i,a)

                    collections.append(duplicate_collection_attrs) 

                manager.add_settings()   

                new_set = manager.sets[manager.index.sets]
                
                new_set.quick = old_set.quick
                new_set.parent = old_set.parent
                new_set.category = old_set.category
                new_set.name = old_set.name+" (Duplicate)"
                new_set.index.objects = old_set.index.objects
                new_set.index.collections = old_set.index.collections
                index = 0

                for a in attrs:
                    new_set.attrs.add().name = a["name"]
                    setattr(new_set.attrs[index],a["name"],a["value"])
                    index += 1
                
                index = 0
                for object in objects:
                    new_set.objects.add()
                    for attr in object_attrs:
                        setattr(new_set.objects[index],attr,object[attr])
                    index += 1
                index = 0
                for collection in collections:
                    new_set.collections.add()
                    for attr in collection_attrs:
                        setattr(new_set.collections[index],attr,collection[attr])
                    index += 1    

        return {'FINISHED'}

class FRGLT_OP_manager_category_set_icon(Operator):
    """Batch Render"""

    bl_idname = "frglt.category_set_icon"
    bl_label = "Batch Render"
    icon: StringProperty(default="category")
    
    def execute(self, context):
        scene = context.scene  
        manager = scene.FRGLT_manager
        manager.current_category().icon = self.icon
        
        return{'FINISHED'}

class FRGLT_OP_manager_batch_render(Operator):
    """Batch Render"""

    bl_idname = "frglt.manager_batch_render"
    bl_label = "Batch Render"
    mode: StringProperty(default="category")
    
    def execute(self, context):
        scene = context.scene  
        manager = scene.FRGLT_manager
        system = platform.system()
        filename = bpy.path.basename(bpy.context.blend_data.filepath)
        name = "FRGLT_BATCH_"+bpy.path.clean_name(bpy.path.display_name(name=bpy.context.blend_data.filepath,has_ext=True))
        filepath = bpy.context.blend_data.filepath
        path = bpy.path.abspath("//")
        batchfile = path+name
        bin_path = os.path.dirname(bpy.app.binary_path)
        batch_extension = ".bat"
        copy = path+name+".blend"
        

        batchtext = ""
        bin = "blender"

        if system=="Linux":
            bin = bpy.app.binary_path
        index = 0
        render_counter = 0
        current_category_id = manager.categories[manager.index.categories_quick].id
        for i in manager.sets:
            
            render = False
            
            if self.mode=="selected" and i.select == True and i.category==current_category_id: 
                render = True           
            elif self.mode=="all" and i.category==current_category_id:
                render = True
            elif self.mode=="current" and i.category==current_category_id and index == manager.index.active:
                render = True
                print("Batch Render Current Set")
            else:
                print("False")
           
            if render == True:
                render_counter +=1
                batchtext += bin+' -b "'+copy+'" --python-expr "import bpy;bpy.ops.frglt.start_batch_operation(index='+str(index)+')" \n'
            
            index += 1
        if system=="Linux":
            batch_extension = ".sh"
            if manager.cfg.render.shutdown == True:
                batchtext += 'shutdown -h +1 \n'
            batchtext += "rm '"+path+name+".blend' \n"
            batchtext += "rm '"+path+name+".sh' \n"
        elif system == "Windows":
            batch_extension = ".bat"
            batchtext += "cd /d "+path+"\n"
            if manager.cfg.render.shutdown == True:
                batchtext += 'shutdown -s -t 010 \n'
            batchtext += "del "+name+".blend \n"
            batchtext += "del "+name+".bat \n"
            batchtext = 'cd /d '+bin_path+" \n" + batchtext
    

        if render_counter > 0:

            bpy.ops.wm.save_as_mainfile(filepath=copy,copy=True) 
            batchfile += batch_extension
            with open(batchfile, 'w') as f:
                f.write(batchtext)
            
            while not os.path.exists(path):
                print("wait for temp blend")       
    
    
            while not os.path.exists(batchfile):
                print(" wait for temp batch")
      
                  
            b='"'+batchfile+'"'
            
            if system=="Linux":
                os.system("chmod u+x "+b) 
                os.system("gnome-terminal -- sh "+b) 
               #print(b)
               #os.system("bash "+b) 
            
            elif system=="Windows":
                os.system("start cmd /c "+b) 
                pass

        else:
            print("Batch Render: Nothing selected")

        return{'FINISHED'}

class FRGLT_OP_manager_render_animation(Operator):
    """render this settings"""

    bl_idname = "frglt.manager_render_animation"
    bl_label = "Apply current Settings"
    index: IntProperty(default=0)

    def execute(self, context):
        scene = context.scene  
        manager = scene.FRGLT_manager
        old_index = manager.index.sets_quick
        manager.index.sets_quick = self.index
        bpy.ops.render.render({'dict': "override"},'INVOKE_DEFAULT',animation=True)
        return{'FINISHED'}

class FRGLT_OP_manager_render_frame(Operator):
    """render this settings"""

    bl_idname = "frglt.manager_render_frame"
    bl_label = "Apply current Settings"
    index: IntProperty(default=0)

    def execute(self, context):
        scene = context.scene  
        manager = scene.FRGLT_manager
        old_index = manager.index.sets_quick
        manager.index.sets_quick = self.index
        bpy.ops.render.render({'dict': "override"},'INVOKE_DEFAULT',use_viewport=True)

        return{'FINISHED'}

class FRGLT_OP_manager_format_apply(Operator):
    """Apply current Settings"""

    bl_idname = "frglt.manager_format_apply"
    bl_label = "Apply current Settings"
    index: IntProperty(default=0)   
    format: StringProperty(default="")

    def execute(self, context):
        scene = context.scene
        
        

        return{'FINISHED'}

class FRGLT_OP_manager_change_order(Operator):
    bl_idname = "frglt.change_order"
    bl_label = "Move the Item up"
    mode: StringProperty(default="set")
    direction: StringProperty(default="up")
    def execute(self, context):
        manager = context.scene.FRGLT_manager
        indexMode = "default"
        if self.direction == "up":
            direction = -1
        elif self.direction == "down":
            direction = 1
        
        if self.mode=="set":
            indexType = "sets"
            stack = manager.sets
            item_stack = manager.sets
            indexMode = "cat"
            
        elif self.mode == "category":
            
            indexType = "categories"
            stack = manager.category_types
            item_stack = manager.category_types
            items = manager.category_types
        
        items = []
        category_items = []
        index = 0
        category_index = 0

        if manager.index.categories == -1:
            category_id = -1
        else:
            category_id = manager.categories[manager.index.categories].id

        if indexMode=="cat":
            for i in item_stack:
                if i.category == category_id:
                    category_items.append(index)
                    if index == getattr(manager.index,indexType):
                        current_category_item = category_index
                    category_index += 1
                index += 1     
        
            current_index = category_items[current_category_item]
            next_category_item_index = current_category_item+direction
            
            if next_category_item_index < 0:
                #print("No Up")
                pass
            elif next_category_item_index > len(category_items)-1:
                #print("No Down")
                pass
            else:            
                next_index = category_items[next_category_item_index]
                stack.move(current_index,next_index)
                setattr(manager.index,indexType,next_index)
        else:
            current_index = getattr(manager.index,indexType)
            next_index = current_index + direction
            if next_index > -1 and next_index < len(stack):
                stack.move(current_index,next_index)
                setattr(manager.index,indexType,next_index)
        return{'FINISHED'}

class FRGLT_OP_manager_add(Operator):
    """Create a set"""

    bl_idname = "frglt.manager_add"
    bl_label = "Add a set"
    mode : StringProperty(default="set")

    def execute(self, context):
        scene = context.scene
        manager = scene.FRGLT_manager
        if len(manager.sets)>0:
            current_set = manager.sets[manager.index.sets]
        if self.mode=="set":
            
            if manager.index.categories == -1 or len(manager.categories)==0:
                id = -1
            else:
                id = manager.categories[manager.index.categories].id

            new_set = manager.sets.add()
            new_set.category = id
            new_set.categories_list = str(id)
            new_set.id = manager.id
            manager.id +=1
            manager.index.sets = len(manager.sets)-1
        elif self.mode=="collections":
            current_set.collections.add()
        elif self.mode=="objects":
            current_set.objects.add()
        elif self.mode=="category":
            
            manager.categories.add().id = manager.category_types_id
            manager.categories[len(manager.categories)-1].name="New Category"
            manager.index.categories= len(manager.categories)-1
            manager.categories_list = str(manager.index.categories)
            
            manager.category_types_id += 1   


       
        return{'FINISHED'}

class FRGLT_OP_manager_remove(Operator):
    """Remove a set"""

    bl_idname = "frglt.manager_remove"
    bl_label = "Remove current set"
    mode: StringProperty(default="set")
    def execute(self, context):
        scene = context.scene
        manager = context.scene.FRGLT_manager
        items = []
        index = 0
        count = 0
        prev = 0

        if len(manager.sets)>0:
            current_set = manager.sets[manager.index.sets]

        if self.mode=="set":
          
            if manager.index.categories == -1 or len(manager.sets)==0:
                current_category_id = -1
            else:
                current_category_id = manager.categories[manager.index.categories].id
            
            
            category_items = [i for i in range(0,len(manager.sets)) if manager.sets[i].category==current_category_id]

            manager.sets.remove(manager.index.sets)
            if category_items[-1] == manager.index.sets:
                if len(category_items) > 1:
                    manager.index.sets = category_items[-2]
                else:
                    manager.index.sets = -1

            if len(manager.sets)==0:
                manager.id = 0
            
        elif self.mode=="collections":
            current_set.collections.remove(current_set.index.collections)
            if len(current_set.collections)==current_set.index.collections:
                current_set.index.collections -= 1
        
        elif self.mode=="objects":
            current_set.objects.remove(current_set.index.objects)
            if len(current_set.objects)==current_set.index.objects:
                current_set.index.objects -= 1
        
        elif self.mode=="category":
            if manager.index.categories != -1:

                current_category = manager.categories[manager.index.categories].id
                
                for i in manager.sets:
                    if i.category == current_category:
                        i.category = -1
                        i.categories_list = "-1"
                        pass
            
                manager.categories.remove(manager.index.categories)
                if manager.index.categories == manager.index.categories_quick:
                    manager.index.categories_quick = -1

                if len(manager.categories) == manager.index.categories:
                
                    manager.index.categories = len(manager.categories)-1
                    manager.categories_list = str(len(manager.categories)-1)

        elif self.mode=="attr":

            current_set.attrs.remove(current_set.index.attrs)
            
            if len(current_set.attrs)==current_set.index.attrs:
                current_set.index.attrs -= 1
        
            
            
        return{'FINISHED'}

class FRGLT_OP_manager_add_item(Operator):
    """Adds a new item to the current set."""

    bl_idname = "frglt.manager_add_item"
    bl_label = "Add"
    item_id: StringProperty(default="peter")

    def execute(self, context):
        manager = context.scene.FRGLT_manager
        manager.add_item(self.item_id)

            
        return{'FINISHED'}

class FRGLT_OP_manager_add_parent(Operator):
    """Removes this item from the current set"""

    bl_idname = "frglt.manager_add_parent"
    bl_label = "Add Parent"
    id : IntProperty()

    def execute(self, context):
        manager = context.scene.FRGLT_manager
        manager.sets[manager.index.sets].parent=self.id
        

        return{'FINISHED'}

class FRGLT_OP_manager_edit_category(Operator):
    bl_idname = "frglt.edit_category"
    bl_label = "Edit Category"
 
 
 
    def execute(self, context):
        #self.report({'INFO'}, self.message)
        #print(self.message)
        return {'FINISHED'}
 
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width = 400)
 
    def draw(self, context):
        manager = context.scene.FRGLT_manager
        if manager.index.categories == -1:
            current_category = manager.default_category
            noneCategory = True
        else:
            noneCategory = False
            current_category = manager.categories[manager.index.categories]
        
        
        if noneCategory == True:
            row = self.layout.row()
            row.label(text="This category contains all sets without a category")
        


        if len(manager.categories)>0:
            row = self.layout.row()
            row.prop(current_category,"hide")
        else:
            row = self.layout.row()
            row.label(text="There are no categories. None Category is always visible in Quick Acces.")
        


        
        if noneCategory == False:
            row = self.layout.row()
            row.label(text="Icon:")
            row.operator("frglt.search_enum_operator",text="",emboss=True,icon=current_category.icon).index = manager.index.categories
            row = self.layout.row()
            row.prop(current_category,"name",text="Name")

class FRGLT_OP_manager_set_active_set(Operator):
    """Makes this set active."""
    bl_idname = "frglt.set_active_set"
    bl_label = "Make active set."
    index: IntProperty(name="id")

    def execute(self,context):
        print("Apply Set from Manager")
        manager = bpy.context.scene.FRGLT_manager
        index = self.index
        manager.index.sets = index
        manager.index.sets_quick = index
        #manager.index.active = self.index
        #
        #
        #print(self.index)

        return {'FINISHED'}

class FRGLT_OP_manager_export(Operator,ExportHelper):
    """Makes this set active."""
    bl_idname = "frglt.manager_export"
    bl_label = "Export"
    filename_ext = '.json'
    
    filter_glob: StringProperty(
        default='*.json',
        options={'HIDDEN'}
    )

    file_content: StringProperty(
        default="",
        options={'HIDDEN'}
    )




    
    def execute(self,context):        
        self.prepare()
        self.write()
        return {'FINISHED'}

    def prepare(self):
        manager = bpy.context.scene.FRGLT_manager
        categories = manager.categories
        sets = manager.sets
        export_categories = []
        export_sets = []
        exclude_names = ["__annotations__","__dict__","__doc__","__module__","__weakref__","bl_rna","rna_type","index","select","categories_list"]
        set_sub_names = ["attrs","collections","objects"]

        for c in categories:
            c = {"name":c.name,"hide":c.hide}
            export_categories.append(c)

        index = 0
        for i in sets:
            names = dir(i)
            export_sets.append({})
            for n in names:
                if n not in exclude_names:
                    attr = getattr(i,n)
                    if n == "attrs":                        
                        export_sets[index][n] = []
                        for a in attr:
                            export_sets[index][n].append({"name":a.name,"value":getattr(a,a.name)})

                    elif n == "objects":
                        export_sets[index][n] = []
                        for a in attr:
                            #attr_list = ["viewport_hide","viewport_disable","selection_disable","exclude","holdout","indirect_only","render_disable"]
                            attr_list = ["object","viewport_hide","viewport_disable","selection_disable","render_disable"]
                            ss = {}

                            for g in attr_list:
                                if g == "object":
                                    if hasattr(getattr(a,g),"name"):
                                        ss[g] = getattr(a,g).name
                                    else:
                                        ss[g] = ""

                                    pass
                                else:
                                    ss[g]=getattr(a,g)

                            export_sets[index][n].append(ss)     

                    
                    elif n == "collections":
                            export_sets[index][n] = []
                            for a in attr:
                                attr_list = ["collection","viewport_hide","viewport_disable","selection_disable","exclude","holdout","indirect_only","render_disable"]
                                
                                ss = {}

                                for g in attr_list:
                                    if g == "collection":
                                        if hasattr(getattr(a,g),"name"):
                                            ss[g] = getattr(a,g).name
                                        else:
                                            ss[g] = ""

                                        pass
                                    else:
                                        ss[g]=getattr(a,g)

                                export_sets[index][n].append(ss)    
                    else:
                        
                        export_sets[index][n]=attr
                    
                    
            index += 1
        export = {"categories":export_categories,"sets":export_sets}
        
        self.file_content = pprint.pformat(export)

    def write(self):
        f = open(self.filepath, "w")
        f.write(self.file_content)
        f.close()
        self.file_content = ""
        
class FRGLT_OP_manager_import(Operator,ImportHelper):
    """Import Settings"""
    bl_idname = "frglt.manager_import"
    bl_label = "Import"
    filename_ext = '.json'
    
    overwrite: BoolProperty(
        default=False
    )

    mode: StringProperty(name="mode")

    
    filter_glob: StringProperty(
        default='*.json',
        options={'HIDDEN'}
    )
    
    def draw(self,context):
        layout = self.layout
        layout.label(text="Overwrite Settings?")
        
        layout.operator(self.bl_idname,text="overwrite").mode = "overwrite"
        layout.operator(self.bl_idname,text="append").mode = "append"
        layout.operator(self.bl_idname,text="append").mode = "cancel"
        

    def execute(self,context):

        manager = bpy.context.scene.FRGLT_manager
 
        if len(manager.sets) > 0 or len(manager.categories) > 0:
            return context.window_manager.invoke_popup(self)

        return {'FINISHED'}

    def overwrite_sets(self):
        print("Overwrite Sets")
    
    def append_sets(self):
        print("Append Sets")

    def invoke(self,context,event):
        context.window_manager.fileselect_add(self)
        print("peep")
        return {'RUNNING_MODAL'}
#Property Groups

class FRGLT_PROP_manager_sets_collections(PropertyGroup):
    use_default: BoolProperty(name="use default",default=False)
    collection: PointerProperty(type=bpy.types.Collection, name="Collection")
    viewport_hide: BoolProperty(name="Show in Viewport",default=False)
    viewport_disable: BoolProperty(name="Show in Viewport",default=False)
    selection_disable: BoolProperty(name="Show in Viewport",default=False)
    exclude:  BoolProperty(name="Show in Viewport",default=False)
    holdout: BoolProperty(name="Show in Viewport",default=False)
    indirect_only: BoolProperty(name="Show in Viewport",default=False)
    render_disable: BoolProperty(name="Show in Viewport",default=False)

class FRGLT_PROP_manager_sets_objects(PropertyGroup):
    use_default: BoolProperty(name="use default",default=False)
    object: PointerProperty(type=bpy.types.Object, name="Object")
    viewport_hide: BoolProperty(name="Show in Viewport",default=False)
    viewport_disable: BoolProperty(name="Show in Viewport",default=False)
    selection_disable: BoolProperty(name="Show in Viewport",default=False)
    render_disable: BoolProperty(name="Show in Viewport",default=False)

class FRGLT_PROP_manager_sets_default(PropertyGroup):
    objects: PointerProperty(type = FRGLT_PROP_manager_sets_objects)
    collections: PointerProperty(type = FRGLT_PROP_manager_sets_collections)

class FRGLT_PROP_manager_sets_attr(PropertyGroup):
    name: StringProperty(name="name")
    start : IntProperty(name="start")
    end : IntProperty(name="end")
    frame_step: IntProperty(name="Frame Step",max=100,min=1)
    current_frame: IntProperty(name="Current Frame")
    camera: PointerProperty(name = "my pointer", description = "my descr", type=bpy.types.Object, poll=filter_cameras) 
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

class FRGLT_PROP_manager_sets_index(PropertyGroup):
    attrs : IntProperty(name="Attributes Index")
    collections : IntProperty(name="Collections Index")
    objects : IntProperty(name="Objects Index")

class FRGLT_PROP_manager_cfg_render_buttons_list(PropertyGroup):
    frame : BoolProperty(name="All",default=True)
    animation : BoolProperty(name="Selected",default=True)

class FRGLT_PROP_manager_cfg_render_buttons_batch(PropertyGroup):
    all : BoolProperty(name="All",default=True)
    selected : BoolProperty(name="Selected",default=True)
    current : BoolProperty(name="Current",default=True)

class FRGLT_PROP_manager_cfg_render_buttons(PropertyGroup):
    batch: PointerProperty(type=FRGLT_PROP_manager_cfg_render_buttons_batch)
    list: PointerProperty(type=FRGLT_PROP_manager_cfg_render_buttons_list)

class FRGLT_PROP_manager_cfg_render_overwrite(PropertyGroup):
    buttonsBatch: BoolProperty(name="Batch Buttons", description ="", default = False)
    buttonsList: BoolProperty(name="List Buttons", description ="", default = False)

class FRGLT_PROP_manager_cfg_render(PropertyGroup):
    buttons: PointerProperty(type=FRGLT_PROP_manager_cfg_render_buttons)
    shutdown: BoolProperty(name = "Shutdown", description = "Shutdown when finished", default = False)
    overwrite: PointerProperty(type=FRGLT_PROP_manager_cfg_render_overwrite)

class FRGLT_PROP_manager_cfg_categories_overwrite(PropertyGroup):
    style: BoolProperty(name="Category Style", description ="", default = False)
    label: BoolProperty(name="Label Style", description ="", default = False)

class FRGLT_PROP_manager_cfg_categories(PropertyGroup):
    style: EnumProperty(name = "Settings Category Types Index", items=[("buttons","Buttons",""),("list","List","")],default = "buttons")
    label: EnumProperty(name = "Settings Category Types Index", items=[("text","Text",""),("icons","Icons",""),("texticons","Text & Icons","")],default = "texticons")
    overwrite: PointerProperty(type=FRGLT_PROP_manager_cfg_categories_overwrite)

class FRGLT_PROP_manager_index(PropertyGroup):
    sets: IntProperty(name = "Sets index", default = 0)
    sets_quick: IntProperty(name = "Categories index", default = 0, update = FRGLT_manager_set_active)
    categories: IntProperty(name = "Categories index", default = 0)
    categories_quick: IntProperty(name = "Categories index", default = 0)
    active: IntProperty(name = "Active Set", update = FRGLT_manager_apply_set)

class FRGLT_PROP_manager_categories(PropertyGroup):
    """Categories for Setting Collections"""
    name: StringProperty(name="Category Name",default="None")
    id: IntProperty(name = "Settings id index")
    icons: EnumProperty("select icons", items=get_icons)
    icon: StringProperty(name="Category Name",default="QUESTION")
    hide: BoolProperty(name="Hide from Quick",default=False)

class FRGLT_PROP_manager_sets(PropertyGroup): 
    """Base of a Setting Collection"""
      
    name : StringProperty(name="Name", default="Settings")
    id : IntProperty(name="id")
    index : PointerProperty(type=FRGLT_PROP_manager_sets_index)
    category: IntProperty(name="category id",default=0)
    categories_list: EnumProperty(items= category_items, update=set_item_category)
    parent: IntProperty(name="parent id",default=-1)
    quick: BoolProperty(name="quick",default=False)
    select: BoolProperty(name="select",default=False)
    
    attrs : CollectionProperty(type = FRGLT_PROP_manager_sets_attr) 
    collections: CollectionProperty(type = FRGLT_PROP_manager_sets_collections)
    objects: CollectionProperty(type = FRGLT_PROP_manager_sets_objects)
    default: PointerProperty(type = FRGLT_PROP_manager_sets_default)

class FRGLT_PROP_manager_cfg(PropertyGroup):
    render : PointerProperty(type=FRGLT_PROP_manager_cfg_render)
    categories : PointerProperty(type=FRGLT_PROP_manager_cfg_categories)

class FRGLT_PROP_manager(PropertyGroup):
    sets: CollectionProperty(type = FRGLT_PROP_manager_sets)
    id: IntProperty(name = "Settings id index", default = 1)
    index: PointerProperty(type=FRGLT_PROP_manager_index)
    orderBy: EnumProperty("index", items=[("index","","Order By Index","ALIGN_JUSTIFY",1),("name","","Order by Name","FILE_TEXT",2)])
    category: IntProperty(name="current category id",default=0)
    categories: CollectionProperty(type = FRGLT_PROP_manager_categories)  
    categories_list: EnumProperty(name="Category List" , items=category_items , update=set_current_category)
    categories_list_quick: EnumProperty(name="Category List Quick" , items=category_items_quick , update=set_current_category_quick)
    default_category: PointerProperty(type=FRGLT_PROP_manager_categories)
    hide_default: BoolProperty(name="Hide Default 'None' Category from Quick Acces",default=False)
    category_types_id: IntProperty(name = "Category Types Id Index", default = 1)
    category_types_show: BoolProperty(name = "Settings Category Types Index", default = False)
    cfg: PointerProperty(type=FRGLT_PROP_manager_cfg)

    def get_by_id(self,id):
        for i in self.sets:
            if i.id == id:
                return i
        return False
    

    def add_settings(self):


        self.sets.add().id = self.id
        self.index.sets = len(self.sets)-1        
        self.sets[self.index.sets].name = self.sets[self.index.sets].name
        self.sets[self.index.sets].category = bpy.context.scene.FRGLT_manager.category
        self.id += 1
        self.sets[self.index.sets].order = len(self.sets)
    
    def add_item(self,item_id):
        self.sets[self.index.sets].attrs.add().name = item_id

    def remove_item(self,item_id): 
        self.sets[self.index.sets].attrs.remove(item_id)

    def category_size(self):
        return len(self.category_types)

   # def current_category(self):
   #     return self.category_types[self.index.categories]

#UIList

class FRGLT_UL_manager_sets_collections(UIList):
    """List of settings"""

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        
        manager = context.scene.FRGLT_manager
        if self.layout_type in {'DEFAULT', 'COMPACT'}:

            if index==manager.sets[manager.index.sets].index.collections:
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
   
class FRGLT_UL_manager_sets_objects(UIList):
    """List of settings"""

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        
        manager = context.scene.FRGLT_manager
        if self.layout_type in {'DEFAULT', 'COMPACT'}:

            if index==manager.sets[manager.index.sets].index.objects:
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
    
class FRGLT_UL_manager_sets(UIList):
    """List of settings"""

    custom_invert: BoolProperty(name="Reverse search by name", default=False)

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        
        manager = context.scene.FRGLT_manager
        current_set = manager.sets[manager.index.sets]

        if self.layout_type in {'DEFAULT', 'COMPACT'}:

            icon = "OUTLINER_COLLECTION"
            row = layout.row()
            ic = "BLANK1"

            
            if item.id == current_set.parent:
                ic = "DECORATE_LINKED"
            if manager.index.active == index:
                selector_icon = "RESTRICT_SELECT_OFF"
            else:
                selector_icon = "RESTRICT_SELECT_ON"

            row.operator("frglt.set_active_set",text="",emboss=False,icon=selector_icon).index = index
            row.prop(item,"name",text="",emboss=False,icon=ic)
            #row.label(text="category_id: "+str(item.category))
            #row.label(text="index: "+str(index))
            #row.label(text="id: "+str(item.id))
            if item.parent > -1:
                
                if item.name == item.parent:
                    use_icon = "ERROR"

                parent = manager.get_by_id(item.parent)
                if parent != False:
                    row.label(text=parent.name+" (id: "+str(parent.id)+" category: "+str(parent.category)+")",icon="FILE_PARENT")
                
                elif parent == False and item.parent != 0:

                    row.label(text="parent not found",icon="ERROR")
                else:
                    row.label(text="")
                    
                

        elif self.layout_type in {'GRID'}:

            layout.alignment = 'CENTER'
            layout.prop(item,"name")
    
    def draw_filter(self, context, layout):
        line = layout.row()
        col = line.column(align=True)
        col = col.row(align=True)
        col.prop(self,"filter_name",text="")
        col.prop(self,"custom_invert",text="",icon="ARROW_LEFTRIGHT")
       
        col = line.column(align=True)
        col = col.row(align=True)
        col.prop(self,"use_filter_sort_alpha",text="")
        if self.use_filter_sort_reverse == True:
            col.prop(self,"use_filter_sort_reverse",text="",icon="SORT_DESC")
        else:
            col.prop(self,"use_filter_sort_reverse",text="",icon="SORT_ASC")

        pass
        

    def filter_items(self, context, data, propname):
        """Filter and order items in the list."""
        manager = context.scene.FRGLT_manager
        category = manager.category
        helpers = bpy.types.UI_UL_list

        if manager.index.categories == -1 or len(manager.categories)==0:
            current_category = -1
        else:            
            current_category = manager.categories[manager.index.categories].id
        
        category_ids = []

        for i in manager.categories:
            category_ids.append(i.id)
        
        items = getattr(data, propname)
        filtered = []
        ordered = []

        filtered = [self.bitflag_filter_item] * len(items)

        i = 0
        for item in items:
            item_category = item.category
            if current_category == -1 and item.category not in category_ids:
                item_category = -1

            name_filter = False

            if self.custom_invert == False:
                
                if item.name.lower().find(self.filter_name.lower())<0 and self.filter_name != "":
                    name_filter = True
            else:
                
                if item.name.lower().find(self.filter_name.lower())>-1 and self.filter_name != "":
                    name_filter = True

            if current_category != item_category or name_filter==True:   
                      
                filtered[i] &= ~self.bitflag_filter_item  
            i += 1

        if self.use_filter_sort_alpha == True:
            ordered = UI_UL_list.sort_items_by_name(items, 'name')
  
        return filtered,ordered

class FRGLT_UL_manager_quick(UIList):
    """List of settings"""

    custom_invert: BoolProperty(name="Reverse search by name", default=False)
    show_hidden: BoolProperty(name="Show sets hidden from quick acces.", default=False)
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):

        manager = context.scene.FRGLT_manager  
        preferences = bpy.context.preferences.addons[__name__].preferences
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            


            icon = "OUTLINER_COLLECTION"
            row = layout.row(align=True)
            if manager.cfg.render.buttons.batch.selected == True:
                row.prop(item,"select",text="") 
            row.label(text=item.name)   
         

            if manager.cfg.render.overwrite.buttonsList==True:
                frame = manager.cfg.render.buttons.list.frame
                animation = manager.cfg.render.buttons.list.animation 
            else:
                frame = preferences.renderButtonFrame
                animation = preferences.renderButtonAnimation

            if animation == True:
                row.operator("frglt.manager_render_animation",text="",icon="RENDER_ANIMATION").index = index
            if frame == True:
                row.operator("frglt.manager_render_frame",text="",icon="IMAGE_DATA").index = index

        elif self.layout_type in {'GRID'}:

            layout.alignment = 'CENTER'
            row.label(text=item.name)
    
    def draw_filter(self, context, layout):
        line = layout.row()
        col = line.column(align=True)
        col = col.row(align=True)
        col.prop(self,"filter_name",text="")
        col.prop(self,"custom_invert",text="",icon="ARROW_LEFTRIGHT")
       
        col = line.column(align=True)
        col = col.row(align=True)
        if self.show_hidden == True:
            show_hidden_icon = "HIDE_OFF"
        else:
            show_hidden_icon = "HIDE_ON"
        col.prop(self,"show_hidden",text="",icon=show_hidden_icon)
        col.prop(self,"use_filter_sort_alpha",text="")
        if self.use_filter_sort_reverse == True:
            col.prop(self,"use_filter_sort_reverse",text="",icon="SORT_DESC")
        else:
            col.prop(self,"use_filter_sort_reverse",text="",icon="SORT_ASC")

        pass
        
        

    def filter_items(self, context, data, propname):
        """Filter and order items in the list."""
        manager = context.scene.FRGLT_manager
        category = manager.category
        helpers = bpy.types.UI_UL_list

        if manager.index.categories_quick == -1 or len(manager.categories)==0:
            current_category = -1
        else:            
            #print(manager.index.categories_quick)
            current_category = manager.categories[manager.index.categories_quick].id
        
        category_ids = []

        for i in manager.categories:
            category_ids.append(i.id)
        
        items = getattr(data, propname)
        filtered = []
        ordered = []

        filtered = [self.bitflag_filter_item] * len(items)

        i = 0
        for item in items:
            item_category = item.category
            if current_category == -1 and item.category not in category_ids:
                item_category = -1

            name_filter = False

            if self.custom_invert == False:
                
                if item.name.lower().find(self.filter_name.lower())<0 and self.filter_name != "":
                    name_filter = True
            else:
                
                if item.name.lower().find(self.filter_name.lower())>-1 and self.filter_name != "":
                    name_filter = True

            hide = False
            
            if self.show_hidden == True:
                if current_category != item_category:
                    hide = True
           
            elif current_category != item_category or item.quick != True or name_filter==True:   
                hide = True 
            
            if hide==True:
                filtered[i] &= ~self.bitflag_filter_item  

            i += 1

        if self.use_filter_sort_alpha == True:
            ordered = UI_UL_list.sort_items_by_name(items, 'name')
  
        return filtered,ordered

class FRGLT_UL_manager_sets_attrs(UIList):
    """List of settings"""

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
                   

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            
            icon = "OUTLINER_COLLECTION"
            row = layout.row()
            row.label(text=item.name)
            row.prop(item,item.name,text="")

        elif self.layout_type in {'GRID'}:

            layout.alignment = 'CENTER'
            row.label(text=item.name)

#PANELS

class FRGLT_PT_manager_quick:
    """Creates a Panel in the 3D_VIEW properties window"""
    bl_space_type = 'VIEW_3D'
    bl_category = "Settings" 
    bl_region_type = 'UI'

class FRGLT_PT_manager_quick_main(FRGLT_PT_manager_quick,Panel): 
    bl_idname = "FRGLT_PT_manager_quick_main"
    bl_label = "Settings Manager Quick Acces"

    def draw(self,context):
        pass

class FRGLT_PT_manager_quick_sub(FRGLT_PT_manager_quick, Panel):
    bl_parent_id = "FRGLT_PT_manager_quick_main"

    def draw_header(self,context):
        pass

class FRGLT_PT_manager_quick_render(FRGLT_PT_manager_quick_sub):
    bl_label = "Render" 
   
    def draw(self,context):
        scene = context.scene
        manager = context.scene.FRGLT_manager
        layout = self.layout
        list = layout.row(align=True)
        preferences = bpy.context.preferences.addons[__name__].preferences
        
        if bpy.data.is_saved:
            list.prop(manager.cfg.render,"shutdown",text="Shutdown")

            if manager.cfg.render.shutdown == True and bpy.data.is_dirty:
                list.label(text="Save File to render shutdown.")
                list.operator("wm.save_mainfile",text="Save")
                list.operator("wm.save_as_mainfile",text="Save as")
            else:
                
                
                

                if manager.cfg.render.overwrite.buttonsBatch==True:
                    all = manager.cfg.render.buttons.batch.all
                    selected = manager.cfg.render.buttons.batch.selected
                    current = manager.cfg.render.buttons.batch.current
                else:
                    all = preferences.renderButtonAll
                    selected = preferences.renderButtonSelected
                    current = preferences.renderButtonCurrent
                    


                if all == True:
                    list.operator("frglt.manager_batch_render",text="All",icon="ALIGN_JUSTIFY").mode = "all"
                if selected == True:
                    list.operator("frglt.manager_batch_render",text="Selected",icon="CHECKBOX_HLT").mode = "selected"
                if current == True:
                    list.operator("frglt.manager_batch_render",text="Current",icon="RADIOBUT_ON").mode = "current"
            



        else:
            list.label(text="Save file for Batch Render.")
            list.operator("wm.save_mainfile")
        pass
    
    @classmethod
    def poll(cls, context):
        manager = context.scene.FRGLT_manager
        preferences = bpy.context.preferences.addons[__name__].preferences
        button = manager.cfg.render.buttons.batch
        show = 0
        
        if manager.cfg.render.overwrite.buttonsBatch==True:
            all = manager.cfg.render.buttons.batch.all
            selected = manager.cfg.render.buttons.batch.selected
            current = manager.cfg.render.buttons.batch.current
        else:
            all = preferences.renderButtonAll
            selected = preferences.renderButtonSelected
            current = preferences.renderButtonCurrent

        if all == True or selected == True or current == True :
            show = 1

        if show==0:
            return False
        else:
            return True
         
class FRGLT_PT_manager_quick_sets(FRGLT_PT_manager_quick_sub):
    
    bl_label = "Sets" 
    bl_options = {'HIDE_HEADER'}

    def draw(self,context):
        scene = context.scene
        manager = context.scene.FRGLT_manager
        preferences = bpy.context.preferences.addons[__name__].preferences

        layout = self.layout
        list = layout.row(align=True)
        
        if len(manager.categories) > 0:
            list = layout.row()
            list.label(text="Category")
              

            if preferences.categoryAs == "buttons":
                style = True
            else:
                style = False

            if manager.cfg.categories.overwrite.style==True:
                if manager.cfg.categories.style=="buttons":
                    style = True
                else:
                    style = False              
                
            
            list.prop(manager,"categories_list_quick",text="name",expand=style)

        list = layout.row()
        list.template_list("FRGLT_UL_manager_quick", "", manager, "sets", manager.index, "sets_quick",rows=9, type="DEFAULT")


        pass
    

class FRGLT_PT_manager:
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene" 

class FRGLT_PT_manager_main(FRGLT_PT_manager,Panel):
    bl_idname = "FRGLT_PT_settings_panel_main"
    bl_label = ""
    

    def draw_header(self,context):
        manager = context.scene.FRGLT_manager
        self.layout.label(text="Settings Manager")
        self.layout.prop(manager, "category_types_show", icon="PREFERENCES", text="", emboss=False)
        #self.layout.operator("frglt.manager_export", icon="EXPORT", text="", emboss=False)
        #self.layout.operator("frglt.manager_import", icon="IMPORT", text="", emboss=False)

    def draw(self, context):
        pass

class FRGLT_PT_manager_sub(FRGLT_PT_manager, Panel):
    bl_parent_id = "FRGLT_PT_settings_panel_main"
    
    @classmethod
    def poll(cls, context):
        manager = context.scene.FRGLT_manager

        if manager.category_types_show == True or len(manager.sets)==0:
            return False
        else:
            return True  

    def draw_header(self, context):
        pass

class FRGLT_PT_manager_configure_categories(FRGLT_PT_manager_sub):
    bl_label = "Configure Categories"
 
    def draw(self, context):
       
        layout = self.layout
        scene = context.scene
        manager = scene.FRGLT_manager

        list = layout.row()
        col = list.column()
        col.prop(manager.cfg.categories.overwrite,"style",text="")
        col = list.column()
        col.enabled = manager.cfg.categories.overwrite.style
        col = col.row()

        col.label(text="Show Categories as")
        col.prop(manager.cfg.categories,"style",text="Show Categories as", expand=True)

        list = layout.row()
        col = list.column()
        col.prop(manager.cfg.categories.overwrite,"label",text="")
        col = list.column()
        col.enabled = manager.cfg.categories.overwrite.label
        col = col.row()
        col.label(text="Show Categories Label as")
        col.prop(manager.cfg.categories,"label",text="Show Category Label as", expand=True)
       
      


    def draw_header(self,context):
        pass

    @classmethod
    def poll(cls, context):
        manager = context.scene.FRGLT_manager
        if manager.category_types_show == False:
            return False
        else:
            return True

class FRGLT_PT_manager_configure_render(FRGLT_PT_manager_sub):
    bl_label = "Render Buttons"
    


    def draw(self, context):
       
        layout = self.layout
        scene = context.scene
        manager = scene.FRGLT_manager

        

        list = layout.row(align=True)
        col = list.column()
        col.prop(manager.cfg.render.overwrite,"buttonsBatch",text="")
        col = list.column()
        col = col.row()
        col.enabled = manager.cfg.render.overwrite.buttonsBatch
        col.label(text="Show Batch Render Buttons")
        col.prop(manager.cfg.render.buttons.batch,"all",text="All", toggle = 1)
        col.prop(manager.cfg.render.buttons.batch,"selected",text="Selected", toggle = 1)
        col.prop(manager.cfg.render.buttons.batch,"current",text="Current", toggle = 1)
        
        list = layout.row(align=True)
        col = list.column()
        list.prop(manager.cfg.render.overwrite,"buttonsList",text="")
        col = list.column()
        col = col.row()
        col.enabled = manager.cfg.render.overwrite.buttonsList
        col.label(text="Show Single Render Buttons")
        col.prop(manager.cfg.render.buttons.list,"frame",text="Frame", toggle = 1)
        col.prop(manager.cfg.render.buttons.list,"animation",text="Animation", toggle = 1)
   

    def draw_header(self, context):
        pass

    @classmethod
    def poll(cls, context):
        manager = context.scene.FRGLT_manager
        if manager.category_types_show == False:
            return False
        else:
            return True

class FRGLT_PT_manager_sets(FRGLT_PT_manager_sub):
    bl_label = "Settings List"
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
       
        layout = self.layout
        scene = context.scene
        manager = scene.FRGLT_manager
        preferences = bpy.context.preferences.addons[__name__].preferences

        categories = layout.box()
        categories = categories.row()
        
        if len(manager.categories) > 0:
            enable_category_options = True
            categories.label(text="Categories")

            if preferences.categoryAs == "buttons":
                style = True
            else:
                style = False
            if manager.cfg.categories.overwrite.style==True:
                if manager.cfg.categories.style=="buttons":
                    style = True
                else:
                    style = False
                
            
            index = 0
            categories.prop(manager,"categories_list",expand=style)
              
            
            
        else:

            
            enable_category_options = False
            categories.label(text="No categories")
        
        enable_edit_button = enable_category_options
        if manager.index.categories == -1:
            enable_edit_button = False
        editButton = categories.row()
        editButton.enabled = True
        editButton.operator("frglt.edit_category",text="",icon="PREFERENCES")
        
        addButton = categories.row()
        addButton.enabled = True
        addButton.operator("frglt.manager_add", text="", icon='ADD').mode="category"
        

        removeButton = categories.row()        
        removeButton.enabled = enable_edit_button
        removeButton.operator("frglt.manager_remove", text="", icon='REMOVE').mode="category"    
        

        sets = layout.row()
        sets.enabled = True
        sets.template_list("FRGLT_UL_manager_sets", "", manager, "sets", manager.index, "sets",rows=9, type="DEFAULT")
        
      
        enable_set_options = False

        if len(manager.categories)>0:
            if int(manager.categories_list) == -1:
                current_category_id = -1
            else:    
                current_category_id = manager.categories[int(manager.categories_list)].id
        else:
            current_category_id = -1

        category_length = len([i for i in manager.sets if i.category==current_category_id])
        
        if category_length > 0 and manager.index.sets != -1:
            enable_set_options = True

       
        sidebar = sets.column(align=True)
       
        sidebar = sidebar.column()
        sidebar.operator("frglt.manager_add", text="", icon='ADD').mode="set"
        
        sidebar = sidebar.column()
        sidebar.operator("frglt.manager_remove", text="", icon='REMOVE').mode="set"
        sidebar.enabled = enable_set_options

        sidebar = sidebar.column()
        sidebar.separator() 

        sidebar = sidebar.column()
        sidebar.enabled = enable_set_options
        sidebar.operator("frglt.duplicate_item", text="", icon='DUPLICATE').mode="set"

        sidebar = sidebar.column()
        sidebar.enabled = enable_set_options
        sidebar.separator() 
        
 
        sidebar = sidebar.column()
        sidebar.enabled = enable_set_options
        button = sidebar.operator("frglt.change_order", text="", icon='TRIA_UP')
        button.mode = "set"
        button.direction = "up"

        sidebar = sidebar.column()
        sidebar.enabled = enable_set_options
        button = sidebar.operator("frglt.change_order", text="", icon='TRIA_DOWN')
        button.mode = "set"
        button.direction = "down"
        

    def draw_header(self,context):
        pass
    @classmethod
    def poll(cls, context):

        manager = context.scene.FRGLT_manager
        
        if manager.category_types_show == True:
            return False
        else:
            return True

class FRGLT_PT_manager_cfg(FRGLT_PT_manager_sub):
    bl_label = "Configure"
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        layout = self.layout
        manager = context.scene.FRGLT_manager
        preferences = bpy.context.preferences.addons[__name__].preferences

        if len(manager.sets)>0: 
            
            box = layout.box()

            current = manager.sets[manager.index.sets]

            row = box.row()
            
            row.prop(current,"quick",text="Show in quick panel")
            
            if len(manager.categories)>0:
            
                if preferences.categoryAs == "buttons":
                    style = True
                else:
                    style = False

                if manager.cfg.categories.overwrite.style==True:
                    if manager.cfg.categories.style=="buttons":
                        style = True
                    else:
                        style = False

                row.prop(current,"categories_list",expand=style)
           
            row = box.row()
            use_icon = "FILE_PARENT"
            if current.parent == current.name:
                use_icon = "ERROR" 
            
            
            ICON = "FILE_PARENT"
            text =""
            
           
            if current.parent == -1:
                text = "Select Parent"
            else:                
                parent = manager.get_by_id(current.parent)   
                if current.parent == -1:
                    text = "Select Parent"

                elif parent == False :
                    text = "Error: parent ID:"+str(current.parent)+" not found."
                    ICON = "ERROR"
                elif parent != False:                    
                    text = parent.name
            
            label = "Select Parent"
            row.menu("FRGLT_MT_settings_parent_menu",text=text,icon=ICON)

class FRGLT_PT_manager_collections(FRGLT_PT_manager_sub):
    bl_label = "Collections"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        manager = context.scene.FRGLT_manager
        current = manager.sets[manager.index.sets]
    



        list = layout.row()        
        list.prop(current.default.collections,"use_default",text="")
        list = list.row(align=True)   
        list.enabled = False
        if current.default.collections.use_default == True:
            list.enabled = True
        list.label(text="Default Settings for all collections")

        if current.default.collections.viewport_hide == True:
            viewport_hide_icon = "HIDE_ON"
        else:
            viewport_hide_icon= "HIDE_OFF"

        if current.default.collections.render_disable == True:
            render_disable_icon = "RESTRICT_RENDER_ON"
        else:
            render_disable_icon= "RESTRICT_RENDER_OFF"
        
        if current.default.collections.exclude == False:
            exclude_icon = "CHECKBOX_HLT"
        else:
            exclude_icon = "CHECKBOX_DEHLT"

        if current.default.collections.selection_disable == False:
            selection_disable_icon = "RESTRICT_SELECT_OFF"
        else:
            selection_disable_icon = "RESTRICT_SELECT_ON"

        if current.default.collections.viewport_disable == False:
            viewport_disable_icon = "RESTRICT_VIEW_OFF"
        else:
            viewport_disable_icon = "RESTRICT_VIEW_ON"

        if current.default.collections.holdout == False:
            holdout_icon = "HOLDOUT_OFF"
        else:
            holdout_icon = "HOLDOUT_ON"

        if current.default.collections.indirect_only == False:
            indirect_only_icon = "INDIRECT_ONLY_OFF"
        else:
            indirect_only_icon = "INDIRECT_ONLY_ON"


        list.prop(current.default.collections,"exclude",text="",icon=exclude_icon,emboss=False)
        list.prop(current.default.collections,"selection_disable",text="",icon=selection_disable_icon,emboss=False)
        list.prop(current.default.collections,"viewport_hide",text="",icon=viewport_hide_icon,emboss=False)
        list.prop(current.default.collections,"viewport_disable",text="",icon=viewport_disable_icon,emboss=False)        
        list.prop(current.default.collections,"render_disable",text="",icon=render_disable_icon,emboss=False)
        list.prop(current.default.collections,"holdout",text="",icon=holdout_icon,emboss=False)
        list.prop(current.default.collections,"indirect_only",text="",icon=indirect_only_icon,emboss=False)
        

        list = layout.row()
        list.template_list("FRGLT_UL_manager_sets_collections", "", current, "collections", current.index, "collections",rows=9, type="DEFAULT")
        
        list_sidebar = list.column(align=True)
        list_sidebar_add = list_sidebar.row(align=True)
        list_sidebar_add.operator("frglt.manager_add", text="", icon='ADD').mode = "collections"
        list_sidebar_add = list_sidebar.row(align=True)
        list_sidebar_add.operator("frglt.manager_remove", text="", icon='REMOVE').mode = "collections"

class FRGLT_PT_manager_objects(FRGLT_PT_manager_sub):
    bl_label = "Objects"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        manager = context.scene.FRGLT_manager
        current = manager.sets[manager.index.sets]
    

        list = layout.row()        
        list.prop(current.default.objects,"use_default",text="")
        list = list.row(align=True)   
        list.enabled = False
        if current.default.objects.use_default == True:
            list.enabled = True
        list.label(text="Default settings for all objects")

        if current.default.objects.viewport_hide == True:
            viewport_hide_icon = "HIDE_ON"
        else:
            viewport_hide_icon= "HIDE_OFF"

        if current.default.objects.render_disable == True:
            render_disable_icon = "RESTRICT_RENDER_ON"
        else:
            render_disable_icon= "RESTRICT_RENDER_OFF"

        if current.default.objects.selection_disable == False:
            selection_disable_icon = "RESTRICT_SELECT_OFF"
        else:
            selection_disable_icon = "RESTRICT_SELECT_ON"

        if current.default.objects.viewport_disable == False:
            viewport_disable_icon = "RESTRICT_VIEW_OFF"
        else:
            viewport_disable_icon = "RESTRICT_VIEW_ON"

        list.prop(current.default.objects,"selection_disable",text="",icon=selection_disable_icon,emboss=False)
        list.prop(current.default.objects,"viewport_hide",text="",icon=viewport_hide_icon,emboss=False)
        list.prop(current.default.objects,"viewport_disable",text="",icon=viewport_disable_icon,emboss=False)
        list.prop(current.default.objects,"render_disable",text="",icon=render_disable_icon,emboss=False)

        list = layout.row()
        list.template_list("FRGLT_UL_manager_sets_objects", "", current, "objects", current.index, "objects",rows=9, type="DEFAULT")
        
        list_sidebar = list.column(align=True)
        list_sidebar_add = list_sidebar.row(align=True)
        list_sidebar_add.operator("frglt.manager_add", text="", icon='ADD').mode = "objects"
        list_sidebar_add = list_sidebar.row(align=True)
        list_sidebar_add.operator("frglt.manager_remove", text="", icon='REMOVE').mode = "objects"

class FRGLT_PT_manager_attr(FRGLT_PT_manager_sub):
    bl_label = "Attributes"

    def draw(self, context):
        manager = context.scene.FRGLT_manager
        item_stack = {}
        types = get_setting_types()
        for cat in types:
            for i in types[cat]:
                item_stack[i] = types[cat][i]
        
        #print(manager.index.sets)
        #pass
        current = manager.sets[manager.index.sets]

        layout = self.layout

        
        layout.menu("FRGLT_MT_manager_items",text="Add Attribute")
        item_index = 0
        list = layout.row()
        list.template_list("FRGLT_UL_manager_sets_attrs", "", current, "attrs", current.index, "attrs",rows=9, type="DEFAULT")
        
        
        sidebar = list.column(align=True)
             
        sidebar.operator("frglt.manager_remove", text="", icon='REMOVE').mode="attr"
        sidebar.separator()
        
        up_button = sidebar.operator("frglt.change_order", text="", icon='TRIA_UP')
        up_button.mode = "set"
        up_button.direction = "up"
                
        down_button = sidebar.operator("frglt.change_order", text="", icon='TRIA_DOWN')
        down_button.mode = "set"
        down_button.direction = "down"



#Addon Preferences

class FRGLT_manager_addon_preferences(AddonPreferences):
    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __name__

    linuxTerminal: EnumProperty(
        name="Terminal for Bacth Rendering",
        items = [("gnome-terminal --","Gnome Terminal",""),("custom","Custom","Specify terminal command"),("none","None","Renders in Background")],
        default = "gnome-terminal --"
        
    )
    linuxTerminalCustom: StringProperty(
        name="custom terminal"

    )

    windowsTerminal: EnumProperty(
        name="Terminal for batch rendering",
        items = [("cmd","CMD",""),("custom","Custom","")],
        default = "cmd"
        
    )


    categoryAs: EnumProperty(
        name="Show Category as",
        items = [("buttons","Buttons",""),("list","List","")]
        
    )
    labelAs: EnumProperty(
        name="Show Category Labels as",
        items = [("text","Text",""),("icons","Icons",""),("texticons","Text & Icons","")]
        
    )

    renderButtonAll: BoolProperty(
        name="All",
        default = True
    )

    renderButtonSelected: BoolProperty(
        name="Selected",
        default = True
    )

    renderButtonCurrent: BoolProperty(
        name="Current",
        default = True
    )

    renderButtonFrame: BoolProperty(
        name="Frame",
        default = True
    )

    renderButtonAnimation: BoolProperty(
        name="Animation",
        default = True
    )


    def draw(self, context):
        layout = self.layout
        layout.label(text="Default settings for the Manager configuration. Can be overwritten manually in the Panel.")
        
        categoriesBox = layout.box()
        categories = categoriesBox.row(align=True)
        categories.label(text="Show categories as")
        categories.prop(self, "categoryAs",expand=True)
        categories = categoriesBox.row(align=True)
        categories.label(text="Show category labels as")
        categories.prop(self, "labelAs",expand=True)
        

        renderButtonsBatchBox = layout.box()

        renderButtonsBatch = renderButtonsBatchBox.row(align=True)
        renderButtonsBatch.label(text="Show batch render buttons")
        renderButtonsBatch.prop(self,"renderButtonAll",toggle = 1)
        renderButtonsBatch.prop(self,"renderButtonSelected",toggle = 1)
        renderButtonsBatch.prop(self,"renderButtonCurrent",toggle = 1)
        
        renderButtonsSingleBox = layout.box()

        renderButtonsSingle = renderButtonsSingleBox.row(align=True)
        renderButtonsSingle.label(text="Show Render Buttons in List")
        renderButtonsSingle.prop(self,"renderButtonFrame",toggle = 1)
        renderButtonsSingle.prop(self,"renderButtonAnimation",toggle = 1)
        
        system = platform.system()
        if system =="Windows":

            windows = layout.box()
            row = windows.row(align=True)
            row.label(text="Windows only")
            row = windows.row(align=True)
            row.prop(self, "windowsTerminal")

        elif system=="Linux":

            linux = layout.box()
            
            row = linux.row(align=True)
            row.label(text="Linux only")
            row = linux.row(align=True)
            row.prop(self, "linuxTerminal")
            if self.linuxTerminal == "custom":
                row = linux.row(align=True)
                row.prop(self, "linuxTerminalCustom")



#Register Variables 

register_operators = [ 
    FRGLT_OP_manager_export,
    FRGLT_OP_manager_import,
    FRGLT_OP_manager_set_active_set,
    FRGLT_manager_addon_preferences,
    FRGLT_OP_manager_edit_category,
    FRGLT_OP_manager_select_category,
    FRGLT_OP_manager_start_batch,
    FRGLT_OP_manager_duplicate,
    FRGLT_OP_manager_icon_search,
    FRGLT_OP_manager_batch_render,
    FRGLT_OP_manager_add_item,
    FRGLT_OP_manager_add,
    FRGLT_OP_manager_remove,
    FRGLT_OP_manager_format_apply,    
    FRGLT_OP_manager_add_parent,
    FRGLT_OP_manager_render_animation,
    FRGLT_OP_manager_render_frame,
    FRGLT_OP_manager_category_set_icon,
    FRGLT_OP_manager_change_order

]

register_menus = [
    FRGLT_MENU_manager_items,
    FRGLT_MENU_manager_items_format,
    FRGLT_MENU_manager_sets_parent,
    FRGLT_MENU_icons
]
 
register_properties = [
    FRGLT_PROP_manager_sets_index,
    FRGLT_PROP_manager_index,
    FRGLT_PROP_manager_cfg_categories_overwrite, 
    FRGLT_PROP_manager_cfg_categories,
    FRGLT_PROP_manager_cfg_render_overwrite,
    FRGLT_PROP_manager_cfg_render_buttons_list,
    FRGLT_PROP_manager_cfg_render_buttons_batch,
    FRGLT_PROP_manager_cfg_render_buttons,
    FRGLT_PROP_manager_cfg_render,
    FRGLT_PROP_manager_cfg,
    FRGLT_PROP_manager_sets_collections,
    FRGLT_PROP_manager_sets_objects,
    FRGLT_PROP_manager_sets_default,
    FRGLT_PROP_manager_categories,
    FRGLT_PROP_manager_sets_attr,
    FRGLT_PROP_manager_sets,
    FRGLT_PROP_manager   
]
 
register_list = [
    FRGLT_UL_manager_sets_collections,
    FRGLT_UL_manager_sets_objects,
    FRGLT_UL_manager_sets_attrs,
    FRGLT_UL_manager_sets,
    FRGLT_UL_manager_quick
    
]
 
register_panels= [
    FRGLT_PT_manager_quick_main,    
    FRGLT_PT_manager_quick_render,
    FRGLT_PT_manager_quick_sets,
    FRGLT_PT_manager_main,
    FRGLT_PT_manager_configure_categories,
    FRGLT_PT_manager_configure_render,
    FRGLT_PT_manager_sets,
    FRGLT_PT_manager_cfg,
    FRGLT_PT_manager_collections,
    FRGLT_PT_manager_objects,
    FRGLT_PT_manager_attr
   
    
]


#Register Functions

def register():
    

    for cls in register_operators:
        register_class(cls)

    for cls in register_menus:
        register_class(cls)

    for cls in register_properties:
        register_class(cls)
    
    Scene.FRGLT_manager = PointerProperty(type=FRGLT_PROP_manager,name="The Manager")
    

    for cls in register_list:
        register_class(cls)
     
    for cls in register_panels:
        register_class(cls) 
    
  

def unregister():


    for cls in register_operators:
        unregister_class(cls)

    for cls in register_menus:
        unregister_class(cls)


    for cls in register_properties:
        unregister_class(cls)
    
    
    del Scene.FRGLT_manager
        
    for cls in register_list:
        unregister_class(cls)
    
    for cls in register_panels:
        unregister_class(cls)
    
if __name__ == "__main__":
    register()