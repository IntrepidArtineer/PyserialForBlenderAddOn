#First, put the file/Add-on details at the top. Be sure to keep them accurate!
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

#Now Import what the add-on will need
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

#Separate each section with a divider like the one below.

# ------------------------------------------------------------------------
#    Scene Properties
# ------------------------------------------------------------------------
#Scene Properties go here.
class SerialProperties(PropertyGroup): #This PropertyGroup defines what a SerialProperties PropertyGroup is like, it doesn't actually add anything to the scene.
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
                ],
        default = '9600'
    )
    com_enum: EnumProperty(
        name="Serial Port",
        description = "Serial Port choice",
        items=[ ('COM5', "COM5", ""),
        ],
        default = 'COM5' #The Non-Windows Version should have a different default
    )
    timeout_float: FloatProperty(
        name="Timeout value",
        description = "For setting up the Serial communications",
        default = 1
    )
    seropen: BoolProperty(default=False)


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
            ('Encoder', "Encoder", ""), #Todo: figure out and define best practice for where to handle encoder counting stuff
            ('Button', "Button", ""),
            ('VirtualToggleBtn', "VirtualToggleBtn", "") #When all you have is a regular button but you need a toggle button
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
#    Defs
# ------------------------------------------------------------------------
#I don't know if this is good policy, but since these defs were getting reused a lot and might need rewriting later, rather than have it in multiple places to get rewritten I'm putting them all here
class sermod:
    def iftree(self, context, targettype, targetthing, countup):
        scene = context.scene

        try:
            if targettype == 'Int':
                scene.prop_group.coll[countup].val = int(targetthing)
            elif targettype == 'Float':
                scene.prop_group.coll[countup].floatval = float(targetthing)
            elif targettype == 'Bool':
                scene.prop_group.coll[countup].ExampleBool = bool(targetthing)
            elif targettype == 'String':
                scene.prop_group.coll[countup].stringval = str(targetthing)
            else:
                pass
        except:
            print("error at iftree")
        finally:
            return
    
    def longtree(self, context, dumb, data):
        #Since this code was getting repeated, and might get changed later as needed, it was given its own def
        scene = context.scene
        print("got to longtree")
        
        if len(data) > dumb:
            print("called data>dumb")
            #there is less data items than prop_group items
            #stop when you use all the data    
            countup = 0
                
            for thing in data:
                self.iftree(context, scene.prop_group.coll[countup].type, thing, countup) #Simplified.
                countup = countup + 1
            
            return
        
        elif len(data) < dumb:
            print("called dumb>data")
            #there is less prop_group items than data items
            #stop when you use all the prop_group items
            countup = 0

            for thing in scene.prop_group.coll:
                self.iftree(context, scene.prop_group.coll[countup].type, data[countup], countup)
                countup = countup + 1
            
            return
        
        elif len(data) == dumb:
            print("caled data=dumb")
            #they're equal, use either to count up
            countup = 0
            
            for thing in data:
                self.iftree(context, scene.prop_group.coll[countup].type, thing, countup)
                countup = countup + 1
            
            return
        else:
            #hopefully this is impossible
            print("error in longtree")
            return
    
    def readser(self, context):
        #Since this might get changed on an as needed basis, it has been unified into this def
        scene = context.scene
        serdevice = scene.serdevice

        #Get a garbage line so you don't actually use garbage
        serdevice.readline()

        #Now get a real line
        raw_string = serdevice.readline()
        line = str(raw_string)

        #Now do some cleaning on the received line
        line = line[2:] #Remove the unicode characters
        line = line[:-5] #Remove the carriage return and newline from the end of the string
        data = line.split(" ") #IMPORTANT: The Serial Add-On expects the Serial data to be sent in the form of data separated by spaces, with each set of data sent as a line ended by a carriage return
        #If a change in how the data is transmitted is required, you will need to change the above section of code too.
        
        return data

# ------------------------------------------------------------------------
#    Operators
# ------------------------------------------------------------------------
#Operators are defined here. Defining them here defines what operators do when they're used.

class SCENE_OT_Serial_Run(Operator, sermod):
    bl_idname = "scene.serial_run"
    bl_label = "Run Serial Communication"

    _timer = None

    @classmethod
    def poll(cls, context): #This gets used to restrict when the operator can be called. It defines when the operator should be grayed out
        return True
    
    def __init__(self):
        print("Start Serial")
    
    def __del__(self):
        print("End Serial")

    def modal(self, context, event): #Todo: Add an undo feature, probably by having a confirm or cancel, instead of just cancell
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cancel(context)
            return {'CANCELLED'}

        if event.type == 'TIMER':
            self.execute(context)

        return {'RUNNING_MODAL'}

    def execute(self, context):
        scene = context.scene

        data = self.readser(context)

        try:
            #Count how many are in prop_group.coll
            dumb = 0
            for dumber in scene.prop_group.coll:
                dumb = dumb + 1
            
            self.longtree(context, dumb, data)
        except:
            print("Error calling longtree")
        
        return {'FINISHED'} #What happens here is that def execute is getting called last, because the invoke is saying to call the def modal first, and def modal loops until it calls the execute
    
    def invoke(self, context, event):
        scene = context.scene
        serdevice = scene.serdevice

        wm = context.window_manager
        self._timer = wm.event_timer_add(1.0, window=context.window)
        wm.modal_handler_add(self)
        #since we're executing, and hopefully not executing more than once, we should open the channel here

        try:
            #Initialize the serial
            serdevice.baudrate = Int(scene.serialtool.baud_enum)
            serdevice.port = Str(scene.serialtool.com_enum)
            serdevice.timeout = Float(scene.serialtool.timeout_float)
        except:
            print("Error during serial setup")

        try:
            #now, open it if it isn't open already
            scene.serdevice.open()
            scene.serialtool.seropen = True
        except:
            print("error opening serial device/or already open")
            pass

        self.execute(context)

        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        scene = context.scene

        scene.serdevice.close()
        scene.serialtool.seropen = False

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
        item.floatval = serialtool.list_example_float
        
        item.freezebool = example_entry.freezebool
        
        return {'FINISHED'}
        
class SCENE_OT_SerialOneScan(Operator, sermod):
    bl_idname = "scene.serial_scan_once"
    bl_label = "Get the data once"
    
    def execute(self, context):
        scene = context.scene
        serialtool = scene.serialtool
        #example_entry = scene.example_entry

        #we need to get data for each listbox item
        #first, open communications
        try:
            serdevice = scene.serdevice
            try:
                #Initialize the serial
                serdevice.baudrate = int(scene.serialtool.baud_enum)
                serdevice.port = str(scene.serialtool.com_enum)
                serdevice.timeout = float(scene.serialtool.timeout_float)
            except:
                print("Error during serial setup")
            
            try:
                serdevice.open()
                serialtool.seropen = True
            except:
                print("error in opening single scan")
            
            try:
                serdevice.readline()
            except:
                print("error in 1st readline")

            try:
                data = self.readser(context)
                print(data)
            except:
                print("error in dataget")

            try:
                #Todo:find a not dumb way to get the Len(prop_group)
                dumb = 0
                for dumber in scene.prop_group.coll:
                    dumb = dumb + 1
                print ("snort")
                print(dumb)
                self.longtree(context, dumb, data)

            except:
                print("error 2")
        except:
            print("No serial device found")
            #exit()
        try:
            serial_device.close()
        except:
            pass
        return {'FINISHED'}
  
class EXAMPLE_OT_TheModalOperator(Operator, sermod):
    bl_idname = "my.themodaloperator"
    bl_label = "TheModalOperator Operator"

    _timer = None

    def invoke(self, context, event):
        scene = context.scene
        serdevice = scene.serdevice
        serialtool = scene.serialtool

        print("TheModalOperator invoke")
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        wm.modal_handler_add(self)

        try:
            #Initialize the serial
            serdevice.baudrate = int(serialtool.baud_enum)
            serdevice.port = str(serialtool.com_enum)
            serdevice.timeout = float(serialtool.timeout_float)
        except:
            print("Error during serial setup")

        try:
            #now, open it if it isn't open already
            serdevice.open()
            serialtool.seropen = True
            print("opened serdevice")
        except:
            print("error opening serial device/or already open")
            pass

        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        scene = context.scene
        print("TheModalOperator modal", event.type, event.value)
        if event.type == 'TIMER':
            print("---TheModalOperator modal pass-through")
            data = self.readser(context)
            try:
                #Count how many are in prop_group.coll
                dumb = 0
                for dumber in scene.prop_group.coll:
                    dumb = dumb + 1
            
                self.longtree(context, dumb, data)
                print("did the thing")
            except:
                print("Error calling longtree")
            return {'PASS_THROUGH'}
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            print("---TheModalOperator modal finished")
            context.window_manager.event_timer_remove(self._timer)
            return {'FINISHED'}
        else:
            print("---TheModalOperator modal pass-through")
            data = self.readser(context)
            try:
                #Count how many are in prop_group.coll
                dumb = 0
                for dumber in scene.prop_group.coll:
                    dumb = dumb + 1
            
                self.longtree(context, dumb, data)
                print("did the thing")
            except:
                print("Error calling longtree")
            return {'PASS_THROUGH'}       


class EXAMPLE_OT_MyOperator(Operator):
    """This is my operator"""
    bl_idname = "my.operator"
    bl_label = "My Operator"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        print("MyOperator execute")
        self.report({'INFO'}, "MyOperator executed")
        bpy.ops.my.themodaloperator('INVOKE_DEFAULT')
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
        #obj = context.object
        serialtool = scene.serialtool
        #example_entry = scene.example_entry

        layout.prop(serialtool, "serial_freeze_bool")
        layout.prop(serialtool, "baud_enum")
        layout.prop(serialtool, "com_enum")
        layout.prop(serialtool, "timeout_float")

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
        layout.operator("scene.serial_run")
        layout.operator("my.operator")
        layout.template_list("SCENE_UL_list", "", scene.prop_group, "coll", scene.prop_group, "index")


# ------------------------------------------------------------------------
#    Registration
# ------------------------------------------------------------------------

classes = ( #list all your classes here so you don't have to register them individually later
    ExampleEntry,
    ExampleGroup,
    SCENE_UL_list,
    SCENE_OT_list_add,
    SCENE_OT_Serial_Run,
    SCENE_OT_SerialOneScan,
    EXAMPLE_OT_TheModalOperator,
    EXAMPLE_OT_MyOperator,
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
    bpy.types.Scene.serdevice = serial.Serial()


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.serialtool #Don't forget to unregister your stuff when it's time to
    del bpy.types.Scene.prop_group
    del bpy.types.Scene.example_entry
    del bpy.types.Scene.serdevice

if __name__ == "__main__":
    register()