from OCC.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire, BRepBuilderAPI_Transform
from OCC.BRepOffsetAPI import BRepOffsetAPI_MakePipe
from OCC.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCC.GC import GC_MakeLine, GC_MakeSegment
from OCC.GProp import GProp_GProps
from OCC.Quantity import Quantity_Color, Quantity_TOC_RGB
from OCC.gp import gp_Pnt, gp_Vec
from OCC import gp as _gp
from OCC.TopoDS import topods_Face, topods_Edge, topods_Wire
from OCC.BRepGProp import brepgprop_SurfaceProperties
from OCC.BRepFill import brepfill_Shell, brepfill_Face
from shapely.geometry import Polygon
from c03 import makeFace
from display import QuantColor
from meshTriang import triangulate

__author__ = 'v'
"""
import sys
sys.path.append('/home/v/c/FreeCAD_S1')
import city2fc
"""

import random
# from shapely.geometry import Polygon, LinearRing
from subdiv import subDiv

from OCC.Display.SimpleGui import init_display


# import bpy
import layout
import c03
from layout import Joint, JointSide, calcEdgeDir, cSStart, cSEnd, eJSStart
import networkx as nx
from operator import itemgetter
from functools import reduce
# from FreeCAD import Vector
# import Part
import math
from shapely.affinity import scale

pts=[]
lines=[]

# def createCurvedPatch(node):

rs=[]

display, start_display, add_menu, add_function_to_menu = init_display()
layout.display=display
c03.display=display


def create_city(h=0):

    # removeAll()

    #set consts
    r=4
    range=200

    #create graph
    pg=nx.grid_2d_graph(r,r)
    dg=nx.DiGraph(pg)
    # pos=nx.spring_layout(g,iterations=200)
    pos=nx.spectral_layout(pg)
    for p in pos.items():
        # print type(p[0])
        # dg.node[p[0]]['joint']=Joint(p[1]*100,dg)
        dg.node[p[0]]['joint']=Joint((p[1][0],p[1][1],h*random.random())*range,dg)
    # print(pos)
    # print g.nodes(data=True)
    # for n in g.nodes():
    #     # print g.node[n]
    #     j=g.node[n]['joint']
    #     # print j.loc

    # dg=nx.DiGraph(g)

    #TODO: angles, dir maybe unneeded
    inEs=dg.in_edges()
    outEs=dg.out_edges()
    inEAs=[(x,calcEdgeDir(x,dg)) for x in inEs]
    outEAs=[(x,calcEdgeDir(x,dg)) for x in outEs]
    # print ('inEAs',inEAs)

    #set opposite edges
    #TODO simplify without angles
    for inEA in inEAs:
        # print type(inEA[1]), inEA[1], inEA[1].__neg__()
        # print inEA[1], outEAs[0][1].__neg__(),inEA[1].__eq__(outEAs[0][1].__neg__())
        # res=inEA[1].__eq__(outEAs[0][1].__neg__())
        # print res
        # print True in res
        # print inEA[1].__ne__(outEAs[0][1].__neg__())
        # cEA=next((x for x in outEAs if not False in inEA[1].__eq__(x[1].__neg__())),None)
        # cEA=next((x for x in outEAs if inEA[1].dot(x[1]) < -0.9),None)
        cEA=next((x for x in outEAs if inEA[0][0] == x[0][1] and inEA[0][1] == x[0][0]),None)
        # print ('cEA=', cEA, inEA, cEA[1].dot(inEA[1]))
        dg[cEA[0][0]][cEA[0][1]]['oppEdge']=inEA[0]
        # dg[cEA[0][0]][cEA[0][1]]['oppEdge']=inEA[0]
        # dg[cEA[0]]['oppEdge']=inEA[0]//don't works
        # dg[inEA[0]]['oppEdge']=cEA[0]
        #dbg
        # pt1=dg.node[cEA[0][0]]['joint'].loc
        # pt2=dg.node[inEA[0][0]]['joint'].loc
        # print('pts',pt1,pt2)

        #dbg
        # pts.append(Vector((pt1[0],pt1[1],0)))
        # lines.append([Vector((pt1[0],pt1[1],0)),Vector((pt2[0],pt2[1],0))])


    #create JointSides on graph nodes
    for n in dg.nodes():
        # print dg.out_edges(n)
        # print dg.in_edges(n)
        # print dg.node[n]
        j=dg.node[n]['joint']
        # print id(j),j.loc
        inEs=dg.in_edges(n)
        # print 'inEs=',inEs
        for inE in inEs:
            j.addSide(inE,dg[inE[0]][inE[1]]['oppEdge'])
        # print id(j.sides),j.sides

            # j.addSide(inEA[0],cEA[0])

    #link opp JointSides (for roads)
    for e in dg.edges():
        oppE=dg[e[0]][e[1]]['oppEdge']
        js1=eJSStart[e]
        js2=eJSStart[oppE]
        js1.setOpposite(js2)
        js2.setOpposite(js1)

    #dbg
    # for e in dg.edges():
    #     j=dg.node[e[0]]['joint']
    #     print('sides: ',len(j.sides),list(j.sides))
    #     # print(type(e[0]),e[0])
    #     d=calcEdgeDir(e,dg)
    #     # print 'dir=', d, -d
    #     # print e,dg[e[0]][e[1]]['oppEdge']


    # for n in dg.nodes():
    #     j=dg.node[n]['joint']
    #     vv=j.loc
    #     # bpy.ops.mesh.primitive_cube_add(radius=1, view_align=False, enter_editmode=False, location=(vv[0], vv[1], 0), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
    #
    #     ss=j.sides
    #     for s in ss:
    #         print (s)
    #         outEdge=s.outEdge
    #         dir=calcEdgeDir(outEdge,dg)
    #         # print('dd',dir)
    #         s.draw()
    #         s.do()
    #         # print(cSStart)

    #nodes joints (crossroads) geometry, sides sort
    for n in dg.nodes():
        # print(len(dg.node[n]['joint'].sides))
        ss=dg.node[n]['joint'].sides
        #print(ss)

        def getKey(js):
            return js.aR
        sss=sorted(ss,key=getKey)
        dg.node[n]['joint'].sides=sss
        dg.node[n]['joint'].linkSides()

        dg.node[n]['joint'].makeToNextSideCurves()
        dg.node[n]['joint'].makePatchFromCurvesAsBRepFilling()

        #print(sss)

        #dbg create patch
        # spts=[]
        # for s in sss:
        #     spts.append(s.rpos)
        #     spts.append(s.lpos)
        # #print(list(spts))
        # create_patch(spts)
        # # for s in dg.node[n]['joint'].sides:
        # #     # oppEdge=
        # #     print(s.aR)
        #     # print(s.lpos, s.rpos)

    #print(cSStart)

    # #links (roads) geometry ver 1
    # for e in dg.edges():
    #     print(e,cSStart[e],cSEnd[e])
    #     oppE=dg[e[0]][e[1]]['oppEdge']
    #     print(oppE,cSStart[oppE],cSEnd[oppE])
    #     create_patch([cSStart[e],cSEnd[e],cSStart[oppE],cSEnd[oppE]])

    for n in dg.nodes():
        j=dg.node[n]['joint']
        j.calcSplineStartPts()

    for n in dg.nodes():
        j=dg.node[n]['joint']
        j.makeSplines()

    used_sides=[]

    def makeRoad(edge):
        startJointSide=eJSStart[edge]
        if startJointSide in used_sides:
            return
        counterEdge = layout.getCounterDirectedEdge(edge,dg)
        endJointSide= layout.eJSEnd[edge]
        used_sides.append(endJointSide)

        spl1=startJointSide.rSpline
        spl2=endJointSide.rSpline
        e1=BRepBuilderAPI_MakeEdge(spl1.Curve())
        spl2.Curve().GetObject().Reverse()
        e2=BRepBuilderAPI_MakeEdge(spl2.Curve())
        fr=brepfill_Face(topods_Edge(e1.Shape()),topods_Edge(e2.Shape()))
        display.DisplayColoredShape(fr,color=QuantColor(0.1,0.1,0.1))
        ts=triangulate(fr)
        display.DisplayShape(ts)
        #straight segments version
        # def getPts(jointSide,counterJointSide,reversed=False):
        #     pts=[]
        #     pts.extend(jointSide.rSplinePts)
        #     pts2=[]
        #     pts2.extend(counterJointSide.lSplinePts)
        #     pts2.reverse()
        #     pts.extend(pts2)
        #     if reversed:
        #         pts.reverse()
        #     return pts
        #
        # ptsD=getPts(startJointSide,endJointSide)
        # ptsCD=getPts(endJointSide,startJointSide,reversed=True)
        # wireR= c03.makeWire(ptsD)
        # wireL= c03.makeWire(ptsCD)
        # sh=brepfill_Shell(topods_Wire(wireR.Shape()),topods_Wire(wireL.Shape()))
        # display.DisplayColoredShape(sh,color=layout.QuantColor(0.1,0.1,0.1))



    for e in dg.edges():
        makeRoad(e)


    # # #links (roads) geometry ver 1
    # for e in dg.edges():
    #     jsS=eJSStart[e]
    #     oppE=dg[e[0]][e[1]]['oppEdge']
    #     jsE=eJSStart[oppE]
    #     # create_patch([jsS.lpos,jsS.rpos,jsE.lpos,jsE.rpos,jsS.lpos],pColor=Quantity_Color(0.2,0.2,0.2, Quantity_TOC_RGB))
    #     create_patch([jsS.lSplinePts[0],jsS.rSplinePts[-1],jsE.lSplinePts[-1],jsE.rSplinePts[-1],jsS.lSplinePts[0]],pColor=Quantity_Color(0.2,0.2,0.2, Quantity_TOC_RGB))
    #     # create_patch([jsS.lpos,jsS.rpos,jsE.lpos,jsE.rpos,jsS.lpos],pColor='RED')

    #get all joints sides
    jsss=[dg.node[n]['joint'].sides for n in dg.nodes()]
    # js=sum(jss)
    jss=reduce(list.__add__,jsss)

    #curves version
    innerPatches=[]
    tptss=[]
    used_s=[]
    for js in jss:
        if not js in used_s:

            dpts=[]
            poss=[]
            cs=js

            while True:
                used_s.append(cs)
                poss.append(cs.curveToNext.Value())
                p1=cs.next.rpos
                p2=cs.next.opposite.lpos
                #straight line version
                # l=GC_MakeSegment(gp_Pnt(p1.XYZ()),gp_Pnt(p2.XYZ()))
                # poss.append(l.Value())
                #BSpline version
                spl=cs.next.rSpline
                poss.append(spl.Curve())
                dpts.extend([p1,p2])
                cs=cs.next.opposite

                if cs == js:
                    break

            innerPatches.append(poss)
            tptss.append(dpts)
            # print(poss)
            # for p in poss:
            #     print(id(p))

    #search max
    lens=[len(ip) for ip in innerPatches]
    i,v=max(enumerate(lens),key=itemgetter(1))
    # print(i,v)
    outerOutlineL=innerPatches[i]
    innerPatches.remove(innerPatches[i])

    outerOutline= c03.makeWire(outerOutlineL)
    bf= c03.makeFilling(outerOutlineL)
    gp=GProp_GProps()
    brepgprop_SurfaceProperties(bf.Face(),gp)
    cm=gp.CentreOfMass()
    #dbg
    # print(cm.X(),cm.Y(),cm.Z())
    # layout.dbgDrawUpStake(gp_Vec(cm.XYZ()),150)

    tSc=_gp.gp_Trsf()
    tSc.SetScale(cm,1.35)
    # tt=BRepBuilderAPI_Transform(t.Multiplied(tSc))
    tt=BRepBuilderAPI_Transform(tSc)
    tt.Perform(outerOutline.Shape())
    tps1=tt.Shape()
    display.DisplayShape(tps1)

    sh=brepfill_Shell(topods_Wire(outerOutline.Shape()),topods_Wire(tps1))
    display.DisplayColoredShape(sh,color='GREEN')

    # w=BRepBuilderAPI_MakeWire()
    # for c in outerOutline:
    #     e=BRepBuilderAPI_MakeEdge(c)
    #     w.Add(topods_Edge(e.Shape()))


    # prf=BRepBuilderAPI_MakeEdge(gp_Pnt(0,10,0),gp_Pnt(0,15,2))
    # p=BRepOffsetAPI_MakePipe(topods_Wire(w.Shape()),prf.Shape())



    lens=[len(ip) for ip in tptss]
    i,v=max(enumerate(lens),key=itemgetter(1))
    # print(i,v)
    fm=tptss[i]
    tptss.remove(tptss[i])
    # fmax=makeFace(fm)
    # display.DisplayShape(fmax.Shape(),color="RED")

    for p in innerPatches:
        # dbg_display_as_edges(p)
        create_patch(p,extrudeH=0.0,pColor='GREEN')
    # create_patch(innerPatches[0],True)

    #dbg areas view
    # for d in tptss:
    #     d1=d
    #     d1.append(d[0])
    #     f=makeFace(d1)
    #     display.DisplayShape(f.Shape())

    for gds in tptss:
        ds=[(gd.X(),gd.Y(),gd.Z()) for gd in gds]
        p=Polygon(ds)
        # print(p.area)
        ps=subDiv(p)
        for p in ps:
            p2=scale(p, xfact=0.85, yfact=0.85)
            # p2=p.buffer(0.1)
            # print(list(p2.coords))
            pl=[]
            pl.extend(p2.boundary.coords)
            h=20+random.random()*30
            # create_patch(pl,h,randomColor())
        # p=Polygon(d)
        # print(p.area)
        # ps=subDiv(p)
        # for p in ps:
        #     print(list(p.boundary.coords))
        #     pl=[]
        #     pl.extend(p.boundary.coords)
        #     create_patch(pl,True)
    # global rs
    # rs=innerPatches

def dbg_display_as_edges(tcs):
    for trimCurv in tcs:
        print(trimCurv.GetObject().StartPoint().X())
        e=BRepBuilderAPI_MakeEdge(trimCurv)
        display.DisplayShape(e.Shape())

def create_patch(p_i,extrudeH=0,pColor='RED'):
    p=p_i
    # p.append(p_i[0])
    # f=makeFace(p)
    f= c03.makeFilling(p)
    z=triangulate(f.Face())
    display.DisplayShape(z)
    # if extrudeH != 0:
    #     p=BRepPrimAPI_MakePrism(topods_Face(f.Shape()),gp_Vec(0,0,extrudeH))
    #     display.DisplayColoredShape(p.Shape(),color=pColor,update=True)
    # else:
    #     display.DisplayColoredShape(f.Face(),color=pColor,update=True)
    #

def randomColor():
    return Quantity_Color(random.random(),random.random(),random.random(),Quantity_TOC_RGB)





if __name__ == "__main__":
    create_city(0.1)
    print('test')
    start_display()
