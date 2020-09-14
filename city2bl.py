# todo
'''
    check outer grass inner bound
    extern sidewalk
    blocks scale check height
'''
"""
import sys
sys.path.append('/media/50G/v/c/_obs/BlenderScripts/tests/')
from importlib import reload
import bmesh_001
filename = "/media/50G/v/c/City_Py_OCC/city2bl.py"
exec(compile(open(filename).read(), filename, 'exec'))
"""
import os
import pickle
import sys
from OCC.BRepLib import BRepLib_MakeFace
from OCC.BRepPrimAPI import BRepPrimAPI_MakePrism

filename = "/media/50G/v/c/City_Py_OCC/city2bl.py"
dn = os.path.dirname(os.path.abspath('__file__'))
dn1 = os.path.dirname(os.path.abspath(filename))
# dn=os.path.dirname(os.path.abspath(__bmesh_001__))
# print(dn)
# dn2=dn
# print(dn1 + '/color.png')
sys.path.append(dn1)
# sys.path.append("/media/50G/v/c/_obs/BlenderScripts/tests")

import display
from BRep_funx import BRep_triangulate
from OCC.gp import gp_Pnt, gp_Vec, gp_Dir
# from navMeshNodeSection import NavMeshNodeSection, linkList

from block import CityBlock
# from house import House, CompoundHouse

from OCC.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_Transform
from OCC.GProp import GProp_GProps
from OCC import gp as _gp
from OCC.TopoDS import topods_Edge, topods_Wire, topods_Face, TopoDS_Shape
from OCC.BRepGProp import brepgprop_SurfaceProperties
from OCC.BRepFill import brepfill_Shell, brepfill_Face
from shapely.geometry import Polygon
from meshTriang import triangulate

import json
# import numpy as np
import random
# from shapely.geometry import Polygon, LinearRing
import layout
import c03
from subdiv import subDiv, getBoundary
from display import Display, DisplayColored, QuantColor

if display.OCC_FrontEnd:
    from display import start_display


# import bpy
from layout import Joint, calcEdgeDir, eJSStart
import networkx as nx
from operator import itemgetter
from functools import reduce
# from FreeCAD import Vector
# import Part
from shapely.affinity import scale

from funx import appendEntry

pts = []
lines = []
rs = []
# grassyPtches=
dmp = {}
cdmp = []
geoms = {}
geoms['innerPatches'] = []
geoms['lArea'] = []
geoms['houses'] = []
blocks = []
# from OCC.Display.SimpleGui import init_display
# display, start_display, add_menu, add_function_to_menu = init_display()
layout.display = display
c03.display = display

dg = None


def nx_create_grid_2d_graph_spectral(r=4, rangeHoriz=100):
    """
    """
    # create graph
    pg = nx.grid_2d_graph(r, r)
    dg = nx.DiGraph(pg)
    # pos=nx.spring_layout(g,iterations=200)
    nPos = nx.spectral_layout(pg)
    # pos = {k: (v[0]*rangeHoriz, v[1]*rangeHoriz) for k, v in nPos.items()}
    pos = {k: v * rangeHoriz for k, v in nPos.items()}

    return dg, pos


# def create_city(rangeHoriz = 100, rangeVert = 10):
def create_city(gr, pos, rangeVert=10):
    # removeAll()
    global dg
    dg = gr
    # dg, pos = nx_create_grid_2d_graph_spectral()
    # set consts
    for p in pos.items():
        # print type(p[0])
        # dg.node[p[0]]['joint']=Joint(p[1]*100,dg)
        # dg.node[p[0]]['joint'] = Joint((p[1][0]*rangeHoriz, p[1][1]*rangeHoriz, random.random() * rangeVert), dg)
        dg.node[p[0]]['joint'] = Joint(
            (p[1][0], p[1][1], random.random() * rangeVert), dg)
    # print(pos)
    # print g.nodes(data=True)
    # for n in g.nodes():
    #     # print g.node[n]
    #     j=g.node[n]['joint']
    #     # print j.loc

    # dg=nx.DiGraph(g)

    # TODO: angles, dir maybe unneeded
    inEs = dg.in_edges()
    outEs = dg.out_edges()
    inEAs = [(x, calcEdgeDir(x, dg)) for x in inEs]
    outEAs = [(x, calcEdgeDir(x, dg)) for x in outEs]
    # print ('inEAs',inEAs)

    # set opposite edges
    # TODO simplify without angles
    for inEA in inEAs:
        # print type(inEA[1]), inEA[1], inEA[1].__neg__()
        # print inEA[1], outEAs[0][1].__neg__(),inEA[1].__eq__(outEAs[0][1].__neg__())
        # res=inEA[1].__eq__(outEAs[0][1].__neg__())
        # print res
        # print True in res
        # print inEA[1].__ne__(outEAs[0][1].__neg__())
        # cEA=next((x for x in outEAs if not False in inEA[1].__eq__(x[1].__neg__())),None)
        # cEA=next((x for x in outEAs if inEA[1].dot(x[1]) < -0.9),None)
        cEA = next((x for x in outEAs if inEA[0][0] == x[
                   0][1] and inEA[0][1] == x[0][0]), None)
        # print ('cEA=', cEA, inEA, cEA[1].dot(inEA[1]))
        dg[cEA[0][0]][cEA[0][1]]['oppEdge'] = inEA[0]
        # dg[cEA[0][0]][cEA[0][1]]['oppEdge']=inEA[0]
        # dg[cEA[0]]['oppEdge']=inEA[0]//don't works
        # dg[inEA[0]]['oppEdge']=cEA[0]
        # dbg
        # pt1=dg.node[cEA[0][0]]['joint'].loc
        # pt2=dg.node[inEA[0][0]]['joint'].loc
        # print('pts',pt1,pt2)

        # dbg
        # pts.append(Vector((pt1[0],pt1[1],0)))
        # lines.append([Vector((pt1[0],pt1[1],0)),Vector((pt2[0],pt2[1],0))])

    # create JointSides on graph nodes
    for n in dg.nodes():
        # print dg.out_edges(n)
        # print dg.in_edges(n)
        # print dg.node[n]
        j = dg.node[n]['joint']
        # print id(j),j.loc
        inEs = dg.in_edges(n)
        # print 'inEs=',inEs
        for inE in inEs:
            j.addSide(inE, dg[inE[0]][inE[1]]['oppEdge'])
            # print id(j.sides),j.sides

            # j.addSide(inEA[0],cEA[0])

    # link opp JointSides (for roads)
    for e in dg.edges():
        oppE = dg[e[0]][e[1]]['oppEdge']
        js1 = eJSStart[e]
        js2 = eJSStart[oppE]
        js1.setOpposite(js2)
        js2.setOpposite(js1)

    # nodes joints (crossroads) geometry, sides sort
    for n in dg.nodes():
        # print(len(dg.node[n]['joint'].sides))
        ss = dg.node[n]['joint'].sides
        # print(ss)

        def getKey(js):
            return js.aR

        sss = sorted(ss, key=getKey)
        dg.node[n]['joint'].sides = sss
        dg.node[n]['joint'].linkSides()

        dg.node[n]['joint'].makeToNextSideCurves()
        # dg.node[n]['joint'].discretizeCurves()
        # dg.node[n]['joint'].makePatchFromCurvesAsBRepFilling()

    # roads

    # for n in dg.nodes():
    #     j = dg.node[n]['joint']
    #     # j.calcSplineStartPts()

    for n in dg.nodes():
        j = dg.node[n]['joint']
        j.makeSplines()
        j.discretizeCurves()
        j.makePatchFromDiscretizedPointsAsBRepFilling()

    used_sides = []

    def makeRoadFromTwoSplinesAsBRepFace(edge):
        startJointSide = eJSStart[edge]
        if startJointSide in used_sides:
            return
        endJointSide = layout.eJSEnd[edge]
        used_sides.append(endJointSide)

        spl1 = startJointSide.rSpline
        spl2 = endJointSide.rSpline
        e1 = BRepBuilderAPI_MakeEdge(spl1.Curve())
        spl2.Curve().GetObject().Reverse()
        e2 = BRepBuilderAPI_MakeEdge(spl2.Curve())
        roadFilledAsFace = brepfill_Face(
            topods_Edge(e1.Shape()), topods_Edge(e2.Shape()))
        startJointSide.roadFilledAsFace = roadFilledAsFace
        # DisplayColored(fr,color=QuantColor(0.1,0.1,0.1))
        # ts=triangulate(fr)
        # Display(ts)

    for e in dg.edges():
        makeRoadFromTwoSplinesAsBRepFace(e)

    # inner patches

    # get all joints sides grouped by joints
    jsss = [dg.node[n]['joint'].sides for n in dg.nodes()]

    # flat joints side in single list
    # js=sum(jss)
    jss = reduce(list.__add__, jsss)

    # curves version
    roadsLoopsOutlinesCurves = []
    roadsLoopsOutlinesPts = []
    looked_sides = []

    for js in jss:
        if js not in looked_sides:

            loopPts = []
            loopCurves = []
            cs = js

            while True:
                looked_sides.append(cs)

                p1 = cs.next.rpos
                p2 = cs.next.opposite.lpos
                loopPts.extend([p1, p2])

                # straight line version
                # l=GC_MakeSegment(gp_Pnt(p1.XYZ()),gp_Pnt(p2.XYZ()))
                # loopCurves.append(l.Value())

                # BSpline version
                loopCurves.append(cs.curveToNext.Value())
                spl = cs.next.rSpline
                loopCurves.append(spl.Curve())

                cs = cs.next.opposite

                if cs == js:
                    break

            roadsLoopsOutlinesCurves.append(loopCurves)
            roadsLoopsOutlinesPts.append(loopPts)
            # print(loopCurves)
            # for p in loopCurves:
            #     print(id(p))

    # (BRep) curves to edges
    roadsLoopsOutlinesEdges = [c03.toEdges(
        es) for es in roadsLoopsOutlinesCurves]

    # search max
    lens = [len(ip) for ip in roadsLoopsOutlinesEdges]
    i, v = max(enumerate(lens), key=itemgetter(1))
    # print(i,v)
    # outerOutlineL=c03.makeWire(roadsLoopsOutlinesEdges[i])
    # roadsLoopsOutlinesEdges.remove(roadsLoopsOutlinesEdges[i])
    # roadsLoopsOutlinesPts.remove(roadsLoopsOutlinesPts[i])
    roadsLoopsOutlines = zip(roadsLoopsOutlinesEdges, roadsLoopsOutlinesPts)
    # l=roadsLoopsOutlines.pop(i)
    maxL=i

    # roadsOutlinesW=[c03.makeWire(ro) for ro in roadsLoopsOutlinesEdges]

    # blocks.append(RoadBorder(outerOutlineL, 1))
    # oo = blocks[-1].getSidewalkInnerOutline()

    # build outer grassy
    # scOuter = c03.scaleCrvs(outerOutlineL, 1.4)
    # scOuter = c03.scaleShapes(oo, 1.4)
    # w1=c03.makeWire(scOuter)
    # w2=c03.makeWire(outerOutlineL)
    # sh = brepfill_Shell(topods_Wire(w1.Shape()), topods_Wire(w2.Shape()))
    # # sh = brepfill_Shell(topods_Wire(scOuter.Shape()), topods_Wire(outerOutlineL.Shape()))
    # DisplayColored(sh, color='GREEN')
    # geoms['grassy'] = [sh]
    geoms['grassy'] = []    # stub

    # scaledInner=[scaleWire(inO,0.8) for inO in roadsLoopsOutlinesEdges]
    # w=BRepBuilderAPI_MakeWire()
    # for c in outerOutline:
    #     e=BRepBuilderAPI_MakeEdge(c)
    #     w.Add(topods_Edge(e.Shape()))

    # innerGrassy=[c03.makeFilling(p).Face() for p in roadsLoopsOutlinesEdges]
    # geoms['grassy'].extend(innerGrassy)

    # innerGrassy=[makeShiftedArea(p,0.8) for p in roadsLoopsOutlinesEdges]
    # geoms['grassy'].extend(innerGrassy)

    # for p in roadsLoopsOutlinesEdges:
    # dbg_display_as_edges(p)
    # makeShiftedArea(p,0.8)
    # create_patch(p,extrudeH=0.0,pColor='GREEN')

    for i,rlo in enumerate(roadsLoopsOutlines):
        if i == maxL:
            offsDir=1
        else:
            offsDir=-1
        cb = CityBlock(*rlo,offsDir)
        cb.create()
        cb.display()
        cdmp.append(cb.export())
        # appendEntry(cdmp,'data','CityBlock',cb.export())
        # t,l=c03.getBounds(outl)
        # extrs.append((t,l))
        # layout.dbgDrawUpStake(layout.tuple_to_gp_Vec(t),20)
        # layout.dbgDrawUpStake(layout.tuple_to_gp_Vec(l),20,color='GREEN')


def dbg_display_as_edges(tcs):
    for trimCurv in tcs:
        # print(trimCurv.GetObject().StartPoint().X())
        e = BRepBuilderAPI_MakeEdge(trimCurv)
        Display(e.Shape())


def create_patch(p_i, extrudeH=0, pColor='RED'):
    p = p_i
    # for pi in p_i:
    # pi.remove(pi[-1])
    # p=reduce(list.__add__,p_i)
    # p.append(p[0])
    # # print(len(p),p[0],p[-1])
    # # p.append(p_i[0])

    # f= c03.makeFace(p)#for planar

    f = c03.makeFilling(p)
    print(f.IsDone())
    z = triangulate(f.Face())
    Display(z)

    # if extrudeH != 0:
    #     p=BRepPrimAPI_MakePrism(topods_Face(f.Shape()),gp_Vec(0,0,extrudeH))
    #     display.DisplayColoredShape(p.Shape(),color=pColor,update=True)
    # else:
    #     display.DisplayColoredShape(f.Face(),color=pColor,update=True)
    #


def linkJointsSides():
    for n in dg.nodes():
        j = dg.node[n]['joint']
        j.linkHalfRoadsSections()
        # j.linkHalfRoadsLanes()
        j.calcLaneSplinesPts()


def getAllLinks():
    '''
    get all roads traces of city
    param
    return:
    [LinkedRoadLanes{indInThisArray:discrSpline}]
    '''
    ls = []
    # getting all roadlanes in flat array
    for n in dg.nodes():
        j = dg.node[n]['joint']
        t = j.getAllLanes()
        ls.extend(j.getAllLanes())

    # set array pos index for every roadlane
    for i, l in enumerate(ls):
        l.ind = i

    # simplify for json export
    lss = [l.simplify() for l in ls]
    json.dump(lss, open('nmss.json', 'w'))
    # dbg
    # dc=lss[1:12]
    #json.dump(dc,open('db.json', 'w'))

    #cc=json.load(open('nmss.json', 'r'))

    # prev version
    # for l in ls:
    #     l.center = None
    #     l.tlHalfRoadSection = None
    #
    # pickle.dump(ls, open('nmss.bin', 'wb'))


# depr
def buildDiscretizedNavMeshForRoads(dg):
    def calcCenterPts(startJointSide, endJointSide):
        ptsR = startJointSide.discrRSpline
        ptsL = endJointSide.discrRSpline.copy()
        ptsL.reverse()
        # print(ptsR)
        # print(ptsL)
        # print('')
        dirs = []
        for z in range(0, len(ptsR)):
            pt1 = layout.tuple_to_gp_Pnt(ptsR[z])
            pt2 = layout.tuple_to_gp_Pnt(ptsL[z])
            # e=BRepBuilderAPI_MakeEdge(pt1,pt2)
            # DisplayColored(e.Shape())
            dirs.append(gp_Vec(pt1, pt2))
        dirsDiv = [d.Divided(2) for d in dirs]
        vecsR = [layout.tuple_to_gp_Vec(p) for p in ptsR]
        dps = zip(dirsDiv, vecsR)
        ptsC = [dp[1].Added(dp[0]) for dp in dps]
        ptsCT = [layout.gp_Vec_to_tuple(p) for p in ptsC]
        ptsCTR = ptsCT.copy()
        ptsCTR.reverse()
        startJointSide.centerPts = ptsCT
        endJointSide.centerPts = ptsCTR

    def createNavMeshForEdge(edge, color=None):
        startJointSide = eJSStart[edge]
        endJointSide = layout.eJSEnd[edge]
        ptsR = startJointSide.discrRSpline
        ptsL = startJointSide.centerPts
        navMeshSs = []
        for z in range(0, len(ptsR)):
            navMeshSs.append(NavMeshNodeSection(ptsR, ptsL))
            # dbg
            # pt1= layout.tuple_to_gp_Pnt(ptsR[z])
            # pt2= layout.tuple_to_gp_Pnt(ptsL[z])
            # e=BRepBuilderAPI_MakeEdge(pt1,pt2)
            # DisplayColored(e.Shape(),color=color)
            # end of dbg
        linkList(navMeshSs)
        startJointSide.outHalfRoadSection = navMeshSs[0]
        endJointSide.inHalfRoadSection = navMeshSs[-1]
        startJointSide.directNavMeshSections = navMeshSs
        endJointSide.backNavMeshSections = navMeshSs

    outEdgs = dg.out_edges()
    used_sides = []

    for edge in outEdgs:
        startJointSide = eJSStart[edge]
        if startJointSide in used_sides:
            continue
        endJointSide = layout.eJSEnd[edge]
        used_sides.append(endJointSide)

        calcCenterPts(startJointSide, endJointSide)

    # colors=['WHITE','RED']
    # ind=0
    for edge in outEdgs:
        createNavMeshForEdge(edge)  # ,colors[ind & 1])
        # ind += 1

    linkJointsSides()

    allSectionsByEdges = [eJSStart[e].directNavMeshSections for e in outEdgs]
    allSectionsFlat = reduce(list.__add__, allSectionsByEdges)
    pickle.dump(allSectionsFlat, open('nmss.bin', 'wb'))


# depr
def makeNavMap():
    outEdgs = dg.out_edges()
    used_sides = []

    for edge in outEdgs:
        startJointSide = eJSStart[edge]
        if startJointSide in used_sides:
            continue
        endJointSide = layout.eJSEnd[edge]
        used_sides.append(endJointSide)

    linkJointsSides()

    allLanesByEdges = [eJSStart[e].directNavMeshSections for e in outEdgs]
    allSectionsFlat = reduce(list.__add__, allSectionsByEdges)
    pickle.dump(allSectionsFlat, open('nmss.bin', 'wb'))
    pass


def OCC_Display():
    for n in dg.nodes():
        j = dg.node[n]['joint']
        j.OCC_Display()

        for s in j.sides:
            if hasattr(s, 'roadFilledAsFace'):
                DisplayColored(s.roadFilledAsFace,
                               color=QuantColor(0.1, 0.1, 0.1))
                ts = triangulate(s.roadFilledAsFace)
                Display(ts)

    for b in blocks:
        b.display()


# depr
def blend_Display():

    roads = []
    tblocks = []
    grassies = []

    for n in dg.nodes():
        j = dg.node[n]['joint']
        j.blend_Display()

        for s in j.sides:
            if hasattr(s, 'roadFilledAsFace'):
                BReps_triangulate_to_BMesh(
                    [s.roadFilledAsFace], objectName='road', textureName='road_stripe_001')
                roads_tris = BRep_triangulate(s.roadFilledAsFace)
                roads.extend(roads_tris)

    dmp['roads'] = roads
    appendEntry(cdmp, 'tris', 'roads', roads)
    # return
    for b in blocks:
        rs = b.display()
        # print(list(rs))
        if rs:
            tblocks.extend(rs)

    appendEntry(cdmp, 'tris', 'blocks', tblocks)

    # gs = geoms['houses']
    # print('houses:',list(gs))
    # for g in gs:
    #     # BRep_triangulate_to_BMesh(g.Shape(),textureName='red_bricks_001')
    #     BReps_triangulate_to_BMesh([g.Shape()],textureName='wall_001')
    #     roads_tris.extend(BRep_triangulate(g.Shape()))
    #
    gs = geoms['grassy']
    for g in gs:
        BReps_triangulate_to_BMesh([g], textureName='grass_001')
        grassies.extend(BRep_triangulate(g))

    appendEntry(cdmp, 'tris', 'grassies', grassies)

    bpy.ops.object.lamp_add(type='HEMI')

    # json.dump(dmp,open('roads.json', 'w'))
    json.dump(dmp, open('dmps.json', 'w'))


def exportToJSON():
    ctw = []

    joints_tris = []
    roads_tris = []

    for n in dg.nodes():
        j = dg.node[n]['joint']
        joints_tris.extend(j.exportTriangulated())
        # cdmp.append(j.exportTriangulated())

        for s in j.sides:
            if hasattr(s, 'roadFilledAsFace'):
                road_tris = BRep_triangulate(s.roadFilledAsFace)
                roads_tris.extend(road_tris)

    appendEntry(cdmp, 'material', 'material', 'road_001')
    appendEntry(cdmp, 'tris', 'joints', joints_tris)
    appendEntry(cdmp, 'material', 'material', 'road_stripe_001')
    appendEntry(cdmp, 'tris', 'roads', roads_tris)

    appendEntry(ctw, 'data', 'city', cdmp)
    json.dump(ctw, open('cdmps.json', 'w'))


if __name__ == "__main__":

    import os

    print('running: ', os.path.realpath('__file__'))
    print('cwd:', os.getcwd())
    full_path = os.path.realpath('__file__')

    sys.path.append("/media/50G/v/c/_obs/BlenderScripts/tests")
    import graphs

    # create_city(*nx_create_grid_2d_graph_spectral())
    create_city(*graphs.createRectGraph(3, 3, 50, 50))
    linkJointsSides()
    getAllLinks()
    exportToJSON()

    # sys.setrecursionlimit(30000)
    # buildDiscretizedNavMeshForRoads(dg)

    # s=json.dumps(dg)
    # print(s)

    if display.OCC_FrontEnd:
        OCC_Display()
        start_display()
    else:
        blend_Display()
