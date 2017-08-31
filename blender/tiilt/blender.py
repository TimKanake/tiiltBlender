import sys
sys.path.append('.')
import bpy
import bgl
import socket
import json
import math
import logging
import mathutils
import bpy_extras.view3d_utils
import pickle
import time
import numpy
import unicodedata


def read_command(transport):
    try:
        line = transport.recv(2048)
        data = pickle.loads(line)
        print('Data has been received')
        if not line:
            return
    except ValueError as e:
        logging.exception(e)
        raise IOError()

    try:
        cmd = data['verb']
        del data['verb']
    except KeyError as e:
        logging.exception(e)
        raise IOError()

    return cmd, data


'''Selects the object that the user is staring at'''
def gazed_object(pos):
    obj_name =  find_object_by_coordinates(pos)
    select_object(obj_name)

'''Returns vector coordinates based on a quantity and direction. For example given 2 and top it returns (x_coordinate, quantity, z_coordinate) '''
def coord_calc(quantity, direction):
    if direction == [u'top'] or direction == [u'up']:
        return [bpy.data.screens['Default'].scene.cursor_location[0], quantity, bpy.data.screens['Default'].scene.cursor_location[2]]
    elif direction == [u'bottom'] or direction == [u'down']:
        return [bpy.data.screens['Default'].scene.cursor_location[0], -(quantity), bpy.data.screens['Default'].scene.cursor_location[2]]
    elif direction == [u'right']:
        return [quantity, bpy.data.screens['Default'].scene.cursor_location[1], bpy.data.screens['Default'].scene.cursor_location[2]]
    elif direction == [u'left']:
        return [-(quantity), bpy.data.screens['Default'].scene.cursor_location[1], bpy.data.screens['Default'].scene.cursor_location[2]]
    else:
        return [0,0,0]


'''coordinate calculation for move command. Returns coord
inates with ony the move direction specified'''

def move_coord_calc(coords, obj_location):
    pos = bpy_extras.view3d_utils.region_2d_to_location_3d(bpy.context.region, bpy.context.space_data.region_3d, mathutils.Vector((coords[0], bpy.data.scenes["Scene"].render.resolution_y - coords[1])), mathutils.Vector((0,0,0)))
    quantity = [pos[0]-obj_location[0], pos[1]-obj_location[1], 0]
    return quantity


def move_coord_calc2(quantity, direction, obj_name):
    if direction == [u'top'] or direction == [u'up']:
        return [0, quantity,0]
    elif direction == [u'bottom'] or direction == [u'down']:
        return [0, -(quantity), 0]
    elif direction == [u'right']:
        return [quantity, 0,0]
    elif direction == [u'left']:
        return [-(quantity), 0,0]
    else:
        return [0,0,0]

'''Calculates the distance betweent two points on the screen'''

def calc_min_distance(obj1_loc, obj2_loc):
    dist = (obj1_loc[0]-obj2_loc[0])**2 + (obj1_loc[1]-obj2_loc[1])**2
    return math.sqrt(dist)


'''Given an object specifier such as the word 'cube' this method finds it and returns its name
Only works if just one of that kind of object is on screen'''

def find_object(obj_specifier):
    scene = bpy.context.scene
    obj_counter = 0;
    real_object = None
    for ob in scene.objects:
        if ob.name.startswith(obj_specifier):
            real_object = ob
            obj_counter = obj_counter + 1

    if obj_counter > 1 or real_object is None:
        raise Exception('Please specify which ' + obj_specifier + ' you want.')
    else:
        return real_object.name


def find_object_by_coordinates(coords):
    scene = bpy.context.scene
    min_dist = 1000000000
    real_object = None

    for ob in scene.objects:
        distance_b2n = calc_min_distance(coords, ob.location[:2])
        if distance_b2n < min_dist:
            min_dist = distance_b2n
            real_object = ob

    return real_object.name   


'''Selects an object and makes it the active object
    obj_name : The name of the object as stored in blender
'''
def select_object(obj_name):
    curr_obj = bpy.context.selected_objects
    
    if len(curr_obj) > 0:
        bpy.ops.object.select_all(action = 'TOGGLE')
    
    bpy.context.scene.objects.active = bpy.data.objects[obj_name]
    bpy.data.objects[obj_name].select = True




class TIILTOperator(bpy.types.Operator):
    bl_idname = "object.tiilt"
    bl_label = "TIILT Operator"

    # TODO use Blender's Properties
    # sock_addr = bpy.props.StringProperty(name="Server address")

    def __init__(self):
        print("Starting")
        self.transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sockfile = None

        _commands = [
        self.undo,
        self.redo,
        self.add,
        #self.move,
        self.quit,
        self.view,
        self.delete,
        self.clear,
        self.rename,
        self.change,
        #self.select,
        ]

        self.commands = {f.__name__:f for f in _commands}
        self._timer = None

        self.current_mode = 'OBJECT'
    def __del__(self):
        print("Ending")
        self.transport.close()

        if self.sockfile:
            self.sockfile.close()

        print("End")

    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D'

    def execute(self, context):
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type == 'ESC':
            context.window_manager.event_timer_remove(self._timer)
            return {'FINISHED'}

        if event.type == 'TIMER':
            bpy.ops.view3d.viewnumpad(type = 'TOP')
            try:
                cmd = read_command(self.transport)
            except IOError as e:
                logging.exception(e)
            else:
                if cmd:
                    func, kwargs = cmd
                    if func in self.commands:
                        self.commands[func](kwargs)


        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        try:
            self.transport.connect(('localhost', 8888))
            self.sockfile = self.transport.makefile()

        except IOError as e:
            logging.exception(e)
            return {'CANCELLED'}

        print("Started")
        bpy.ops.view3d.viewnumpad(type = 'TOP')
        self._timer = context.window_manager.event_timer_add(0.01, context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    '''changes the view direction of the screen'''

    def view_temp(self, obj):
        unicode.normalize('NKFD', obj['direction']).encode('ascii', 'ignore').decode("utf-8")
        bpy.ops.view3d.viewnumpad(type = dirct.upper())

    def view(self, dict):
        coords = dict['coord']
        pos = bpy_extras.view3d_utils.region_2d_to_location_3d(bpy.context.region, bpy.context.space_data.region_3d, mathutils.Vector((coords[0], bpy.data.scenes["Scene"].render.resolution_y - coords[1])), mathutils.Vector((0,0,0)))
        gazed_object(pos)

    '''adds an object to the screen'''
    def add(self, dict):
        shape = dict['object']
        obj_pos = dict['quantity']
        obj_direction = dict['direction']
        coords = dict['coord']
        if (obj_pos != [u''] and obj_direction != [u'']):
            pos = coord_calc(obj_pos, obj_direction) 
        else:
            pos = bpy_extras.view3d_utils.region_2d_to_location_3d(bpy.context.region, bpy.context.space_data.region_3d, mathutils.Vector((coords[0], bpy.data.scenes["Scene"].render.resolution_y - coords[1])), mathutils.Vector((0,0,0)))

        bpy.context.scene.cursor_location = mathutils.Vector((pos[0], pos[1], 0))
        if(shape == 'cube'):
            bpy.ops.mesh.primitive_cube_add()
        elif (shape == 'monkey'):
            bpy.ops.mesh.primitive_monkey_add()
        elif (shape == 'cylinder'):
            bpy.ops.mesh.primitive_cylinder_add()
        elif (shape == 'cone'):
            bpy.ops.mesh.primitive_cone_add()
        elif (shape == 'circle'):
            bpy.ops.mesh.primitive_circle_add()
        else:
            pass

    '''kills the timer to allow control via blender interface
        NEED TO PRESS ESC KEY FROM BLENDER INTERFACE TO COMPLETELY GAIN CONTROL
    '''
    def quit(self,otherStuff):
        bpy.context.window_manager.event_timer_remove(self._timer)
        return {'FINISHED'}


    '''Moves the selected object to the point where the user is staring at'''
    def change(self, dict):
        obj_location = mathutils.Vector(bpy.context.scene.objects.active.location)
        bpy.ops.transform.translate(value = move_coord_calc(dict['coord'], obj_location))

    '''renames the selected/active object'''
    def rename(new_name):
        bpy.data.objects[bpy.context.scene.objects.active.name].name = new_name

    '''undo the previous command'''
    def undo(self, dict):
        bpy.ops.ed.undo()

    '''redo the previous command'''
    def redo(self, dict):
        bpy.ops.ed.redo()


    '''clears all objects from the screen'''
    def clear(self):
        if not bpy.context.selected_objects:
            bpy.ops.object.select_all(actions = 'TOGGLE') 
        bpy.ops.object.select_all(actions = 'TOGGLE')
        bpy.ops.object.delete(use_global = False)


    '''delete the selected object from screen'''
    def delete(self, dict):
        bpy.ops.object.delete(use_global)




bpy.utils.register_class(TIILTOperator)