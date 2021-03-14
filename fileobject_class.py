# generic class for all atom/coordinate based fileobjects that can be loaded

import bpy

class Atomfile():
    def __init__(self, file):
        self.file = file
        self.all_atoms = []
        self.resnames = set()
        self.atomnames = set()
        self.selection = {}
        

    # generates a three point light set, brightest at back, intermediate close to protein right, weak far from protein left
    def light_simple(self):
        # move objects origin to the geometry centre of the box   
        #bpy.data.objects['BOX'].select_set(True)
        #bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
    
        xc,yc,zc = self.center
        # generate three point light - note the location and brightness is currently fixed
        back_light = bpy.ops.object.light_add(type='POINT', radius=0.5, align='WORLD', location=(xc, -yc*4, 0))
        bpy.context.object.data.energy = 1000000
        front_right = bpy.ops.object.light_add(type='POINT', radius=0.5, align='WORLD', location=(xc*6, yc*4, zc*2))
        bpy.context.object.data.energy = 100000
        front_left = bpy.ops.object.light_add(type='POINT', radius=0.5, align='WORLD', location=(-xc*4, yc*3, zc*4))
        bpy.context.object.data.energy = 75000
    
        # create camera - note this is usually placed 100 away in the y-axis from objects mid-point, rotation is default
        bpy.ops.object.camera_add(location=(-xc, yc+yc+40, zc*3), rotation=(1.309, 0, 3.5256))
        bpy.context.scene.render.film_transparent = True