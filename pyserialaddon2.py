bl_info = {
    "name": "General Pyserial for Blender",
    "description": "General pyserial add-on for Blender",
    "author": "IntrepidArtineer",
    "version": (0, 0, 1),
    "blender": (2, 81, 0),
    "location": "3D View > Tools",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "Development"
}

import bpy
import random
import serial

from bpy.props import (StringProperty, #These will get used later, and they're pretty common so might as well have them
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       CollectionProperty,
                       )
from bpy.types import (Panel,
                       Menu,
                       Operator,
                       PropertyGroup,
                       UIList,
                       )

# ------------------------------------------------------------------------
#    Scene Properties
# ------------------------------------------------------------------------

class SerialProperties(PropertyGroup):     
    serial_freeze_bool: BoolProperty( #This property just demonstrates how to make a check box. It doesn't do anything else yet
        name="Freeze",
        description="Temporarily Stop All Transmission",
        default = True
        )
    serial_receiving_profiles: EnumProperty( #This creates an EnumProperty. It looks like a Visual Studio ComboBox when drawn
        name="Receiving Profile",
        description="Pick a receiving Profile",
        items=[ ('OP40', "3D Mouse", ""),
                ('OP50', "Human Doll", ""),
                ('OP60', "Dog Doll", ""),
                ('OP70', "Dragon Doll", ""),
                ('OP80', "Horse Doll", ""),
                ('OP90', "Lemur Foot Prototype No. 1", "")
                ]
        )
    my_path: StringProperty( #Use this to declare a property for opening a file path
        name = "Profile File",
        description="Choose a directory",
        default="",
        maxlen=1024,
        subtype='DIR_PATH' #This line is what makes a difference
        )
    data_value_int: IntProperty(
        name = "Received Data As Int",
        description = "Received Data Value As An Integer",
        default = 0,
        )
        
    list_example_int: IntProperty(
        name = "User Input Int",
        description = "Int To Send To New ListBox Item",
        default = 0,
        )
    list_example_string: StringProperty(
        name = "User Input String",
        description="String To Send To New ListBox Item",
        default="",
        maxlen=1024,
        )
    list_example_bool: BoolProperty(
        name="User Input Boolean",
        description="Boolean To Send To New ListBox Item",
        default = False
        )
    list_example_float: FloatProperty(
        name="User Input Float",
        description="Float to send to new item",
        default = False
    )
    baud_enum: EnumProperty(
        name="Baudrate",
        description = "baud rate",
        items=[ ('9600', "9600", ""),
                ]
    )
    com_enum: EnumProperty(
        name="Serial Port",
        description = "Serial Port choice",
        items=[ ('COM5', "COM5", ""),
        ]
    )


class ExampleEntry(PropertyGroup):
    type: EnumProperty(
        items=(
            ('Int', "Integer", ""),
            ('Float', "Float", ""),
            ('String', "String", ""),
            ('Bool', "Boolean", ""),
        )
    )
    inputtype: EnumProperty(
        items=(
            ('Potentiometer', "Potentiometer", ""),
            ('Encoder', "Encoder", ""),
            ('Button', "Button", "")
        )
    )
    val: IntProperty() #Stores value of data as Int
    stringval: StringProperty()
    floatval: FloatProperty() #Stores value of data as Float
    ExampleBool: BoolProperty() #Stores value as Boolean Property
    freezebool: BoolProperty(name="freeze", description="freeze", default=True)

class ExampleGroup(PropertyGroup):
    coll: CollectionProperty(type=ExampleEntry)
    index: IntProperty()

# ------------------------------------------------------------------------
#    Operators
# ------------------------------------------------------------------------

class SCENE_OT_list_add(Operator):
    bl_idname = "scene.list_add"
    bl_label = "Add to List"
    
    def execute(self, context):
        item = context.scene.prop_group.coll.add()
        scene = context.scene
        serialtool = scene.serialtool
        example_entry = scene.example_entry
        
        item.name = serialtool.list_example_string
        item.val = serialtool.list_example_int
        item.type = example_entry.type
        item.inputtype = example_entry.inputtype
        item.ExampleBool = serialtool.list_example_bool
        itemfloatval = serialtool.list_example_float
        
        item.freezebool = example_entry.freezebool
        
        return {'FINISHED'}

class SCENE_OT_SerialOneScan(Operator):
    bl_idname = "scene.serial_scan_once"
    bl_label = "Get the data once"

    def execute(self, context):
        scene = context.scene
        serialtool = scene.serialtool
        example_entry = scene.example_entry

        #we need to get data for each listbox item
        #first, open communications
        try:
            serial_device = serial.Serial()
            serial_device.baudrate = 9600 #TODO: MAKE THESE ACTUALLY OBEY THE CHOICES IN THE ENUMS
            serial_device.port = 'COM5'
            serial_device.timeout = 1
            serial_device.open()
            serial_device.readline()            

            raw_string = serial_device.readline()
            line = str(raw_string)
            
            #Todo: figure out how to read an arbitrary number of sensors for an arbitrary number of items
            #For now, assume 3 sensors and 3 items
            line = line[2:] #Remove the unicode characters
            line = line[:-5] #Remove the cariage return and newline from the end of the string
            data = line.split(" ")
            try:
                #Todo:find a not dumb way to get the Len(prop_group)
                dumb = 0
                for dumber in scene.prop_group.coll:
                    dumb = dumb + 1

                if len(data) > dumb:
                    #there is less data items than prop_group items
                    #stop when you use all the data
                    countup = 0

                    for thing in data:
                        #thing is like data[x], so...
                        #next we need to figure out what to do based on the specifications for the data?
                        #or should we try to use the data for all types?
                        #But if we get a string, then what?
                        #Todo: figure out how to cast arbitrary data as any type
                        if scene.prop_group.coll[countup].type == 'Int':
                            #display thing as int
                            scene.prop_group.coll[countup].val = int(thing)
                        elif scene.prop_group.coll[countup].type == 'Float':
                            scene.prop_group.coll[countup].floatval = float(thing)
                        elif scene.prop_group.coll[countup].type == 'String':
                            scene.prop_group.coll[countup].stringval = str(thing)
                        elif scene.prop_group.coll[countup].type == 'Bool':
                            scene.prop_group.coll[countup].ExampleBool = bool(thing)
                        else:
                            pass

                        countup = countup + 1
                elif len(data) < dumb:
                    #there is less prop_group items than data items
                    #stop when you use all the prop_group items
                    countup = 0
                    for thing in scene.prop_group.coll:
                        if scene.prop_group.coll[countup].type == 'Int':
                            #display thing as int
                            scene.prop_group.coll[countup].val = int(data[countup])
                        elif scene.prop_group.coll[countup].type == 'Float':
                            scene.prop_group.coll[countup].floatval = float(data[countup])
                        elif scene.prop_group.coll[countup].type == 'String':
                            scene.prop_group.coll[countup].stringval = str(data[countup])
                        elif scene.prop_group.coll[countup].type == 'Bool':
                            scene.prop_group.coll[countup].ExampleBool = bool(data[countup])
                        else:
                            pass
                        countup = countup + 1

                elif len(data) == dumb:
                    #they're equal, use either to count up
                    countup = 0
                    for thing in data:
                        if scene.prop_group.coll[countup].type == 'Int':
                            #display thing as int
                            scene.prop_group.coll[countup].val = int(thing)
                        elif scene.prop_group.coll[countup].type == 'Float':
                            scene.prop_group.coll[countup].floatval = float(thing)
                        elif scene.prop_group.coll[countup].type == 'String':
                            scene.prop_group.coll[countup].stringval = str(thing)
                        elif scene.prop_group.coll[countup].type == 'Bool':
                            scene.prop_group.coll[countup].ExampleBool = bool(thing)
                        else:
                            pass
                        countup = countup + 1
                else:
                    #hopefully this is impossible
                    print("error 1")
            except:
                print("error 2")
        except:
            print("No serial device found")
            #exit()
        
        return {'FINISHED'}
    
# ------------------------------------------------------------------------
#    Panel in Object Mode
# ------------------------------------------------------------------------

class SCENE_UL_list(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "name", text="", emboss=False)
            layout.prop(item, "val", text="")
            layout.prop(item, "floatval", text="")
            layout.prop(item, "type", text="")
            layout.prop(item, "inputtype", text="")
            layout.prop(item, "ExampleBool", text="")

            layout.prop(item, "freezebool", text="freeze")
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)
     
class SERIAL_PT_MainPanel(Panel): #It's imprtant to have PT somewhere in the panel name
    bl_label = "Serial Panel"
    bl_idname = "SERIAL_PT_MainPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Serial" #You can replace serial in this line with any other word you want
    bl_context = "objectmode"
    @classmethod
    def poll(self,context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        obj = context.object
        serialtool = scene.serialtool
        example_entry = scene.example_entry

        layout.prop(serialtool, "serial_freeze_bool")

class SERIAL_PT_ReceivingPanel(Panel): #It's called Receiving P{anel because it was copied from my PySerial for Blender Project
    bl_parent_id = "SERIAL_PT_MainPanel"
    bl_label = "Receiving Panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tools"
    bl_options = {"DEFAULT_CLOSED"}
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        serialtool = scene.serialtool
        example_entry = scene.example_entry
        
        #setup some props for presets for rapid creation
        #don't require the user to use them, they just help
        layout.prop(serialtool, "list_example_string")
        layout.prop(serialtool, "list_example_int")
        layout.prop(example_entry, "type")
        layout.prop(example_entry, "inputtype")
        layout.prop(serialtool, "list_example_bool")
        layout.prop(serialtool, "list_example_float")
        
        layout.operator("scene.list_add")
        layout.operator("scene.serial_scan_once")
        layout.template_list("SCENE_UL_list", "", scene.prop_group, "coll", scene.prop_group, "index")

# ------------------------------------------------------------------------
#    Registration
# ------------------------------------------------------------------------

classes = ( #list all your classes here so you don't have to register them individually later
    ExampleEntry,
    ExampleGroup,
    SCENE_UL_list,
    SCENE_OT_list_add,
    SCENE_OT_SerialOneScan,
    SerialProperties,
    SERIAL_PT_MainPanel, #Order matters here
    SERIAL_PT_ReceivingPanel,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.types.Scene.serialtool = PointerProperty(type=SerialProperties) #You have to tell Blender what the properties apply to
    bpy.types.Scene.prop_group = PointerProperty(type=ExampleGroup)
    bpy.types.Scene.example_entry = PointerProperty(type=ExampleEntry)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.serialtool #Don't forget to unregister your stuff when it's time to
    del bpy.types.Scene.prop_group
    del bpy.types.Scene.example_entry

if __name__ == "__main__":
    register()
