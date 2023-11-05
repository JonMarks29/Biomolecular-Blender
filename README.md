# Biomolecular Blender
![alt text](https://github.com/JonMarks29/Biomolecular-Blender/blob/main/overveiw_graphic_spotlit_PP_short.png)

Scripts to import, manipulate and visualise biomolecular-files in blender


Biomolecular files are loaded as objects using dedicated classes - GRO() or PDB():

grofile = GRO(filename.gro)

pdbfile = PDB(filename.pdb)


In order to display in blender a Selection object is created using the file objects select() method:

selection = pdbfile.select(selection_name, selectionphrase, texture='simple', rgba=(0.6,0.6,0.6,1))


e.g. the following will select all the atoms loaded in the pdbfile object apart from the backbone atoms C, CA, N and O; and assign them a simple texture and the given rgba colors

ss = pdbfile.select('ss', ('notatom', ['C', 'CA', 'N', 'O']), texture='simple', rgba=(0.5,0.5,0.5,1))


The selectionphrase is a tuple and typically takes the format: ('selection_method', selection_arguement/s), where selection_arguement is typically a list of atoms/beads/residues. A list of the selection_methods is found in the selection.py file

Only a single texture and color can be assigned per selection


This can then be pushed to blenders display with the selection objects create() method:

selection.create()


