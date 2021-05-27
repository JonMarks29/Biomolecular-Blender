# Selection class to handle and generate atom based selections

import bpy
from mathutils import Vector

from random import random as rand
import numpy as np


import all_textures
import animation_tools


global SELECTIONS, SELECT_DICT
SELECTIONS, SELECT_DICT = {}, {}

class Selection():
    def __init__(self, name, selphrase, file_parent, texture, rgba):
        self.name = name
        self.selphrase = selphrase
        self.file_parent = file_parent

        self.atoms = []
        
        self.read(selphrase)
        self.set_texture(texture, rgba)

    
    def read(self, selphrase):
        sel_options = {'res': self.res_sele, 'notres': self.res_sele_not, 
                       'atom': self.atom_sele, 'notatom': self.atom_sele_not,
                       'atomandres': self.atom_and_res_sele,
                       'dist':self.dist_sele}
        if selphrase[0] in ['res', 'notres', 'atom', 'notatom']:
            
            try:
                sel_options[selphrase[0]](selphrase[1])
                
            except:
                print(selphrase, 'selection not understood')
                
        elif selphrase[0] in ['dist']:
            if len(selphrase) == 4:
                selgroup = selphrase[-1]
            elif len(selphrase) == 3:
                selgroup = self.file_parent.atomnames 
            try:
                sel_options[selphrase[0]](selphrase[1], selphrase[2], selgroup)
            except:
                print(selphrase, 'selection not understood')
                
        elif selphrase[0] in ['atomandres']:
            try:
                sel_options[selphrase[0]](selphrase[1], selphrase[2])
            except:
                print(selphrase, 'selection not understood')
        print(len(self.atoms), 'atoms selected')
            
    
    # selects based on the atom name, returns list of of selected GroAtoms
    def atom_sele(self, sel_list):
        for atom in self.file_parent.all_atoms:
            if atom.atomname in sel_list:
                self.atoms.append(atom)
    
    # inverse selects based on the atom name, returns list of of selected GroAtoms
    def atom_sele_not(self, not_sel_list):
        for atom in self.file_parent.all_atoms:
            if atom.atomname not in not_sel_list:
                self.atoms.append(atom)
    
    # selects based on resiude name, returns list of of selected GroAtoms
    def res_sele(self, sel_list):
        for atom in self.file_parent.all_atoms:
            if atom.resname in sel_list:
                self.atoms.append(atom)
    
    # inverse selects based on resiude name, returns list of of selected GroAtoms
    def res_sele_not(self, not_sel_list):
        for atom in self.file_parent.all_atoms:
            if atom.resname not in not_sel_list:
                self.atoms.append(atom)
    
    # logical 'and' selection based on an atomname AND residename list, returns list of of selected GroAtoms
    def atom_and_res_sele(self, atom_list, res_list):
        for atom in self.file_parent.all_atoms:
            if atom.atomname in atom_list and atom.resname in res_list:
                self.atoms.append(atom)
    
    # selects based on distance cutoff from given 'center' coordinates, and on atoms by the sel_list is specified
    def dist_sele(self, center, cutoff, sel_list):
        xc,yc,zc = center
        resnumb = set()
        for atom in self.file_parent.all_atoms:
            if atom.x < xc+cutoff and atom.x > xc-cutoff and atom.y < yc+cutoff and atom.y > yc-cutoff and atom.z < zc+cutoff and atom.z > zc-cutoff:
                if atom.resname in sel_list:
                    resnumb.add(atom.resnumb)
        for atom in self.file_parent.all_atoms:
            if atom.resnumb in resnumb:
                self.atoms.append(atom)
                

    # generates ribbon structure of the protein backbone
    # ONLY IMPLEMENTED FOR CG GROFILES (ie 'BB' BEADS)
    def ribbon(self):
        self.atom_sele(['BB'])

        # create curve datablock
        curveData = bpy.data.curves.new('temp_curve', type='CURVE')
        curveData.dimensions = '3D'
        curveData.resolution_u = 1

        # create polyline
        polyline = curveData.splines.new('POLY')
        polyline.points.add(len(self.atoms)-1)

        for i in range(len(self.atoms)):
            x,y,z = self.atoms[i].coors
            polyline.points[i].co = (x, y, z, 0.5)

        # create curve object and bevel
        n = 'bb_'+str(i)
        curve_ob = bpy.data.objects.new(n, curveData) 
        curveData.bevel_depth = 0.06
        curveData.bevel_resolution = 1
        
        # add to scene to visualise
        bpy.context.scene.collection.objects.link(curve_ob)  

        shaders = {'simple':all_textures.simple, 'texture1':all_textures.texture1}
        shaders[self.texture](self, self.name, self.rgba)
        
        ob = bpy.data.objects[n]
        ob.active_material = bpy.data.materials[self.name]     
 
                

    def set_texture(self, texture, rgba=None):
        
        self.texture = texture
        if rgba == None:
            rgba = self.rgba
        else:
            self.rgba = rgba
        shaders = {'simple':all_textures.simple, 'texture1':all_textures.texture1}
        
        #print(self.name, rgba)
        shaders[texture](self, self.name, rgba)
        
        if 'Sphere_'+self.name in bpy.data.objects:
            
            ob = bpy.data.objects['Sphere_'+self.name]
            ob.active_material = bpy.data.materials[self.name]

    
    def set_color(self, rgba):
        self.rgba = rgba
        



    # finds the center point of the selected coordinates, returns tuple coordinates (x,y,z)
    def center(self, atoms=False):
        if not atoms:
            atoms = self.atoms
        x,y,z = 0,0,0
        for atom in atoms:
            x += atom.x
            y += atom.y
            z += atom.z
        return (x/len(atoms), y/len(atoms), z/len(atoms))
        


    # handles particle systems generation by iterating over each key, value pair in the selections dictionary
    def create(self):
        #make box for particle system generation
        if 'BOX' not in  bpy.data.objects:
            xl,yl,zl = self.file_parent.box 
            ob = bpy.ops.mesh.primitive_cube_add(location=(xl/2, yl/2, zl/2))
            ob = bpy.context.object
            ob.name = 'BOX'
            ob.scale=(xl,yl,zl)
            ob.location = self.file_parent.center


        
        #make instancing sphere
        ob = bpy.ops.mesh.primitive_uv_sphere_add(location=(-100,-100,-100))
        ob = bpy.context.object
        #ob.hide_viewport = True
        #ob.hide_render = True
        bpy.ops.object.shade_smooth()
        ob.name = 'Sphere_'+self.name
    
        # gets and assigns the material names after the selection key
        mat = bpy.data.materials.get(self.name)
        ob.data.materials.append(mat)
        
        # calls particle_sys to make the particle system
        self.particle_sys()
            
        # set particle location, and handles blender context requirements
        bpy.app.handlers.frame_change_post.clear()
        
        bpy.app.handlers.frame_change_post.append(particleSetter)
        bpy.context.scene.frame_current = 1


    
    #creates the particle system
    def particle_sys(self):
        particle_count = len(self.atoms)
        
        ob = bpy.data.objects['BOX']

        degp = bpy.context.evaluated_depsgraph_get()
        particle_systems = ob.evaluated_get(degp).particle_systems
        count = len(particle_systems)
        
        SELECT_DICT[self.name] = count

   
        # Prepare particle system
        ob.modifiers.new(self.name, 'PARTICLE_SYSTEM')
        ob.particle_systems[count].settings.count = particle_count
        ob.particle_systems[count].settings.frame_start = 1
        ob.particle_systems[count].settings.frame_end = 1
        ob.particle_systems[count].settings.lifetime = 1000
        ob.particle_systems[count].settings.emit_from = 'VOLUME'
        ob.particle_systems[count].settings.render_type = 'OBJECT'
        ob.particle_systems[count].settings.instance_object = bpy.data.objects["Sphere_"+self.name]
        
        
        if self.file_parent.filetype == 'PDB':
            ob.particle_systems[count].settings.particle_size = 0.1
        elif self.file_parent.filetype == 'GRO':
            ob.particle_systems[count].settings.particle_size = 0.3
            
        ob.show_instancer_for_viewport = False
        ob.show_instancer_for_render = False
        
        bpy.context.scene.use_gravity = False
        #clear the post frame handler
        bpy.app.handlers.frame_change_post.clear()
        
        

    
# converts the sel_atoms GroAtom coordinates or velocities into a completely flatlist of x,y,z (or vx,vy,vz)
def flatList_convert(atoms, t='loc'):
    flatList = []
    if t == 'loc':
        for atom in atoms:
            flatList += [atom.x, atom.y, atom.z]
        
        return flatList
    elif t == 'vel':
        for atom in atoms:
            flatList += [atom.vx, atom.vy, atom.vz]
        return flatList    

    
# sets particle location
def particleSetter(self):

    current_particles = []
    for i in bpy.data.objects.keys(): 
        if i[0:7] == 'Sphere_':
            print(i)
            current_particles.append(i[7:])
    select_dict_keys = list(SELECT_DICT.keys())
    for j in select_dict_keys:
        if j not in current_particles:
            print('removing', j, 'from SELECT_DICT')
            del SELECT_DICT[j]
    
    print(SELECT_DICT)
    ob = bpy.data.objects["BOX"]
    degp = bpy.context.evaluated_depsgraph_get()
    particle_systems = ob.evaluated_get(degp).particle_systems
    
    for sel_name, particlesys_index in SELECT_DICT.items():
        atoms = SELECTIONS[sel_name].atoms
    
        print(sel_name, 'particle setter')
    
        particles = particle_systems[particlesys_index].particles
        totalParticles = len(particles)
    
        scene = bpy.context.scene
        cFrame = scene.frame_current
        sFrame = scene.frame_start
        eFrame = scene.frame_end

        # at start-frame, clear the particle cache
        if cFrame == sFrame:
            psSeed = ob.particle_systems[particlesys_index].seed
            ob.particle_systems[particlesys_index].seed = psSeed

        flatList = flatList_convert(atoms)

        # Set the location of all particle locations to flatList
        particles.foreach_set("location", flatList)




def selection_handler(self, name, selphrase, texture='simple', rgba=(0.6,0.6,0.6,1)):
    sel = Selection(name, selphrase, self, texture=texture, rgba=rgba)
    self.selection[name] = sel
    SELECTIONS[name] = sel
    return sel









        
