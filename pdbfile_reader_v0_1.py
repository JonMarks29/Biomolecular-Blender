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
from fileobject_class import Atomfile
import selection

from Bio.PDB import MMCIFParser


standard_atom_col = {'C': (0.7, 0.7, 0.7, 1), 'N': (0,0,0.6,1), 'H': (0.7, 0.7, 1, 1), 
                'O': (0.6, 0, 0, 1), 'S': (0.5, 0.5, 0, 1), 'F': (0.4, 0.1, 0, 1)}  # F is for iron (intended)
    
bb_atoms = ['C','CA','N','O']



# class set-up for each pdb atom
class Atom():
    def __init__(self, atomnumb, atomname, resnumb, resname, x, y, z, occupancy, bfactor):
        self.atomnumb = atomnumb      # atom number as in the pdb_file
        self.resnumb = resnumb             # residue number, as in pdb file
        self.resname = resname          # the residue 3 letter name
        self.atomname = atomname            # atom element name as in pdb file, eg: CA, C, HZ, HD1...
        self.x = x
        self.y = y
        self.z = z    
        self.occupancy = occupancy      # a float of the occupancy as in pdb file
        self.bfactor = bfactor          #a float of the bfactor as in pdb file

        self.center = (self.x, self.y, self.z)



class PDB(Atomfile):
    def __init__(self, file, id='prot', model_number=1, chain_number=1):
        super().__init__(file)  #file string, all_atoms list, resnames set(), atomnames set(), selection {}
        self.model_number = model_number
        self.chain_number = chain_number
        self.id = id
        
        self.filetype = 'PDB'
        
        # convert self.all_atoms list to numpy array to improve function
        # will change this to an array in the Atomfile class at some point
        self.all_atoms = np.array(self.all_atoms)
        
        self.pdb_read()
    
    def pdb_read(self):
        print('reading', self.file)
        parser = MMCIFParser(QUIET=False)
        data = parser.get_structure(self.id, self.file)

        model = data.get_models()
        models = list(model)
        print('considering model ', self.model_number, ' only, to open a different model pass model_number to PDB object')
        chains = list(models[self.model_number-1].get_chains())
        print('considering chain ', self.chain_number, ' only, to open a different chain pass chain_number to PDB object')
        residues = list(chains[self.chain_number-1].get_residues())
        
        atom_count = 0
        x,y,z = list(residues[0].get_atoms())[0].get_coord()
        x,y,z = x/10,y/10,z/10
        xmax, xmin, ymax, ymin, zmax, zmin = x,x,y,y,z,z
        xcent, ycent, zcent = 0,0,0
        for residue in residues:
            temp_atoms = list(residue.get_atoms())
            for atom in temp_atoms:
                atom_count += 1
                x,y,z = atom.get_coord()
                x,y,z = x/10,y/10,z/10
                xcent, ycent, zcent = xcent+x, ycent+y, zcent+z
                
                if x > xmax:
                    xmax = x
                elif x < xmin:
                    xmin = x
                
                if y > ymax:
                    ymax = y
                elif y < ymin:
                    ymin = y
                    
                if z > zmax:
                    zmax = z
                elif z < zmin:
                    zmin = z
                
                current_atom = Atom(atomnumb=atom_count, atomname=atom.get_name(), resnumb=atom.get_parent().id[1], resname=atom.get_parent().get_resname(), x=x,y=y,z=z, occupancy=atom.occupancy, bfactor=atom.bfactor)                
                self.all_atoms = np.append(self.all_atoms, current_atom)
    
        self.box = (xmax-xmin, ymax-ymin,zmax-zmin)
        xcent, ycent, zcent = xcent/atom_count, ycent/atom_count, zcent/atom_count
        self.center = (xcent, ycent, zcent)
        print(atom_count, 'atoms loaded from', len(residues), 'residues')
        print('box coordinates',  xmax, xmin, ymax, ymin, zmax, zmin, '\n')
    

    def select(self, name, selphrase, texture='simple', rgba=(0.6,0.6,0.6,1)):
        sel = selection.selection_handler(self, name, selphrase, texture=texture, rgba=rgba)
        return sel
    
    def select_bb(self, texture='simple'):
        bb_c = self.select('bb_c', ('atom', ['C']), texture=texture, rgba=(0,0.5,0.08,1))
        bb_ca = self.select('bb_ca', ('atom', ['CA']), texture=texture, rgba=(0,0.5,0.08,1))
        bb_n = self.select('bb_n', ('atom', ['N']), texture=texture, rgba=(0,0,0.6,1))
        bb_o = self.select('bb_o', ('atom', ['O']), texture=texture, rgba=(0.6,0,0,1))
        
        bb_c.create()
        bb_ca.create()
        bb_n.create()
        bb_o.create()


    

    
    

# basic usage

# pdbfile = PDB(file)
# pdbfile.select_bb(texture='texture1')
# ss = pdbfile.select('ss', ('notatom', bb_atoms), texture='simple', rgba=(0.5,0.5,0.5,1))
# ss.create()
# pdbfile.light_simple()


