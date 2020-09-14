import mathutils
import random
# from shapely.speedups._speedups import Point
from OCC.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_Surface


__author__ = 'v'

"""
filename = "/home/v/c/BlenderScripts/tests/bmesh_001.py"
filename = "/media/home2/v/c/BlenderScripts/tests/bmesh_001.py"
filename = "/media/home2/v/c/_obs/BlenderScripts/tests/bmesh_001.py"
exec(compile(open(filename).read(), filename, 'exec


run:

import sys
from importlib import reload
sys.path.append("/media/50G/v/c/_obs/BlenderScripts/tests")
import bmesh_001
dir(bmesh_001)

now can run:
bmesh_001.test_Voronoi(), etc.
"""
from OCC.BRep import BRep_Builder, BRep_Tool_Triangulation
from OCC.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeSphere
from OCC.BRepAlgoAPI import BRepAlgoAPI_Fuse
from OCC.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCC.BRepMesh import brepmesh_Mesh
from OCC.TopExp import TopExp_Explorer
from OCC.TopoDS import TopoDS_Compound, topods_Face
from OCC.TopAbs import TopAbs_FACE
from OCC.TopLoc import TopLoc_Location
from OCC.gp import gp_Pnt, gp_Vec2d, gp_Vec

from OCC.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.BRep import BRep_Tool_Pnt
# from OCC.BRepBuilderAPI import
from OCC.TopExp import TopExp_Explorer
from OCC.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_VERTEX, TopAbs_FORWARD
from OCC.TopoDS import topods_Face, topods_Vertex, TopoDS_Vertex, topods_Edge

import bpy
import bmesh
import os

# import bl_materials
from bl_materials import getOrCreateTexturedMaterial, setMaterial
from BRep_funx import BRep_triangulate



def append_to_bmesh(bm, bm_verts, bm_faces, bm_uvs):
    """
    blender
    appends new faces to bmesh

    params:
    ------

    bm - bmesh for update
    others - values to append
    """

    offs = len(bm.verts)

    for v_co in bm_verts:
        bm.verts.new(v_co)

    # add uvs to the new face
    uv_layer = bm.loops.layers.uv.verify()
    bm.faces.layers.tex.verify()

    for f_idx in bm_faces:
        # print(offs,f_idx)
        bm.verts.ensure_lookup_table()
        bm.faces.new([bm.verts[i + offs] for i in f_idx])

        bm.faces.ensure_lookup_table()
        fs = bm.faces
        # print(bm.faces)
        # print('tot faces',len(bm.faces))
        f = fs[-1]
        # print(f.loops)
        # print('tot loops',len(f.loops))
        ls = enumerate(f.loops)
        # print(list(ls))
        ls = enumerate(f.loops)
        for i, l in ls:
            # print(i, l.vert.co)
            l[uv_layer].uv = bm_uvs[f_idx[i]]


def makeSmooth(bm_object):
    """
    blender
    sets smooth shading to bm_object
    """
    bpy.context.scene.objects.active = bm_object
    bm_object.select = True
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all()
    bpy.ops.mesh.faces_shade_smooth()
    bpy.ops.object.mode_set(mode='OBJECT')
    bm_object.select = False
    # bpy.data.objects['ObjectName'].data.polygons[0].use_smooth
    for p in bm_object.data.polygons:
        p.use_smooth


def create_object_in_scene(mesh, textureName, objectName='bmObject', makeFacesSmooth=True):
    """
    blender
    create object in scene from input vals
    """
    bm_object = bpy.data.objects.new(objectName, mesh)
    mat = getOrCreateTexturedMaterial(textureName)
    setMaterial(bm_object, mat)
    scene = bpy.context.scene  # get current scene
    scene.objects.link(bm_object)

    if makeFacesSmooth:
        makeSmooth(bm_object)

    # ???? from some example
    # add the mesh as an object into the scene with this utility module
    # from bpy_extras import object_utils
    # object_utils.object_data_add(context, mesh, operator=self)

    # bpy.context.scene.objects.active=pyramid_object
    # pyramid_object.select=True
    # bpy.ops.object.mode_set(mode='EDIT')



# # to rem in favour of next
# def BRep_triangulate_to_BMesh(shape, objectName='bmObject', meshName='bmesh', textureName='colorGrid', reTestNormals=True):
#     """
#     blender
#     test
#     works for single shape
#     """
#     mesh = bpy.data.meshes.new(meshName)
#     bm = bmesh.new()
#
#     brepmesh_Mesh(shape, 0.8)
#     builder = BRep_Builder()
#     comp = TopoDS_Compound()
#     builder.MakeCompound(comp)
#
#     ex = TopExp_Explorer(shape, TopAbs_FACE)
#     while ex.More():
#         face = topods_Face(ex.Current())
#         # print(face.Orientation())
#         # if face.Orientation() == 1:
#         #     face=face.Reversed()
#         #     print('try change ',face.Orientation())
#         bm_verts, bm_faces, bm_uvs = BRepFace_triangulate_to_BMesh(
#             face, comp, builder, reTestNormals)
#         # print('bm_uvs',bm_uvs)
#         # bm_uvs=[(x[0],x[1]*2) for x in bm_uvs]
#         # print('new_bm_uvs',bm_uvs)
#         # print('bm_uvs',bm_uvs)
#         # bm_uvs = reCalcUVs(face, bm_uvs)
#         # print('new_bm_uvs',bm_uvs)
#         update_bmesh(bm, bm_verts, bm_faces, bm_uvs)
#         ex.Next()
#
#     bm.to_mesh(mesh)
#     mesh.update()
#     create_object_in_scene(mesh, textureName, objectName)
#     # return mesh
#
#     return comp  # only for OCC


def BReps_triangulate_to_BMesh(shapes, objectName='bmObject', meshName='bmesh', textureName='colorGrid', reTestNormals=True):
    """
    blender

    triangulate to bmesh and adds object to scene

    params:
    -------

    shapes - list of shapes to triangulate
    objectName - name in scene
    meshName
    """

    mesh = bpy.data.meshes.new(meshName)
    bm = bmesh.new()

    for shape in shapes:
        tris = BRep_triangulate(shape)
        for tri in tris:
            append_to_bmesh(bm,*tri)

    bm.to_mesh(mesh)
    mesh.update()
    create_object_in_scene(mesh, textureName, objectName)


def BReps_triangulate(shapes, reTestNormals=True):
    """
    triangulate BReps

    params:
    -------

    shapes - list of shapes to triangulate

    returns:
    -------

    list of tuples [(verts, faces, UVs)]
    """

    for shape in shapes:
        BRep_triangulate_to_BMesh_update(shape, bm)

    bm.to_mesh(mesh)
    mesh.update()
    create_object_in_scene(mesh, textureName, objectName)


def test_Triang_Faces():
    """
    blender test
    """
    shape = BRepPrimAPI_MakeBox(200, 200, 200).Shape()
    theBox = BRepPrimAPI_MakeBox(200, 60, 60).Shape()
    theSphere = BRepPrimAPI_MakeSphere(gp_Pnt(100, 20, 20), 80).Shape()
    shape = BRepAlgoAPI_Fuse(theSphere, theBox).Shape()

    BReps_triangulate_to_BMesh([shape])




# import os
# filename = "/media/50G/v/c/_obs/BlenderScripts/tests/bmesh_001.py"
# dn = os.path.dirname(os.path.abspath('__file__'))
# dn1 = os.path.dirname(os.path.abspath(filename))

if __name__ == "__main__":
    import os

    filename = "/media/home2/v/c/_obs/BlenderScripts/tests/bmesh_001.py"
    dn = os.path.dirname(os.path.abspath('__file__'))
    dn1 = os.path.dirname(os.path.abspath(filename))
    # dn=os.path.dirname(os.path.abspath(__bmesh_001__))
    print(dn)
    # dn2=dn
    print(dn1 + '/color.png')
    # print(os.getcwd())

    # test_Voronoi()

    # test_BRep_to_bmesh_box()
    test_Triang_Faces()

    # test_face_add()

    # init_view()
    # test_build_3()
