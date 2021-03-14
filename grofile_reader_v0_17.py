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
import animation_tools
import selection
from fileobject_class import Atomfile



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

        self.coors = (self.x, self.y, self.z)


# class to store all information from single grofile or 
class Gro(Atomfile):
    def __init__(self, file):
        super().__init__(file)
        
        self.filetype = 'GRO'
        
        self.gro_read()
        
        
    def gro_read(self):
        with open(self.file) as f:
            lines = f.readlines()
            
        xcent, ycent, zcent = 0,0,0
        self.title = lines[0][:-1]
        self.count = int(lines[1][:-1].strip())
        self.box = (float(lines[-1].split()[0]), float(lines[-1].split()[1]), float(lines[-1].split()[2]))
        
        print('reading file with title: ', lines[0][:-1])
        print('number of atoms/beads in file: ', lines[1][:-1])
        print('boxsize (xyz):', lines[-1][:-1])
        
        # initially tries to read gro files with velocity data, if fails reads it without velocity data
        for l in lines[2:-2]:
            x,y,z = float(l[20:28].strip()), float(l[28:36].strip()), float(l[36:44].strip()) 
            try:
                self.all_atoms.append(GroAtom(int(l[0:5].strip()), l[5:10].strip(), l[10:15].strip(), int(l[15:20].strip()), x,y,z, float(l[44:52].strip()), float(l[52:60].strip()), float(l[60:68].strip())))
            except ValueError:
                self.all_atoms.append(GroAtom(int(l[0:5].strip()), l[5:10].strip(), l[10:15].strip(), int(l[15:20].strip()), x,y,z))
            self.resnames.add(l[5:10].strip())
            self.atomnames.add(l[10:15].strip()) 
            xcent, ycent, zcent = xcent+x, ycent+y, zcent+z  
            
            # reports progress by considering atom number 
            if int(l[15:20])%4000 == 0:
                print('at gro atom numb: ', int(l[15:20]))
                
        print('all atom bead names:', self.atomnames)
        self.center = (xcent/self.count, ycent/self.count, zcent/self.count)



    def select(self, name, selphrase, texture='simple', rgba=(0.6,0.6,0.6,1)):
        sel = selection.selection_handler(self, name, selphrase, texture=texture, rgba=rgba)
        return sel

        



# basic usage

#grofile = Gro(file)
#grofile.light_simple()
#lps = grofile.select('lps', ('res', ['REMP','RAMP','OANT']), texture='texture1', rgba=(0.2,0.2,0.2,1))
#lps.create()




