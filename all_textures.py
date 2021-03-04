# texture options
import bpy



# generates VERY simple material (non-node based), called name and with the rgb color
def simple(name, rgba):
    if name in bpy.data.materials:
        bpy.data.materials[name].name = name+".001"
    bpy.data.materials.new(name=name)
    bpy.data.materials[name].use_nodes = False
    bpy.data.materials[name].diffuse_color = rgba
    bpy.data.materials[name].specular_intensity = 0.2
    bpy.data.materials[name].roughness = 0.8 

# generates basic node based texture1
# A single noise shader combined with a color ramp and particle location info
def texture1(name='default', rgba=(0.1,0.1,0.1,1)):
    r,g,b,a=rgba

    # create node-material and clear
    if name in bpy.data.materials:
        bpy.data.materials[name].name = name+".001"
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    for node in nodes:
        nodes.remove(node)

    # create nodes 
    output = nodes.new('ShaderNodeOutputMaterial')
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    add1 = nodes.new('ShaderNodeMath')
    ramp1 = nodes.new('ShaderNodeValToRGB')
    noise1 = nodes.new('ShaderNodeTexNoise')
    mix1 = nodes.new('ShaderNodeMixRGB')
    particleinfo = nodes.new('ShaderNodeParticleInfo')
    geometry = nodes.new('ShaderNodeNewGeometry')

    #set node location
    output.location = (1000, 350)
    principled.location = (700, 350)
    ramp1.location = (365,350)
    mix1.location = (100,350)
    noise1.location = (-200,350)
    add1.location = (-500,250)
    particleinfo.location = (-800,125)
    geometry.location = (-800,475)

    #set node parameters
    add1.operation = 'ADD'
    add1.inputs[0].default_value = 2.5
    ramp1.color_ramp.elements[0].position = 0.3
    ramp1.color_ramp.elements[1].position = 0.7
    ramp1.color_ramp.elements[0].color = (r/4, g/4, b/4, 1)
    ramp1.color_ramp.elements[1].color = rgba
    noise1.inputs[2].default_value = 4
    noise1.inputs[3].default_value = 0
    noise1.inputs[4].default_value = 0.4
    mix1.inputs[0].default_value = 0.65
    principled.inputs[4].default_value = 0.25
    principled.inputs[5].default_value = 0.66
    principled.inputs[7].default_value = 0.9

    # link nodes
    link = mat.node_tree.links
    link.new(principled.outputs[0], output.inputs[0])
    link.new(ramp1.outputs[0], principled.inputs[0])
    link.new(mix1.outputs[0], ramp1.inputs[0])
    link.new(noise1.outputs[1], mix1.inputs[1])
    link.new(geometry.outputs[0], noise1.inputs[0])
    link.new(ramp1.outputs[0], principled.inputs[0])
    link.new(add1.outputs[0], noise1.inputs[5])
    link.new(particleinfo.outputs[1], add1.inputs[1])
