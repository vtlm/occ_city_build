# from shapely.speedups._speedups import Point
from operator import itemgetter
import os

from OCC.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_Surface
from OCC._BRepGProp import brepgprop_VolumeProperties
from OCC.GProp import GProp_GProps
from OCC.gp import gp_Trsf

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



def getMaxFromPairs(lst, ind):
    return max(lst, key=itemgetter(ind))[ind]


def getMinFromPairs(lst, ind):
    return min(lst, key=itemgetter(ind))[ind]


def checkUVs(uvs):
    minU = getMinFromPairs(uvs, 0)
    minV = getMinFromPairs(uvs, 1)
    newUVs = [(uv[0] - minU, uv[1] - minV) for uv in uvs]
    return newUVs


def getFaceSize(face):
    sa = BRepAdaptor_Surface(face)
    firstU = sa.FirstUParameter()
    firstV = sa.FirstVParameter()
    lastU = sa.LastUParameter()
    lastV = sa.LastVParameter()
    pt0 = sa.Value(firstU, firstV)
    ptMaxU = sa.Value(lastU, firstV)
    ptMaxV = sa.Value(firstU, lastV)
    width = pt0.Distance(ptMaxU)
    height = pt0.Distance(ptMaxV)
    return width, height


def reCalcUVs(face, uvs):
    textrW = 1
    textrH = 1
    faceWidth, faceHeight = getFaceSize(face)
    uvs = checkUVs(uvs)
    maxU = getMaxFromPairs(uvs, 0)
    maxV = getMaxFromPairs(uvs, 1)
    cU = faceWidth / textrW
    cV = faceHeight / textrH
    effU = maxU / cU
    effV = maxV / cV
    if effV == 0:
        print(faceWidth, faceHeight)
        print(uvs, maxU, maxV, cU, cV)
        print(maxU, maxV, cU, cV)
    maxU /= effU
    maxV /= effV
    uvs = [(x[0] / effU, x[1] / effV) for x in uvs]
    rndMaxU = round(maxU)
    if rndMaxU == 0:
        rndMaxU = 1
    rndMaxV = round(maxV)
    if rndMaxV == 0:
        rndMaxV = 1
    rndEffU = maxU / rndMaxU
    rndEffV = maxV / rndMaxV
    uvs = [(x[0] / rndEffU, x[1] / rndEffV) for x in uvs]
    return uvs


def BRep_Face_triangulate(face, loc, cm, reTestNormals=True, reCalculateUVs=False):
    """
    params:
    ------
    face: BRep face to triangulate
    comp, builder - n/u

    returns:
    (tr_verts, tr_triang_indices, tr_uvs)
    """
    tr_verts = []
    tr_triang_indices = []
    tr_uvs = []
    location = loc  # TopLoc_Location()
    c=cm  # loc.Transformation().TranslationPart()
    print('centr=',c.X(),c.Y(),c.Z())
    facing = (BRep_Tool_Triangulation(face, location)).GetObject()
    tab = facing.Nodes()
    uvs = facing.UVNodes()

    # print(tab.Upper(),uvs.Upper())
    # all_pts=[(t.X(),t.Y(),t.Z()) for t in tab]
    # print(tab.Lower(),tab.Upper())
    lowBnd = tab.Lower()
    for i in range(tab.Lower(), tab.Upper() + 1):
        pt = tab.Value(i)
        # tr_verts.append((pt.X(), pt.Y(), pt.Z()))
        tr_verts.append((pt.X(), pt.Z(), -pt.Y()))
        pt2d = uvs.Value(i)
        tr_uvs.append((pt2d.X(), pt2d.Y()))

    tri = facing.Triangles()
    for i in range(1, facing.NbTriangles() + 1):
        trian = tri.Value(i)
        index1, index2, index3 = trian.Get()
        # print(index1,index2,index3,lowBnd)
        # v1=gp_Vec2d(uvs.Value(index2 - lowBnd),uvs.Value(index1 - lowBnd))
        # v2=gp_Vec2d(uvs.Value(index3 - lowBnd),uvs.Value(index1 - lowBnd))
        # print("reTestNormals=",reTestNormals)
        if reTestNormals:
            p2 = tab.Value(index2)
            # print('p2=',p2)
            p1 = tab.Value(index1)
            # print('p1=',p1)
            v1 = gp_Vec(p2, p1)
            v2 = gp_Vec(tab.Value(index3), tab.Value(index1))
            # v3=v2.Reversed()
            # ang=v1.Angle(v2)
            # ang2=v2.Angle(v1)
            # print('ang=',ang,ang2)
            crs = v1.Crossed(v2)
            fc=gp_Vec(p1,c)
            if fc.Dot(crs) < 0:
            # print(crs.Z())
            # if crs.Z() >= 0:
                tr_triang_indices.append(
                    (index1 - lowBnd, index2 - lowBnd, index3 - lowBnd))
            else:
                tr_triang_indices.append(
                    (index1 - lowBnd, index3 - lowBnd, index2 - lowBnd))
        else:
            tr_triang_indices.append(
                (index1 - lowBnd, index2 - lowBnd, index3 - lowBnd))

        if reCalculateUVs:
            tr_uvs = reCalcUVs(face, tr_uvs)

    return tr_verts, tr_triang_indices, tr_uvs


def BRep_triangulate(shape, reTestNormals=True, reCalcUVs=False):
    """
    works for single shape
    splits shape to faces, and triangulte every face

    params:
    -------
    shape : to triangulte

    returns:
    --------
    list of triangulations for faces
    [(verts, triangs indexes, UVs)]
    """

    tris = []
    gprops=GProp_GProps()
    brepgprop_VolumeProperties(shape,gprops)
    trsf=gp_Trsf()
    # print("gprops.CentreOfMass()=",gprops.CentreOfMass().X())
    trsf.SetTranslation(gp_Vec(gprops.CentreOfMass(),gp_Pnt()))
    loc=TopLoc_Location(trsf)
    brepmesh_Mesh(shape, 0.8)

    ex = TopExp_Explorer(shape, TopAbs_FACE)
    while ex.More():
        face = topods_Face(ex.Current())
        # print(face.Orientation())
        # if face.Orientation() == 1:
        #     face=face.Reversed()
        #     print('try change ',face.Orientation())
        # tr_verts, tr_faces, tr_uvs = BRepFace_triangulate_to_BMesh(face, comp, builder, reTestNormals)
        tr_verts, tr_triang_indices, tr_uvs = BRep_Face_triangulate(
            face, loc, gprops.CentreOfMass(), reTestNormals, reCalcUVs)
        # print('tr_uvs',tr_uvs)
        # tr_uvs=[(x[0],x[1]*2) for x in tr_uvs]
        # print('new_tr_uvs',tr_uvs)
        # print('tr_uvs',tr_uvs)
        # tr_uvs = reCalcUVs(face, tr_uvs)
        # print('new_tr_uvs',tr_uvs)
        tris.append((tr_verts, tr_triang_indices, tr_uvs))
        ex.Next()

    return tris






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
