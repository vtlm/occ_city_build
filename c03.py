from OCC.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_Surface
from OCC.BRepFill import BRepFill_Filling, brepfill_Shell
from OCC.BRepOffsetAPI import BRepOffsetAPI_MakePipe
from OCC.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCC.GC import GC_MakeLine
from OCC.Geom import Handle_Geom_Line, Handle_Geom_TrimmedCurve
from OCC.GeomAPI import GeomAPI_IntCS

__author__ = 'nezx'


from OCC.gp import gp_Pnt,gp_Vec,gp_Trsf, gp_Vec2d, gp_Pnt2d
from OCC.BRepBuilderAPI import BRepBuilderAPI_MakePolygon,BRepBuilderAPI_Transform, BRepBuilderAPI_MakeWire, \
    BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakeEdge, BRepBuilderAPI_Copy, BRepBuilderAPI_GTransform
from OCC.BRepAlgoAPI import BRepAlgoAPI_Common,BRepAlgoAPI_Cut
from OCC.TopExp import TopExp_Explorer
from OCC.TopAbs import TopAbs_VERTEX, TopAbs_FACE
from OCC.TopoDS import topods_Vertex, topods_Edge, topods_Wire, topods_Face, TopoDS_Shape
from OCC.BRep import BRep_Tool_Pnt
from OCC import gp as _gp
from OCC.GProp import GProp_GProps
from OCC.BRepGProp import brepgprop_SurfaceProperties
from OCC._GeomAbs import GeomAbs_C0, GeomAbs_G1, GeomAbs_C1
from shapely.geometry import Polygon
from shapely.affinity import scale
import shapely


def scaleRise(ds,scaleF=(1,1),h=0):
    p0 = Polygon(ds)
    p=scale(p0, xfact=scaleF[0], yfact=scaleF[1])
    pl = []
    pl.extend(p.boundary.coords)
    pl=[(p[0],p[1],p[2]+h) for p in pl]
    return pl


def scale(ds,scaleF=(1,1)):
    p0 = Polygon(ds)
    p=shapely.affinity.scale(p0, xfact=scaleF[0], yfact=scaleF[1])
    pl = []
    pl.extend(p.boundary.coords)
    return pl


def rise(ds,h=0):
    pl=[(p[0],p[1],p[2]+h) for p in ds]
    return pl


def toEdges(ptsi):
    if type(ptsi[0]) in [BRepBuilderAPI_MakeEdge, BRepBuilderAPI_Transform]:
        return ptsi
    elif type(ptsi[0]) in [Handle_Geom_Line, Handle_Geom_TrimmedCurve, TopoDS_Shape]:
        es=[BRepBuilderAPI_MakeEdge(c) for c in ptsi]
    else:
        es=[]
        if isinstance(ptsi[0], tuple):
            ptsa=[gp_Pnt(pt[0],pt[1],pt[2]) for pt in ptsi]
        elif isinstance(ptsi[0], gp_Vec):
            ptsa=[gp_Pnt(pt.XYZ()) for pt in ptsi]
        else:
            ptsa=ptsi

        # print('ptsa=',ptsa)
        for i in range(len(ptsa)-1):
            es.append(BRepBuilderAPI_MakeEdge(ptsa[i],ptsa[i+1]))
    return es


def toShapes(ptsi):
    if type(ptsi[0]) in [TopoDS_Shape]:
        return ptsi
    else:
        esas=toEdges(ptsi)
        es=[esa.Shape() for esa in esas]
    return es


def makeWire(ptsi):
    # ptsa=None
    if type(ptsi[0]) in [TopoDS_Shape]:
        w=BRepBuilderAPI_MakeWire()
        for c in ptsi:
            w.Add(topods_Edge(c))
        return w
    elif type(ptsi[0]) in [BRepBuilderAPI_MakeEdge, BRepBuilderAPI_Transform]:
        w=BRepBuilderAPI_MakeWire()
        for c in ptsi:
            w.Add(topods_Edge(c.Shape()))
        return w
    elif type(ptsi[0]) in [Handle_Geom_Line, Handle_Geom_TrimmedCurve]:
        w=BRepBuilderAPI_MakeWire()
        for c in ptsi:
            e=BRepBuilderAPI_MakeEdge(c)
            w.Add(topods_Edge(e.Shape()))
        return w
    else:
        if isinstance(ptsi[0], tuple):
            ptsa=[gp_Pnt(pt[0],pt[1],pt[2]) for pt in ptsi]
        elif isinstance(ptsi[0], gp_Vec):
            ptsa=[gp_Pnt(pt.XYZ()) for pt in ptsi]
        else:
            ptsa=ptsi
        w=BRepBuilderAPI_MakeWire()
        for i in range(len(ptsa)-1):
            e=BRepBuilderAPI_MakeEdge(ptsa[i],ptsa[i+1])
            w.Add(topods_Edge(e.Shape()))
        return w


def makeFace(ptsi):
    w=makeWire(ptsi)
    f=BRepBuilderAPI_MakeFace(topods_Wire(w.Shape()))
    return f


def makeRectAsFace(w,h,offs=gp_Vec(0,0,0)):
    pnts=[gp_Pnt(0,0,0),gp_Pnt(w,0,0),gp_Pnt(w,h,0),gp_Pnt(0,h,0),gp_Pnt(0,0,0)]
    ptsa=[p.Translated(offs) for p in pnts]
    #dbg
    # cs=[(p.X(),p.Y()) for p in ptsa]
    # print(cs)
    return makeFace(ptsa)


def makeRectAsWire(w,h,offs=gp_Vec(0,0,0)):
    pnts=[gp_Pnt(0,0,0),gp_Pnt(w,0,0),gp_Pnt(w,h,0),gp_Pnt(0,h,0),gp_Pnt(0,0,0)]
    ptsa=[p.Translated(offs) for p in pnts]
    cs=[(p.X(),p.Y()) for p in ptsa]
    print(cs)
    p=BRepBuilderAPI_MakePolygon()
    for pt in ptsa:
        p.Add(pt)
    return p


def makeShell(outline1,outline2):
    w0=makeWire(outline1)
    w1=makeWire(outline2)
    sh = brepfill_Shell(topods_Wire(w1.Shape()), topods_Wire(w0.Shape()))
    return sh


def makeFilling(ipas, dbgOutput=False):

    if dbgOutput:
        print('len=',len(ipas))
    # print(list(ipas))
        for p in ipas:
            print(p)

    pas=toShapes(ipas)
    w=BRepFill_Filling()
    w.SetResolParam(3,15,2,True)
    w.SetConstrParam(0.1,0.1,0.1,0.1)

    for e in pas:
        # e=BRepBuilderAPI_MakeEdge(sg.Value())
        w.Add(topods_Edge(e), GeomAbs_C0)

    w.Build()
    return w

    # pas=toEdges(ipas)
    # w=BRepFill_Filling()
    #
    # for e in pas:
    #     # e=BRepBuilderAPI_MakeEdge(sg.Value())
    #     w.Add(topods_Edge(e.Shape()), GeomAbs_C0)
    #
    # w.Build()
    # return w

    # f=w.Face()
    # # if f.IsDone():
    # display.DisplayShape(f)


def getConstructedSurfaceGProps(shapes):
    bf=makeFilling(shapes)
    gp = GProp_GProps()
    brepgprop_SurfaceProperties(bf.Face(), gp)
    return gp



def scaleCrvs(initCrvs, scale):
    # outerOutline= c03.makeWire(initOutlineL)

    # TODO change to prev func
    #calc center of mass
    bf = makeFilling(initCrvs)
    gp = GProp_GProps()
    brepgprop_SurfaceProperties(bf.Face(), gp)

    cm = gp.CentreOfMass()
    #dbg
    # print(cm.X(),cm.Y(),cm.Z())
    # layout.dbgDrawUpStake(gp_Vec(cm.XYZ()),150)

    #prep transform
    tSc = _gp.gp_Trsf()
    tSc.SetScale(cm, scale)
    # tt=BRepBuilderAPI_Transform(t.Multiplied(tSc))
    tt = BRepBuilderAPI_Transform(tSc)

    #perform transform
    # outCrvs=[tt.ModifiedShape(TopoDS_Shape(topods_Edge(crv.GetObject()))) for crv in initCrvs]
    outCrvs = []
    for c in initCrvs:
        tt.Perform(c.Shape())
        outCrvs.append(tt.Shape())
    return outCrvs


def translCrvs(initCrvs, transV):#input as Shapes
    # outerOutline= c03.makeWire(initOutlineL)

    # #calc center of mass
    # bf = makeFilling(initCrvs)
    # gp = GProp_GProps()
    # brepgprop_SurfaceProperties(bf.Face(), gp)
    # cm = gp.CentreOfMass()
    # #dbg
    # # print(cm.X(),cm.Y(),cm.Z())
    # # layout.dbgDrawUpStake(gp_Vec(cm.XYZ()),150)

    #prep transform
    tSc = _gp.gp_Trsf()
    tSc.SetTranslation(transV)
    # tt=BRepBuilderAPI_Transform(t.Multiplied(tSc))
    tt = BRepBuilderAPI_Transform(tSc)

    #perform transform
    # outCrvs=[tt.ModifiedShape(TopoDS_Shape(topods_Edge(crv.GetObject()))) for crv in initCrvs]
    outCrvs = []
    for c in initCrvs:
        tt.Perform(c.Shape())
        outCrvs.append(tt.Shape())
    return outCrvs


def scaleShapes(initCrvs, scale):
    # outerOutline= c03.makeWire(initOutlineL)

    #calc center of mass
    bf = makeFilling(initCrvs)
    gp = GProp_GProps()
    brepgprop_SurfaceProperties(bf.Face(), gp)
    cm = gp.CentreOfMass()
    #dbg
    # print(cm.X(),cm.Y(),cm.Z())
    # layout.dbgDrawUpStake(gp_Vec(cm.XYZ()),150)

    #prep transform
    tSc = _gp.gp_Trsf()
    tSc.SetScale(cm, scale)
    # tt=BRepBuilderAPI_Transform(t.Multiplied(tSc))
    tt = BRepBuilderAPI_Transform(tSc)

    #perform transform
    # outCrvs=[tt.ModifiedShape(TopoDS_Shape(topods_Edge(crv.GetObject()))) for crv in initCrvs]
    outCrvs = []
    for c in Copy(initCrvs):
        tt.Perform(c)
        outCrvs.append(tt.Shape())
    return outCrvs


def scaleShapes(initCrvs, scale, trsfCenter=None):

    if not trsfCenter:
        #calc center of mass
        bf = makeFilling(initCrvs)
        gp = GProp_GProps()
        brepgprop_SurfaceProperties(bf.Face(), gp)
        trsfCenter = gp.CentreOfMass()

    #prep transform
    tSc = _gp.gp_Trsf()
    tSc.SetScale(trsfCenter, scale)
    # tt=BRepBuilderAPI_Transform(t.Multiplied(tSc))
    tt = BRepBuilderAPI_Transform(tSc)

    #perform transform
    # outCrvs=[tt.ModifiedShape(TopoDS_Shape(topods_Edge(crv.GetObject()))) for crv in initCrvs]
    outCrvs = []
    for c in Copy(initCrvs):
        tt.Perform(c)
        outCrvs.append(tt.Shape())
    return outCrvs


def translShapes(initCrvs, transV):#input as Shapes
    # outerOutline= c03.makeWire(initOutlineL)

    # #calc center of mass
    # bf = makeFilling(initCrvs)
    # gp = GProp_GProps()
    # brepgprop_SurfaceProperties(bf.Face(), gp)
    # cm = gp.CentreOfMass()
    # #dbg
    # # print(cm.X(),cm.Y(),cm.Z())
    # # layout.dbgDrawUpStake(gp_Vec(cm.XYZ()),150)

    #prep transform
    tSc = _gp.gp_Trsf()
    tSc.SetTranslation(transV)
    tG=_gp.gp_GTrsf()
    tG.SetTrsf(tSc)
    # tt=BRepBuilderAPI_Transform(t.Multiplied(tSc))
    tt = BRepBuilderAPI_GTransform(tG)

    #perform transform
    # outCrvs=[tt.ModifiedShape(TopoDS_Shape(topods_Edge(crv.GetObject()))) for crv in initCrvs]
    outCrvs = []
    for c in Copy(initCrvs):
        tt.Perform(c)
        outCrvs.append(tt.Shape())
    return outCrvs

from operator import itemgetter


def getBounds(shapes):
    pts=[]
    for s in shapes:
        ca=BRepAdaptor_Curve(topods_Edge(s))
        pts.append(ca.Value(ca.FirstParameter()))
        pts.append(ca.Value(ca.LastParameter()))
    ptsC=[(p.X(),p.Y(),p.Z()) for p in pts]
    top=max(ptsC,key=itemgetter(2))
    low=min(ptsC,key=itemgetter(2))

    return low,top


def projectPointsOnSurface(pts,prjDir,brSurface):
    bas=BRepAdaptor_Surface(topods_Face(brSurface))
    gaS=bas.Surface()
    hGeomSurf=gaS.Surface()#.GetObject()
    # print(hGeomSurf)
    intCS=GeomAPI_IntCS()
    outPts=[]
    for pt in pts:
        hLine=GC_MakeLine(pt,prjDir)
        intCS.Perform(hLine.Value(),hGeomSurf)
        if intCS.IsDone() and intCS.NbPoints()>0:
            ptI=intCS.Point(1)
            outPts.append(ptI)

    return outPts


def BRepFace_to_GeomAdaptor(brSurface):
    bas=BRepAdaptor_Surface(topods_Face(brSurface))
    gaS=bas.Surface()
    hGeomSurf=gaS.Surface()#.GetObject()
    return hGeomSurf


def findProjectionPointOnSurfaces(pt,prjDir,geomAdaptsSurfaces):
    """
    ret:
    gp_Pnt
    """
    intCS=GeomAPI_IntCS()
    hLine=GC_MakeLine(pt,prjDir)
    for hGeomSurf in geomAdaptsSurfaces:
        intCS.Perform(hLine.Value(),hGeomSurf)
        if intCS.IsDone() and intCS.NbPoints()>0:
            ptI=intCS.Point(1)
            return ptI

    return None


def projectPointsOnSurfaces(pts,prjDir,surfaceAdaptors):
    """
    ret:
    [gp_Pnt]
    """
    retPts=[]
    for pt in pts:
        prjdPt=findProjectionPointOnSurfaces(pt,prjDir,surfaceAdaptors)
        if prjdPt:
            retPts.append(prjdPt)
    return retPts


def getAllFaces(shell):
    fs=[]
    expl=TopExp_Explorer(shell,TopAbs_FACE)
    while expl.More():
        fs.append(topods_Face(expl.Current()))
        expl.Next()
    return fs

def Copy(shapes):
    copies=[]
    c=BRepBuilderAPI_Copy()
    for s in shapes:
        c.Perform(s)
        copies.append(c.Shape())
    return copies


# ------------------------------------------------------------------

def tst_01():
    p1=makeRectAsFace(20,10,gp_Vec(5,5,0))
    p2=makeRectAsFace(20,10,gp_Vec(0,0,0))
    # p=BRepAlgoAPI_Common(p1.Shape(),p2.Shape())
    p=BRepAlgoAPI_Cut(p1.Shape(),p2.Shape())

    display.DisplayShape(p1.Shape())
    display.DisplayShape(p2.Shape())
    display.DisplayShape(p.Shape())

    vs=TopExp_Explorer(p.Shape(),TopAbs_VERTEX)
    while vs.More():
        pnt=BRep_Tool_Pnt(topods_Vertex(vs.Current()))
        print(vs.Current(),pnt.X(),pnt.Y())
        vs.Next()

    t=_gp.gp_Trsf()
    tv=_gp.gp_Vec(0,0,2)
    t.SetTranslation(tv)

    tt=BRepBuilderAPI_Transform(t)
    tt.Perform(p.Shape())

    tps=tt.Shape()
    display.DisplayShape(tps)

    gp=GProp_GProps()
    brepgprop_SurfaceProperties(tps,gp)
    cm=gp.CentreOfMass()
    print(cm.X(),cm.Y(),cm.Z())

    tSc=_gp.gp_Trsf()
    tSc.SetScale(cm,0.85)
    tt=BRepBuilderAPI_Transform(t.Multiplied(tSc))
    tt.Perform(tps)
    tps1=tt.Shape()
    display.DisplayShape(tps1)


def tst_02():
    from OCC.BRep import BRep_Builder, BRep_Tool_Triangulation
    from OCC.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeSphere
    from OCC.BRepAlgoAPI import BRepAlgoAPI_Fuse
    from OCC.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
    from OCC.BRepMesh import brepmesh_Mesh
    from OCC.TopExp import TopExp_Explorer
    from OCC.TopoDS import TopoDS_Compound, topods_Face, topods_Edge
    from OCC.TopAbs import TopAbs_FACE
    from OCC.TopLoc import TopLoc_Location
    from OCC.gp import gp_Pnt
    import json

    p2=makeRectAsFace(20,10,gp_Vec(0,0,0))
    display.DisplayShape(p2.Shape())

    shape=p2.Shape()
    brepmesh_Mesh(shape, 0.8)

    builder = BRep_Builder()
    comp = TopoDS_Compound()
    builder.MakeCompound(comp)

    ex = TopExp_Explorer(shape, TopAbs_FACE)
    while ex.More():
        face = topods_Face(ex.Current())
        location = TopLoc_Location()
        facing = (BRep_Tool_Triangulation(face, location)).GetObject()
        tab = facing.Nodes()
        tri = facing.Triangles()
        for i in range(1, facing.NbTriangles()+1):
            trian = tri.Value(i)
            index1, index2, index3 = trian.Get()
            for j in range(1, 4):
                if j == 1:
                    m = index1
                    n = index2
                elif j == 2:
                    n = index3
                elif j == 3:
                    m = index2
                me = BRepBuilderAPI_MakeEdge(tab.Value(m), tab.Value(n))
                if me.IsDone():
                    builder.Add(comp, me.Edge())
        # json.dump(facing,open('faces.json', 'w'))

        ex.Next()

    display.EraseAll()
    # display.DisplayShape(shape)
    display.DisplayShape(comp, update=True)


from OCC.BRep import BRep_Builder, BRep_Tool_Triangulation
from OCC.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeSphere
from OCC.BRepAlgoAPI import BRepAlgoAPI_Fuse
from OCC.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCC.BRepMesh import brepmesh_Mesh
from OCC.TopExp import TopExp_Explorer
from OCC.TopoDS import TopoDS_Compound, topods_Face, topods_Edge
from OCC.TopAbs import TopAbs_FACE
from OCC.TopLoc import TopLoc_Location
from OCC.gp import gp_Pnt


def BRep_Face_triangulate(face, reTestNormals=True):
    """
    blender
    params:
    ------
    face: BRep face to triangulate
    comp, builder - n/u

    returns:
    (for bmesh) bm_verts, bm_faces, bm_uvs
    """
    bm_verts = []
    bm_faces = []
    bm_uvs = []
    location = TopLoc_Location()
    facing = (BRep_Tool_Triangulation(face, location)).GetObject()
    tab = facing.Nodes()
    uvs = facing.UVNodes()

    # print(tab.Upper(),uvs.Upper())
    # all_pts=[(t.X(),t.Y(),t.Z()) for t in tab]
    # print(tab.Lower(),tab.Upper())
    lowBnd = tab.Lower()
    for i in range(tab.Lower(), tab.Upper() + 1):
        pt = tab.Value(i)
        bm_verts.append((pt.X(), pt.Y(), pt.Z()))
        pt2d = uvs.Value(i)
        bm_uvs.append((pt2d.X(), pt2d.Y()))
    tri = facing.Triangles()
    for i in range(1, facing.NbTriangles() + 1):
        trian = tri.Value(i)
        index1, index2, index3 = trian.Get()
        # print(index1,index2,index3,lowBnd)
        # v1=gp_Vec2d(uvs.Value(index2 - lowBnd),uvs.Value(index1 - lowBnd))
        # v2=gp_Vec2d(uvs.Value(index3 - lowBnd),uvs.Value(index1 - lowBnd))
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
            # print(crs.Z())
            if crs.Z() >= 0:
                bm_faces.append(
                    (index1 - lowBnd, index2 - lowBnd, index3 - lowBnd))
            else:
                bm_faces.append(
                    (index1 - lowBnd, index3 - lowBnd, index2 - lowBnd))
        else:
            bm_faces.append(
                (index1 - lowBnd, index2 - lowBnd, index3 - lowBnd))

    return bm_verts, bm_faces, bm_uvs


def tst_03():
    from OCC.BRep import BRep_Builder, BRep_Tool_Triangulation
    from OCC.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeSphere
    from OCC.BRepAlgoAPI import BRepAlgoAPI_Fuse
    from OCC.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
    from OCC.BRepMesh import brepmesh_Mesh
    from OCC.TopExp import TopExp_Explorer
    from OCC.TopoDS import TopoDS_Compound, topods_Face, topods_Edge
    from OCC.TopAbs import TopAbs_FACE
    from OCC.TopLoc import TopLoc_Location
    from OCC.gp import gp_Pnt
    import json
    import os

    print(os.getcwd())
    full_path = os.path.realpath(__file__)
    # import sys
    # sys.path.append("/media/50G/v/c/_obs/BlenderScripts/tests")
    # from bmesh_001 import BRepFace_triangulate_to_BMesh

    p2=makeRectAsFace(20,10,gp_Vec(0,0,0))
    display.DisplayShape(p2.Shape())

    shape=p2.Shape()
    brepmesh_Mesh(shape, 0.8)

    builder = BRep_Builder()
    comp = TopoDS_Compound()
    builder.MakeCompound(comp)

    ex = TopExp_Explorer(shape, TopAbs_FACE)

    tris=[]

    while ex.More():
        face = topods_Face(ex.Current())
        rss=BRep_Face_triangulate(face)
        tris.append(rss)
        ex.Next()

    json.dump(tris,open('faces.json', 'w'))



if __name__ == "__main__":

    from OCC.Display.SimpleGui import init_display
    display, start_display, add_menu, add_function_to_menu = init_display()

    tst_03()


    start_display()
