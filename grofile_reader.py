########THIS SCRIPT IS WRITTEN TO BE USED WITH BOTH BLENDER GUI AND THE CONSOLE
########ENSURE THE CONSOLE IS OPEN BEFORE USE
########THIS CAN BE ACCESSED THOUGH: Window > Toggle System Console
########        OR WITH THE COMMAND:  bpy.ops.wm.console_toggle()
########        OR BY LAUNCHING BLENDER FROM THE THE TERMINAL


import bpy
from mathutils import Vector

from random import random as rand
import numpy as np


import all_textures
#import animation_tools




global SELECTIONS, SELECT_DICT, pi
SELECTIONS, SELECT_DICT, pi = {}, {}, 3.141


# class set-up for each atom/bead in the gro file
class GroAtom():
    def __init__(self, resnumb, resname, atomname, atomnumb, x,y,z,vx=None,vy=None,vz=None):
        self.resnumb = resnumb
        self.resname = resname
        self.atomname = atomname
        self.atomnumb = atomnumb
        self.x = x
        self.y = y
        self.z = z
        self.vx = vx
        self.vy = vy
        self.vz = vz


class Selection():
    def __init__(self, name, selphrase, grofile_parent, texture, rgba):
        self.name = name
        self.selphrase = selphrase
        self.grofile_parent = grofile_parent

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
                selgroup = grofile.atomnames 
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
        for atom in grofile.all_atoms:
            if atom.atomname in sel_list:
                self.atoms.append(atom)
    
    # inverse selects based on the atom name, returns list of of selected GroAtoms
    def atom_sele_not(self, not_sel_list):
        for atom in grofile.all_atoms:
            if atom.atomname not in not_sel_list:
                self.atoms.append(atom)
    
    # selects based on resiude name, returns list of of selected GroAtoms
    def res_sele(self, sel_list):
        for atom in grofile.all_atoms:
            if atom.resname in sel_list:
                self.atoms.append(atom)
    
    # inverse selects based on resiude name, returns list of of selected GroAtoms
    def res_sele_not(self, not_sel_list):
        for atom in grofile.all_atoms:
            if atom.resname not in not_sel_list:
                self.atoms.append(atom)
    
    # logical 'and' selection based on an atomname AND residename list, returns list of of selected GroAtoms
    def atom_and_res_sele(self, atom_list, res_list):
        for atom in grofile.all_atoms:
            if atom.atomname in atom_list and atom.resname in res_list:
                self.atoms.append(atom)
    
    # selects based on distance cutoff from given 'center' coordinates, and on atoms by the sel_list is specified
    def dist_sele(self, center, cutoff, sel_list):
        xc,yc,zc = center
        resnumb = set()
        for atom in grofile.all_atoms:
            if atom.x < xc+cutoff and atom.x > xc-cutoff and atom.y < yc+cutoff and atom.y > yc-cutoff and atom.z < zc+cutoff and atom.z > zc-cutoff:
                if atom.resname in sel_list:
                    resnumb.add(atom.resnumb)
        for atom in grofile.all_atoms:
            if atom.resnumb in resnumb:
                self.atoms.append(atom)
                

    def set_texture(self, texture, rgba=None):
        
        self.texture = texture
        if rgba == None:
            rgba = self.rgba
        else:
            self.rgba = rgba
        shaders = {'simple':all_textures.simple, 'texture1':all_textures.texture1}
        
        print(self.name, rgba)
        shaders[texture](self.name, rgba)
        
        if 'Sphere_'+self.name in bpy.data.objects:
            
            ob = bpy.data.objects['Sphere_'+self.name]
            ob.active_material = bpy.data.materials[self.name]

    
    def set_color(self, rgba):
        self.rgba = rgba
        



    # finds the center point of the selected coordinates, returns tuple coordinates (x,y,z)
    def center(self):
        x,y,z = 0,0,0
        for atom in self.atoms:
            x += atom.x
            y += atom.y
            z += atom.z
        return (x/len(self.atoms), y/len(self.atoms), z/len(self.atoms))
        


    # handles particle systems generation by iterating over each key, value pair in the selections dictionary
    def create(self):
        #make box for particle system generation
        if 'BOX' not in  bpy.data.objects:
            xl,yl,zl = self.grofile_parent.box 
            ob = bpy.ops.mesh.primitive_cube_add(location=(xl/2, yl/2, zl/2))
            ob = bpy.context.object
            ob.name = 'BOX'
            ob.scale=(xl,yl,zl)


        
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
        
        print(CUR_SEL)
        
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
        global CUR_SEL 
        CUR_SEL = self.name
        
        
        # Prepare particle system
        ob.modifiers.new(self.name, 'PARTICLE_SYSTEM')
        ob.particle_systems[count].settings.count = particle_count
        ob.particle_systems[count].settings.frame_start = 1
        ob.particle_systems[count].settings.frame_end = 1
        ob.particle_systems[count].settings.lifetime = 1000
        ob.particle_systems[count].settings.emit_from = 'VOLUME'
        ob.particle_systems[count].settings.render_type = 'OBJECT'
        ob.particle_systems[count].settings.instance_object = bpy.data.objects["Sphere_"+self.name]
        
        ob.particle_systems[count].settings.particle_size = 0.3
        ob.show_instancer_for_viewport = False
        ob.show_instancer_for_render = False
        
        bpy.context.scene.use_gravity = False
        #clear the post frame handler
        bpy.app.handlers.frame_change_post.clear()
        
        
        #degp = bpy.context.evaluated_depsgraph_get()
        #par_system = ob.evaluated_get(degp).particle_systems
        #particles = par_system[count].particles
        
        
        #scene = bpy.context.scene
        #cFrame = scene.frame_current
        #sFrame = scene.frame_start
        #eFrame = scene.frame_end
        
        # at start-frame, clear the particle cache
        #if cFrame == sFrame:
        #    psSeed = ob.particle_systems[count].seed
        #    ob.particle_systems[count].seed = psSeed

        #frame = 8
        #par_system.seed += 1
        #par_system.seed -= 1
        
        #flatList = flatList_convert(self.atoms)
        #for i in range(frame):
        #    bpy.context.scene.frame_set(i)
            #particles.foreach_get("location", par_loc)
            #print(par_loc)
    
            #par_loc += 0.2
        #    particles.foreach_set("location", flatList)
    

        #bpy.context.scene.frame_current = 1



    
# converts the sel_atoms GroAtom coordinates or velocities into a completely flatlist of x,y,z (or vx,vy,vz)
def flatList_convert(atoms, t='loc'):
    flatList = []
    if t == 'loc':
        for atom in atoms:
            if atom.resname in aa:
                flatList += [atom.x, atom.y, atom.z]
            else:
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






# class to store all information from single grofile or 
class Gro():
    def __init__(self, file):
        # file: string of filepath opened
        # title: string
        # count: integer couint of number of beads/atoms in file
        # box: tuple of three floats: (x,y,z)
        # all_atoms: list of all the atoms in the structure as GroAtom
        # resnames: set of all the uniue residue names
        # atomnames: set of all the unique atom names
        # selection: dictionary of rhe selection objects, populated after initialisation (via select() method)

        self.file = file
        self.all_atoms = []
        self.resnames = set()
        self.atomnames = set()
        self.selection = {}
        
        with open(file) as f:
            lines = f.readlines()
        
        self.title = lines[0][:-1]
        self.count = int(lines[1][:-1].strip())
        self.box = (float(lines[-1].split()[0]), float(lines[-1].split()[1]), float(lines[-1].split()[2]))
        
        print('reading file with title: ', lines[0][:-1])
        print('number of atoms/beads in file: ', lines[1][:-1])
        print('boxsize (xyz):', lines[-1][:-1])
        
        # initially tries to read gro files with velocity data, if fails reads it without velocity data
        for l in lines[2:-2]:
            try:
                self.all_atoms.append(GroAtom(int(l[0:5].strip()), l[5:10].strip(), l[10:15].strip(), int(l[15:20].strip()), float(l[20:28].strip()), float(l[28:36].strip()), float(l[36:44].strip()), float(l[44:52].strip()), float(l[52:60].strip()), float(l[60:68].strip())))
            except ValueError:
                self.all_atoms.append(GroAtom(int(l[0:5].strip()), l[5:10].strip(), l[10:15].strip(), int(l[15:20].strip()), float(l[20:28].strip()), float(l[28:36].strip()), float(l[36:44].strip())))
            self.resnames.add(l[5:10].strip())
            self.atomnames.add(l[10:15].strip())            
            
            # reports progress by considering atom number 
            if int(l[15:20])%4000 == 0:
                print('at gro atom numb: ', int(l[15:20]))
                
        print('all atom bead names:', self.atomnames)

    # generate selection using Selection class and adds it to the Gro.selection dictionary   
    def select(self, name, selphrase, texture='simple', rgba=(0.6,0.6,0.6,1)):
        sel = Selection(name, selphrase, self, texture=texture, rgba=rgba)
        self.selection[name] = sel
        SELECTIONS[name] = sel
        CUR_SEL = name
        return sel

    # generates a three point light set, brightest at back, intermediate close to protein right, weak far from protein left
    def light_simple(self):
        # move objects origin to the geometry centre of the box   
        #bpy.data.objects['BOX'].select_set(True)
        #bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
    
        xb,yb,zb = self.box
        # generate three point light - note the location and brightness is currently fixed
        back_light = bpy.ops.object.light_add(type='POINT', radius=0.5, align='WORLD', location=(xb/2, -yb*2, 0))
        bpy.context.object.data.energy = 1000000
        front_right = bpy.ops.object.light_add(type='POINT', radius=0.5, align='WORLD', location=(xb*3, yb*2, zb))
        bpy.context.object.data.energy = 100000
        front_left = bpy.ops.object.light_add(type='POINT', radius=0.5, align='WORLD', location=(-xb*2, yb*1.5, zb*2))
        bpy.context.object.data.energy = 75000
    
        # create camera - note this is usually placed 100 away in the y-axis from objects mid-point, rotation is defualt
        bpy.ops.object.camera_add(location=(-xb*0.5, yb+40, zb*1.5), rotation=(1.309, 0, 3.5256))
        bpy.context.scene.render.film_transparent = True
    

   
    def find_center(self):
        x,y,z = 0,0,0
        for i in self.all_atoms:
            x += i.x
            y += i.y
            z += i.z
        n = self.count
        return (x/n, y/n, z/n)


# helper function to deselect everything and then only select the inputted object
def select_only_protein(ob):
    obj = bpy.context.scene.objects[ob]
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    return obj





# bead names for various MARTINI CG lipids and other useful groups
DPPE = ['NH3','PO4','GL1','GL2','C1A','C2A','C3A','C4A','C1B','C2B','C3B','C4B']
CDL2 = ['C5B1', 'GL22', 'C4B1', 'D3A1', 'C2B1', 'PO42', 'C4A1', 'GL11', 'C4A2', 'C2A2', 'C2B2', 'D3B2', 
        'C1B2', 'C1A2', 'D3B1', 'C5A1', 'C1A1', 'GL12', 'C1B1', 'D3A2', 'C2A1', 'GL21', 'C5A2']
DLPG = ['GL0','PO4','GL1','GL2','C1A','D2A','C3A','C4A','C1B','D2B','C3B','C4B']    
RAMP = ['S25', 'C2E', 'S16', 'C2B', 'S12', 'S21', 'S26', 'C1E', 'S34', 'S20', 'S06', 'S36', 'C2F', 'C3B',
        'GM4', 'GM2', 'GM5', 'C1A', 'C2D', 'S07', 'S09', 'S17', 'S24', 'S04', 'S28', 'S13', 'GL4', 'C2C',
        'S05', 'GM3', 'S01', 'S10', 'S14', 'S30', 'GL1', 'GL5', 'C3C', 'C1B', 'S03', 'S22', 'PO2', 'S23',
        'C1C', 'S08', 'S29', 'GL7', 'S15', 'S31', 'GL2', 'S02', 'C1D', 'S19', 'S27', 'S32', 'C3D', 'GM6',
        'C1F', 'S33', 'S18', 'S11', 'GL6', 'GL3', 'GL8', 'C2A', 'C3A', 'S37', 'S35']
lps_oant = ['O40',  'O41',  'O42',  'O43',  'O44',  'O45',  'O46',  'O47',  'O48',  
            'O49',  'O50',  'O51',  'O52',  'O53',  'O54',  'O55',  'O56',  'O57', 
            'O58',  'O59',  'O60',  'O61',  'O62',  'O63',  'O64',  'O65',  'O66',  
            'O67',  'O68',  'O69',  'O70',  'O71',  'O72',  'O73',  'O74',  'O75',  
            'O76',  'O77',  'O78',  'O79',  'O80',  'O81',  'O82',  'O83',  'O84',  
            'O85',  'O86',  'O87',  'O88',  'O89',  'O90',  'O91',  'O92',  'O93',  
            'O94',  'O95',  'O96',  'O97',  'O98',  'O99']

tails = ['C1A','C2A','C3A','C4A','C1B','C2B','C3B','C4B']
pl_head = ['NH3','GL1','GL2']
phosphate = ['PO4', 'PO2', 'PO1']
lps_head = ['S25', 'S16', 'S12', 'S21', 'S26', 'S34', 'S20', 'S06', 'S36',
        'GM4', 'GM2', 'GM5', 'S07', 'S09', 'S17', 'S24', 'S04', 'S28', 'S13', 'GL4',
        'S05', 'GM3', 'S01', 'S10', 'S14', 'S30', 'GL5', 'S03', 'S22', 'S23',
        'S08', 'S29', 'GL7', 'S15', 'S31', 'S02', 'S19', 'S27', 'S32', 'GM6',
        'S33', 'S18', 'S11', 'GL6', 'GL3', 'GL8', 'S37', 'S35', 'S36', 'S37', 'S38',
        'S39', 'GL1', 'GL2']
lps_tails = ['C2E','C2B','C1E','C2F', 'C3B', 'C1A', 'C2D', 'C2C',
             'C3C', 'C1B', 'C1C', 'C1D', 'C3D','C1F', 'C2A', 'C3A']

aa = ['ILE', 'SER', 'ASN', 'GLU', 'ARG', 'MET', 'CYS', 'THR', 'TYR', 'ASP', 
        'GLY', 'LEU', 'LYS', 'PHE', 'HIS', 'TRP', 'PRO', 'ALA', 'VAL', 'GLN']

prot = ['BB','SC1', 'SC2', 'SC3', 'SC4']






