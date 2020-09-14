import os
import bpy

mats = {}


def makeMaterial(name, diffuse, specular, alpha):
    """
    blender
    make material

    parms:
    ----
    name: mat name
    diffuse, specular: tuple rgb diff color
    alpha: alpha

    return:
    ------
    material
    """

    mat = bpy.data.materials.new(name)
    mat.diffuse_color = diffuse
    mat.diffuse_shader = 'LAMBERT'
    mat.diffuse_intensity = 1.0
    mat.specular_color = specular
    mat.specular_shader = 'COOKTORR'
    mat.specular_intensity = 0.5
    mat.alpha = alpha
    mat.ambient = 1
    return mat


def setMaterial(ob, mat):
    """
    blender
    set material mat to object ob
    """
    me = ob.data
    me.materials.append(mat)


def makeTextMat(name):
    """
    make textured material

    params:
    ------
    name - texture file name (without extension)

    return:
    ------
    material

    todo:
        change hardcoded path
    """
    # realpath = os.path.expanduser('~/snippets/textures/color.png')
    print(name)
    realpath = dn1 + '/' + name + '.png'
    # realpath = '/color.png'
    try:
        img = bpy.data.images.load(realpath)
    except:
        raise NameError("Cannot load image %s" % realpath)

    # Create image texture from image
    cTex = bpy.data.textures.new('ColorTex', type='IMAGE')
    cTex.image = img
    cTex.extension = 'REPEAT'
    # cTex.repeat_x=4
    # cTex.repeat_y=4

    mat = bpy.data.materials.new('TexMat')

    # Add texture slot for color texture
    mtex = mat.texture_slots.add()
    mtex.texture = cTex
    mtex.texture_coords = 'UV'
    mtex.uv_layer = 'UVMap'
    mtex.use_map_color_diffuse = True

    mtex.use_map_color_emission = True
    mtex.emission_color_factor = 0.5
    mtex.use_map_density = True
    mtex.mapping = 'FLAT'

    return mat


def getOrCreateTexturedMaterial(textureName):
    """
    blender
    creates, or gets from cache Material for texture

    params:
    ------

    textureName - texture file name, without extension, def .png

    return:
    ------
    material
    """
    mat = mats.get(textureName)
    if mat is not None:
        return mat
    else:
        mat = makeTextMat(textureName)
        mats[textureName] = mat
        return mat


filename = "/media/50G/v/c/_obs/BlenderScripts/tests/bmesh_001.py"
dn = os.path.dirname(os.path.abspath('__file__'))
dn1 = os.path.dirname(os.path.abspath(filename))


print(dn1)
