#Todo: Make sure to follow Blender Best Practices Found here: https://docs.blender.org/api/current/info_best_practice.html

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
#    Scene Properties --- JUMPIPROP
# ------------------------------------------------------------------------
#Scene Properties go here.
def serial_force_update(self,context): #Todo: Move this to a better place
    pass
    return None

class SerialMainProperties(PropertyGroup): #This PropertyGroup defines what a SerialProperties PropertyGroup is like, it doesn't actually add anything to the scene.
    serial_main_freeze_bool: BoolProperty( #This property just demonstrates how to make a check box. It doesn't do anything else yet
        name="Freeze",
        description="Temporarily Stop All Transmission",
        default = True,
        update=serial_force_update
        )
    serial_main_mode_enum: EnumProperty(
        name="Operating Mode",
        description="Select Operation Mode",
        items=[ ('OFF', "OFF", ""),
                ('RECEIVE', "RECEIVE", ""),
                ('SEND', "SEND", ""),
                ],
        default = 'OFF',
        update=serial_force_update
    )
    serial_main_path: StringProperty( #Use this to declare a property for opening a file path
        name = "Profile File",
        description="Choose a directory",
        default="",
        maxlen=1024,
        subtype='DIR_PATH',#This line is what makes a difference
        update=serial_force_update 
        )
    serial_main_baud_enum: EnumProperty(
        name="Baudrate",
        description = "baud rate",
        items=[ ('9600', "9600", ""),
                ],
        default = '9600',
        update=serial_force_update
    )
    serial_main_com_enum: EnumProperty(
        name="Serial Port",
        description = "Serial Port choice",
        items=[ ('COM5', "COM5", ""),
        ],
        default = 'COM5',#The Non-Windows Version should have a different default
        update=serial_force_update 
    )
    serial_main_timeout_float: FloatProperty(
        name="Timeout value",
        description = "For setting up the Serial communications",
        default = 1,
        update=serial_force_update
    )
    serial_device_open: BoolProperty(default=False, update=serial_force_update)

class SerialRecProperties(PropertyGroup):
    rec_defaults_box_open: BoolProperty(
        name = "Open Default Options",
        description = "Open or Close the Defaults Box",
        default=False,
        update=serial_force_update
    )
    serial_receiving_profiles: EnumProperty( #This creates an EnumProperty. It looks like a Visual Studio ComboBox when drawn
        name="Receiving Profile",
        description="Pick a receiving Profile",
        items=[ ('OP40', "3D Mouse", ""),
                ('OP50', "Human Doll", ""),
                ('OP60', "Dog Doll", ""),
                ('OP70', "Dragon Doll", ""),
                ('OP80', "Horse Doll", ""),
                ('OP90', "Lemur Foot Prototype No. 1", ""),
                ('OP100', "Dwarf Model", ""),
                ('OP101', "Elf Model", ""),
                ('OP102', "Monster ID 32 Model", "")
                ],
        update=serial_force_update
        )
    rec_path: StringProperty( #Use this to declare a property for opening a file path
        name = "Profile File",
        description="Choose a directory",
        default="",
        maxlen=1024,
        subtype='DIR_PATH',#This line is what makes a difference
        update=serial_force_update 
        )
    rec_new_int: IntProperty(
        name = "Default Int",
        description = "Int To Send To New ListBox Item",
        default = 0,
        update=serial_force_update
        )
    rec_new_string: StringProperty(
        name = "Default String",
        description="String To Send To New ListBox Item",
        default="",
        maxlen=1024,
        update=serial_force_update
        )
    rec_new_bool: BoolProperty(
        name="Default Boolean",
        description="Boolean To Send To New ListBox Item",
        default = False,
        update=serial_force_update
        )
    rec_default_freeze_bool: BoolProperty(
        name="Default Freeze",
        description="Freeze By Default?",
        default = True,
        update=serial_force_update
        )
    rec_new_float: FloatProperty(
        name="Default Float",
        description="Float to send to new item",
        default = 0.0,
        update=serial_force_update
    )

class SerialSendProperties(PropertyGroup):
    serial_sending_profiles: EnumProperty(
        name="Sending Profile",
        description="Pick a sending Profile",
        items=[ ('OP40', "Automatically Posing Control Puppet", ""),
                ('OP50', "Robot", ""),
                ('OP60', "Origami Robot Action Figure", ""),
                ('OP70', "Pinball Table", ""),
                ('OP80', "Miniture", ""),
                ('OP90', "Moving Poster: Insert Action Movie Here", ""),
                ('OP100', "Waldo Bot", ""),
                ('OP101', "External Art Program", ""),
                ('OP102', "Holographic Box", "")
                ],
        update=serial_force_update
        )
    send_defaults_box_open: BoolProperty(
        name = "Open Default Options",
        description = "Open or Close the Defaults Box",
        default=False,
        update=serial_force_update
    )
    send_new_int: IntProperty(
        name = "Default Int",
        description = "Int To Send To New ListBox Item",
        default = 0,
        update=serial_force_update
        )
    send_new_string: StringProperty(
        name = "Default String",
        description="String To Send To New ListBox Item",
        default="",
        maxlen=1024,
        update=serial_force_update
        )
    send_new_bool: BoolProperty(
        name="Default Boolean",
        description="Boolean To Send To New ListBox Item",
        default = False,
        update=serial_force_update
        )
    send_default_freeze_bool: BoolProperty(
        name="Default Freeze",
        description="Freeze by Default?",
        default = True,
        update=serial_force_update
        )
    send_new_float: FloatProperty(
        name="Default Float",
        description="Float to send to new item",
        default = 0.0,
        update=serial_force_update
    )

class RecEntry(PropertyGroup):
    rec_data_type: EnumProperty(
        name = "Default Data Type",
        items=(
            ('Int', "Integer", ""),
            ('Float', "Float", ""),
            ('String', "String", ""),
            ('Bool', "Boolean", ""),
        ),
        update=serial_force_update
    )
    rec_input_type: EnumProperty(
        name = "Default Device Type",
        items=(
            ('Potentiometer', "Potentiometer", ""),
            ('Encoder', "Encoder", ""), #Todo: figure out and define best practice for where to handle encoder counting stuff
            ('Button', "Button", ""),
            ('VirtualToggleBtn', "VirtualToggleBtn", "") #When all you have is a regular button but you need a toggle button
        ),
        update=serial_force_update
    )
    rec_int: IntProperty(update=serial_force_update) #Stores value of data as Int
    rec_string: StringProperty(update=serial_force_update)
    rec_float: FloatProperty(update=serial_force_update) #Stores value of data as Float
    rec_bool: BoolProperty(update=serial_force_update) #Stores value as Boolean Property
    rec_freeze_bool: BoolProperty(name="freeze", description="freeze", default=True,update=serial_force_update)

class RecGroup(PropertyGroup):
    coll: CollectionProperty(type=RecEntry)
    index: IntProperty(update=serial_force_update)

class SendEntry(PropertyGroup):
    send_data_type: EnumProperty(
        name = "Default Data Type",
        items=(
            ('Int', "Integer", ""),
            ('Float', "Float", ""),
            ('String', "String", ""),
            ('Bool', "Boolean", ""),
        ),
        update=serial_force_update
    )
    send_input_type: EnumProperty(
        name = "Default Target",
        items=(
            ('Motor', "Motor", ""),
            ('Actuator', "Actuator", ""), #Todo: figure out and define best practice for where to handle encoder counting stuff
            ('LED', "LED", ""),
            ('Alarm', "Alarm", ""),
        ),
        update=serial_force_update
    )
    send_int: IntProperty(update=serial_force_update) #Stores value of data as Int
    send_string: StringProperty(update=serial_force_update)
    send_float: FloatProperty(update=serial_force_update) #Stores value of data as Float
    send_bool: BoolProperty(update=serial_force_update) #Stores value as Boolean Property
    send_freeze_bool: BoolProperty(name="freeze", description="freeze", default=True,update=serial_force_update)

class SendGroup(PropertyGroup): #Preemptively split the classes by sending or receiving
    coll: CollectionProperty(type=SendEntry)
    index: IntProperty(update=serial_force_update)

# ------------------------------------------------------------------------
#    Defs ---- JUMPIDEFS
# ------------------------------------------------------------------------
#I don't know if this is good policy, but since these defs were getting reused a lot and might need rewriting later, rather than have it in multiple places to get rewritten I'm putting them all here
class sermod: #Don't put this before the properties.
    def recIfTree(self, context, targettype, targetthing, countup):
        scene = context.scene

        try:
            if targettype == 'Int':
                scene.rec_prop_group.coll[countup].rec_int = int(targetthing)
            elif targettype == 'Float':
                scene.rec_prop_group.coll[countup].rec_float = float(targetthing)
            elif targettype == 'Bool':
                scene.rec_prop_group.coll[countup].rec_bool = bool(targetthing)
            elif targettype == 'String':
                scene.rec_prop_group.coll[countup].rec_string = str(targetthing)
            else:
                pass
        except:
            print("error at iftree")
        finally:
            return
    
    def recShortTree(self, context, dumb, data): #My intuition says either Long Tree or Short Tree is bad. But idk which. -IA
        scene = context.scene
        
        if len(data) > dumb:
            switch_thing = data
        elif len(data) < dumb:
            switch_thing = scene.rec_prop_group.coll
        elif len(data) == dumb:
            switch_thing = data
        
        countup = 0
        for thing in switch_thing:
            self.recIfTree(context, scene.rec_prop_group.coll[countup].type, thing, countup)
            countup = countup + 1
        
        return

    def recLongTree(self, context, dumb, data):
        #Since this code was getting repeated, and might get changed later as needed, it was given its own def
        scene = context.scene
        print("got to longtree")
        
        if len(data) > dumb:
            print("called data>dumb")
            #there is less data items than prop_group items
            #stop when you use all the data    
            countup = 0
                
            for thing in data:
                self.recIfTree(context, scene.rec_prop_group.coll[countup].rec_data_type, thing, countup) #Simplified.
                countup = countup + 1
            
            return
        
        elif len(data) < dumb:
            print("called dumb>data")
            #there is less prop_group items than data items
            #stop when you use all the prop_group items
            countup = 0

            for thing in scene.prop_group.coll:
                self.recIfTree(context, scene.rec_prop_group.coll[countup].rec_data_type, data[countup], countup)
                countup = countup + 1
            
            return
        
        elif len(data) == dumb:
            print("called data=dumb")
            #they're equal, use either to count up
            countup = 0
            
            for thing in data:
                self.recIfTree(context, scene.rec_prop_group.coll[countup].rec_data_type, thing, countup)
                countup = countup + 1
            
            return
        else:
            #hopefully this is impossible
            print("error in rec_long_tree")
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
    
    def sendser(self, context):
        pass
        return None

    def serRecUpdate(self, context):
        return None
    
    def serSendUpdate(self, context):
        return None

# ------------------------------------------------------------------------
#    Operators ---- JUMPIOPS
# ------------------------------------------------------------------------
#Operators are defined here. Defining them here defines what operators do when they're used.

class SERIAL_OT_serial_run(Operator, sermod):
    bl_idname = "serial.serial_run"
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
            
            self.recLongTree(context, dumb, data)
        except:
            print("Error calling longtree")
        
        return {'FINISHED'} #What happens here is that def execute is getting called last, because the invoke is saying to call the def modal first, and def modal loops until it calls the execute
    
    def invoke(self, context, event):
        scene = context.scene
        serdevice = scene.serdevice

        serialRecProps = scene.serialRecProps
        serialMainProps = scene.serialMainProps

        wm = context.window_manager
        self._timer = wm.event_timer_add(1.0, window=context.window)
        wm.modal_handler_add(self)
        #since we're executing, and hopefully not executing more than once, we should open the channel here

        try:
            #Initialize the serial
            serdevice.baudrate = Int(serialMainProps.serial_main_baud_enum)
            serdevice.port = Str(serialMainProps.serial_main_com_enum)
            serdevice.timeout = Float(serialMainProps.serial_main_timeout_float)
        except:
            print("Error during serial setup")

        try:
            #now, open it if it isn't open already
            scene.serdevice.open()
            serialMainProps.seropen = True
        except:
            print("error opening serial device/or already open")
            pass

        self.execute(context)

        return {'RUNNING_MODAL'}

    def cancel(self, context):
        scene = context.scene
        serialMainProps = scene.serialMainProps

        wm = context.window_manager
        wm.event_timer_remove(self._timer)

        scene.serdevice.close()
        serialMainProps.seropen = False

class SERIAL_OT_receive_list_add(Operator):
    bl_idname = "serial.serial_receive_list_add"
    bl_label = "Add to List"
    
    def execute(self, context):
        scene = context.scene
        item = scene.rec_prop_group.coll.add()

        serRecProps = scene.serRecProps
        rec_entry = scene.rec_entry
        
        item.name = serRecProps.rec_new_string
        item.rec_int = serRecProps.rec_new_int
        item.rec_data_type = rec_entry.rec_data_type
        item.rec_input_type = rec_entry.rec_input_type
        item.rec_bool = serRecProps.rec_new_bool
        item.rec_float = serRecProps.rec_new_float
        
        item.rec_freeze_bool = serRecProps.rec_default_freeze_bool
        
        return {'FINISHED'}

class SERIAL_OT_send_list_add(Operator):
    bl_idname = "serial.send_list_add"
    bl_label = "Add to List"
    
    def execute(self, context):
        scene = context.scene
        item = scene.send_prop_group.coll.add()

        serSendProps = scene.serSendProps
        send_entry = scene.send_entry
        
        item.name = serSendProps.send_new_string
        item.send_int = serSendProps.send_new_int
        item.send_data_type = send_entry.send_data_type
        item.send_input_type = send_entry.send_input_type
        item.send_bool = serSendProps.send_new_bool
        item.send_float = serSendProps.send_new_float
        
        item.send_freeze_bool = serSendProps.send_default_freeze_bool
        
        return {'FINISHED'}

class SERIAL_OT_modal_operator(Operator, sermod):
    bl_idname = "serial.serial_modal_operator"
    bl_label = "Serial Modal Operator"

    _timer = None

    def invoke(self, context, event):
        scene = context.scene
        serdevice = scene.serdevice
        serMainProps = scene.serMainProps

        print("TheModalOperator invoke")
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        wm.modal_handler_add(self)

        try:
            #Initialize the serial
            serdevice.baudrate = int(serMainProps.serial_main_baud_enum)
            serdevice.port = str(serMainProps.serial_main_com_enum)
            serdevice.timeout = float(serMainProps.serial_main_timeout_float)
        except:
            print("Error during serial setup")

        try:
            #now, open it if it isn't open already
            serdevice.open()
            serMainProps.seropen = True
            print("opened serdevice")
        except:
            print("error opening serial device/or already open")
            pass

        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        scene = context.scene
        serMainProps = scene.serMainProps
        #print("TheModalOperator modal", event.type, event.value)
        if event.type == 'TIMER':
            #now determine rec or send
            if serMainProps.serial_main_mode_enum == 'OFF':
                return {'FINISHED'}
            elif serMainProps.serial_main_mode_enum == 'RECEIVE':
                #print("---TheModalOperator modal pass-through")
                data = self.readser(context)
                try:
                    #Count how many are in prop_group.coll
                    dumb = 0
                    for dumber in scene.rec_prop_group.coll:
                        dumb = dumb + 1
            
                    self.recLongTree(context, dumb, data)
                except:
                    pass
                return {'RUNNING_MODAL'}
            elif serMainProps.serial_main_mode_enum == 'SEND':
                return {'FINISHED'}
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            context.window_manager.event_timer_remove(self._timer)
            return {'FINISHED'}
        else:
            if serMainProps.serial_main_mode_enum == 'OFF':
                return {'FINISHED'}
            elif serMainProps.serial_main_mode_enum == 'RECEIVE':
                data = self.readser(context)
                try:
                    #Count how many are in prop_group.coll
                    dumb = 0
                    for dumber in scene.rec_prop_group.coll:
                        dumb = dumb + 1
            
                    self.recLongTree(context, dumb, data)
                    print("did the thing")
                except:
                    print("Error calling longtree")
                return {'PASS_THROUGH'}
            elif serMainProps.serial_main_mode_enum == 'SEND':
                return {'FINISHED'} #Todo: make this do something


class SERIAL_OT_invoke_operator(Operator):
    """This is my operator"""
    bl_idname = "serial.serial_invoke_operator"
    bl_label = "Begin Serial Communications"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        print("theOperator execute")
        self.report({'INFO'}, "MyOperator executed")
        bpy.ops.serial.serial_modal_operator('INVOKE_DEFAULT')
        return {'FINISHED'}

# ------------------------------------------------------------------------
#    Panel in Object Mode ---- JUMPIPANEL
# ------------------------------------------------------------------------

class SERIAL_UL_rec_list(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "name", text="", emboss=False)
            layout.prop(item, "rec_int", text="")
            layout.prop(item, "rec_float", text="")
            layout.prop(item, "rec_data_type", text="")
            layout.prop(item, "rec_input_type", text="")
            layout.prop(item, "rec_bool", text="")

            layout.prop(item, "rec_freeze_bool", text="freeze")
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

class SERIAL_UL_send_list(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "name", text="", emboss=False)
            layout.prop(item, "send_int", text="")
            layout.prop(item, "send_float", text="")
            layout.prop(item, "send_data_type", text="")
            layout.prop(item, "send_input_type", text="")
            layout.prop(item, "send_bool", text="")
            layout.prop(item, "send_freeze_bool", text="freeze")
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

class SERIAL_PT_main_panel(Panel): #It's imprtant to have PT somewhere in the panel name
    bl_label = "Serial Panel"
    bl_idname = "SERIAL_PT_main_panel"
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
        serMainProps = scene.serMainProps
        #example_entry = scene.example_entry

        layout.prop(serMainProps, "serial_main_freeze_bool") #This needs to be able to freeze all communications when true
        layout.prop(serMainProps, "serial_main_mode_enum")
        layout.prop(serMainProps, "serial_main_baud_enum") #Select Baud Rate
        layout.prop(serMainProps, "serial_main_com_enum") #Select COM port
        layout.prop(serMainProps, "serial_main_timeout_float") #Provide Timeout value

        layout.operator("serial.serial_invoke_operator")
        layout.label(text="Right click while serial com is running to stop it.")
        

class SERIAL_PT_receiving_panel(Panel):
    bl_parent_id = "SERIAL_PT_main_panel"
    bl_label = "Receiving Panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tools"
    bl_options = {"DEFAULT_CLOSED"}
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        ser_rec_props = scene.serRecProps
        rec_entry = scene.rec_entry
        
        #setup some props for presets for rapid creation
        #don't require the user to use them, they just help
        defaultsBox = layout.box()
        defaultsBox.prop(ser_rec_props, "rec_defaults_box_open")
        if ser_rec_props.rec_defaults_box_open == True: #This box was arranged this way because it is impossible to create a sub-Panel in a sub-Panel
            defaultsBox.prop(ser_rec_props, "rec_new_string")
            defaultsBox.prop(ser_rec_props, "rec_new_int")
            defaultsBox.prop(rec_entry, "rec_data_type")
            defaultsBox.prop(rec_entry, "rec_input_type")
            defaultsBox.prop(ser_rec_props, "rec_new_bool")
            defaultsBox.prop(ser_rec_props, "rec_new_float")
            defaultsBox.prop(ser_rec_props, "rec_default_freeze_bool")
        
        layout.operator("serial.serial_receive_list_add") 
        #layout.operator("my.operator")
        layout.template_list("SERIAL_UL_rec_list", "", scene.rec_prop_group, "coll", scene.rec_prop_group, "index")

class SERIAL_PT_sending_panel(Panel):
    bl_parent_id = "SERIAL_PT_main_panel"
    bl_label = "Sending Panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tools"
    bl_options = {"DEFAULT_CLOSED"}
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        ser_send_props = scene.serSendProps
        send_entry = scene.send_entry
        
        #setup some props for presets for rapid creation
        #don't require the user to use them, they just help
        defaultsBox = layout.box()
        defaultsBox.prop(ser_send_props, "send_defaults_box_open")
        if ser_send_props.send_defaults_box_open == True:
            defaultsBox.prop(ser_send_props, "send_new_string")
            defaultsBox.prop(ser_send_props, "send_new_int")
            defaultsBox.prop(send_entry, "send_data_type")
            defaultsBox.prop(send_entry, "send_input_type")
            defaultsBox.prop(ser_send_props, "send_new_bool")
            defaultsBox.prop(ser_send_props, "send_new_float")
            defaultsBox.prop(ser_send_props, "send_default_freeze_bool")
        
        layout.operator("serial.send_list_add")
        #layout.operator("my.operator")
        layout.template_list("SERIAL_UL_send_list", "", scene.send_prop_group, "coll", scene.send_prop_group, "index")


# ------------------------------------------------------------------------
#    Registration --- JUMPIREG
# ------------------------------------------------------------------------

classes = ( #list all your classes here so you don't have to register them individually later
    RecEntry,
    RecGroup,
    SendEntry,
    SendGroup,
    SERIAL_UL_rec_list,
    SERIAL_UL_send_list,
    SERIAL_OT_receive_list_add,
    SERIAL_OT_send_list_add,
    SERIAL_OT_serial_run,
    SERIAL_OT_modal_operator,
    SERIAL_OT_invoke_operator,
    SerialMainProperties,
    SerialRecProperties,
    SerialSendProperties,
    SERIAL_PT_main_panel, #Order matters here
    SERIAL_PT_receiving_panel,
    SERIAL_PT_sending_panel
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    
    bpy.types.Scene.serMainProps = PointerProperty(type=SerialMainProperties) #You have to tell Blender what the properties apply to
    bpy.types.Scene.serRecProps = PointerProperty(type=SerialRecProperties)
    bpy.types.Scene.serSendProps = PointerProperty(type=SerialSendProperties)
    
    bpy.types.Scene.rec_prop_group = PointerProperty(type=RecGroup)
    bpy.types.Scene.rec_entry = PointerProperty(type=RecEntry)
    
    bpy.types.Scene.send_prop_group = PointerProperty(type=SendGroup)
    bpy.types.Scene.send_entry = PointerProperty(type=SendEntry)
    
    bpy.types.Scene.serdevice = serial.Serial()


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    
    del bpy.types.Scene.serMainProps #Don't forget to unregister your stuff when it's time to
    del bpy.types.Scene.serRecProps
    del bpy.types.Scene.serSendProps
    
    del bpy.types.Scene.rec_prop_group
    del bpy.types.Scene.rec_entry
    
    del bpy.types.Scene.send_prop_group
    del bpy.types.Scene.send_entry
    
    del bpy.types.Scene.serdevice

if __name__ == "__main__":
    register()
