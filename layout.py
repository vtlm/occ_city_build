# from city2 import cSStart, cSEnd
from OCC.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCC.BRepFill import BRepFill_Filling
from OCC.GeomAPI import GeomAPI_Interpolate
from OCC.TColgp import TColgp_HArray1OfPnt
from OCC.GCPnts import GCPnts_AbscissaPoint_Length, GCPnts_QuasiUniformAbscissa
from OCC.BRepAdaptor import BRepAdaptor_Curve
from OCC.GeomAdaptor import GeomAdaptor_Curve
import display
from BRep_funx import BRep_triangulate
from funx import createEntry

# import bpy
# from FreeCAD import Vector
import math
# lines=[]
from OCC.gp import gp_Vec, gp_Pnt, gp_XYZ
from OCC.GC import GC_MakeArcOfCircle, GC_MakeSegment
from OCC.TopoDS import topods_Edge
from OCC._GeomAbs import GeomAbs_C0

from functools import reduce
from RoadLaneWrp import RoadLaneWrp

from meshTriang import triangulate
from display import Display
from c03 import makeFilling

cSStart = {}
cSEnd = {}
eJSStart = {}  # jointSide on Edge Start
eJSEnd = {}
display = None

straightShift = 5
insideJointShift = 4

# print('layout')


def calcEdgeDir(e, g, planar=False):
    ptS = g.node[e[0]]['joint'].loc
    ptE = g.node[e[1]]['joint'].loc
    dir = ptE - ptS
    if(planar):
        dir.SetZ(0)  # ptS.Z())#for gp_Vec
    # print(dir)
    dir.Normalize()
    # print('noz',dir)
    return dir


def getCounterDirectedEdge(edge, diGraph):
    return diGraph[edge[0]][edge[1]]['oppEdge']


def gp_Pnt_to_tuple(pnt):
    return pnt.X(), pnt.Y(), pnt.Z()


def tuple_to_gp_Pnt(t):
    return gp_Pnt(t[0], t[1], t[2])


def tuple_to_gp_Vec(t):
    return gp_Vec(t[0], t[1], t[2])


def gp_Vec_to_tuple(pnt):
    return pnt.X(), pnt.Y(), pnt.Z()


def pointRelToAt(basePt, dir, offsM):
    return basePt + dir * offsM


def calcRelPts(basePt, dirOffs):
    newPt = basePt
    retPts = []
    for dirOff in dirOffs:
        newPt = pointRelToAt(newPt, dirOff[0], dirOff[1])
        retPts.append(newPt)
    return retPts


def calcSplinePreBoundPts(ptS, dirS, ptE, dirE, distanceIsRoad=12, dotTol=0.1, reverseDirE=True):
    '''
    :param ptS:
    :param dirS:
    :param ptE:
    :param dirE:
    :param distanceIsRoad:
    :param dotTol:
    :return: four points for make spline
    '''
    tVec = ptE - ptS
    dist = tVec.Magnitude()  # ptS.Distance(ptE)
    if dist > distanceIsRoad:
        shift = dist * 0.2
    else:
        dotPr = dirS.Dot(dirE)
        if dotPr > (1 - dotTol):  # colinear (straight)
            shift = insideJointShift / 2
        elif dotPr < -(1 - dotTol):  # inv colinear (U-turn)
            shift = dist * 0.5
        else:  # (turn)
            shift = dist * 0.3

    pt1 = pointRelToAt(ptS, dirS, shift)
    if reverseDirE:
        cDirE = dirE.Reversed()
    else:
        cDirE = dirE
    pt2 = pointRelToAt(ptE, cDirE, shift)
    rA = [ptS, pt1, pt2, ptE]
    rAt = [gp_Vec_to_tuple(x) for x in rA]
    return rAt


def discretizeCurve(curve, dLength):
    # ca=BRepAdaptor_Curve(curve)
    ca = GeomAdaptor_Curve(curve)
    l = GCPnts_AbscissaPoint_Length(ca)
    ptsNumb = round(l / dLength)
    # print('l=',l,'pNumb=',ptsNumb)
    qua = GCPnts_QuasiUniformAbscissa(ca, ptsNumb)
    # print('qua',qua.NbPoints())
    parms = []
    for i in range(1, qua.NbPoints() + 1):
        parms.append(qua.Parameter(i))
    # print(parms)
    pts = [gp_Pnt_to_tuple(ca.Value(p)) for p in parms]
    # print(pts)
    return pts


def discretizeCurveD1(curve, dLength=2):
    # ca=BRepAdaptor_Curve(curve)
    ca = GeomAdaptor_Curve(curve)
    l = GCPnts_AbscissaPoint_Length(ca)
    ptsNumb = round(l / dLength)
    # print('l=',l,'pNumb=',ptsNumb)
    qua = GCPnts_QuasiUniformAbscissa(ca, ptsNumb)
    # print('qua',qua.NbPoints())
    parms = []
    pt = gp_Pnt()
    tang = gp_Vec()
    for i in range(1, qua.NbPoints() + 1):
        parm = qua.Parameter(i)
        ca.D1(parm, pt, tang)
        parms.append((gp_Pnt_to_tuple(pt), gp_Vec_to_tuple(tang)))
    # print(pts)
    return parms


def dbgMakeSpline(pts):
    pN = len(pts)
    # v1
    # arr=TColgp_Array1OfPnt(1,pN)
    # for i in range(1,pN+1):
    #     arr.SetValue(i,gp_Pnt(pts[i-1].XYZ()))
    #     print(i,pts[i-1].X(),pts[i-1].Y(),pts[i-1].Z())
    # self.rSpline=GeomAPI_PointsToBSpline(arr)
    # #dbg
    # if self.rSpline.IsDone():
    #     Display(self.rSpline.Curve())
    # else:
    #     print('NotDone!')
    # v2
    arr = TColgp_HArray1OfPnt(1, pN)
    for i in range(1, pN + 1):
        inpVal = pts[i - 1]
        if type(inpVal) in [gp_Vec, gp_Pnt]:
            convVal = inpVal.XYZ()
        else:
            convVal = gp_XYZ(*inpVal)

        # print(convVal)
        arr.SetValue(i, gp_Pnt(convVal))
        # print(i,pts[i-1].X(),pts[i-1].Y(),pts[i-1].Z())
    spline = GeomAPI_Interpolate(arr.GetHandle(), False, 0.01)
    spline.Perform()
    # dbg
    if spline.IsDone():
        Display(spline.Curve())
    else:
        print('NotDone!')

    return spline


class RoadLane(object):

    def __init__(self, center, tl):
        self.center = center
        self.tlHalfRoadSection = tl
        self.links = []  # possible links to other roadLanes
        self.linksSplines = {}
        self.linksDiscrSplines = {}  # linked RoadLane : discretized spline to linked RoadLane

        # dbgDrawUpStake(self.center,20)

    # def calcSplinePts(self):

    def calcSplinesPts(self):
        for linked in self.links:
            self.linksSplines[linked] = calcSplinePreBoundPts(
                self.center, self.tlHalfRoadSection.faceDir, linked.center, linked.tlHalfRoadSection.faceDir)
            pts = self.linksSplines[linked]
            # todo: remove, add inner conversion
            ptsV = [tuple_to_gp_Vec(x) for x in pts]
            spline = dbgMakeSpline(ptsV)
            pts = discretizeCurveD1(spline.Curve())
            self.linksDiscrSplines[linked] = pts
            # for p in pts:
            #     dbgDrawUpStake(tuple_to_gp_Vec(p[0]),10,'GREEN')

    def simplify(self):
        def reMapMap(map):
            itms = map.items()
            # print(list(itms))
            newMap = {}
            for i in itms:
                # print(i)
                # print(i.key)
                # print(i.value)
                newMap[i[0].ind] = i[1]
            return newMap
        newLinks = [l.ind for l in self.links]
        newDiscrSplines = reMapMap(self.linksDiscrSplines)
        # return {'links': newLinks, 'linksSplines': newDiscrSplines}
        return newDiscrSplines


class HalfRoadSection(object):

    def __init__(self, lPt, rPt, faceDir, tl):
        self.lPt = lPt
        self.rPt = rPt
        self.faceDir = faceDir
        self.tlJointSide = tl
        self.lanes = []
        self.createLanes()

    def createLanes(self, laneWidth=3):
        # traverseVec=gp_Vec(self.lPt,self.rPt)
        traverseVec = self.rPt - self.lPt
        hRoadWidth = traverseVec.Magnitude()
        lanesNumb = round(hRoadWidth / laneWidth)
        realLaneWidth = hRoadWidth / lanesNumb
        for i in range(0, lanesNumb):
            self.lanes.append(RoadLane(self.lPt.Added(
                traverseVec.Multiplied((i + 0.5) / lanesNumb)), self))

    def linkLanes(self, othSection):
        for i, l in enumerate(self.lanes):
            l.links.append(othSection.lanes[i])

    def calcLaneSplinesPts(self):
        for l in self.lanes:
            l.calcSplinesPts()


class JointSide(object):

    def __init__(self, inEdge, outEdge, tl, width=9):
        self.inEdge = inEdge
        self.outEdge = outEdge
        # self.rLane=RoadLaneWrp()
        # self.lLane=RoadLaneWrp()
        self.faceDir = calcEdgeDir(outEdge, tl.graph, planar=True)
        self.aR = math.atan2(self.faceDir.Y(), self.faceDir.X())
        # self.next=None
        # self.prev=None
        # self.inHR=None
        # self.outHR=None
        # self.curveToNext=None
        self.tl = tl
        self.width = width
        self.offset = width + 2
        # self.h=h
        eJSStart[outEdge] = self
        eJSEnd[inEdge] = self
        # center=self.tl.loc
        self.posRoadCenter = self.tl.loc + self.faceDir * self.offset
        up = gp_Vec(0, 0, 1)
        self.rDir = self.faceDir.Crossed(up)
        self.rpos = pointRelToAt(self.posRoadCenter, self.rDir, self.width)
        self.lpos = pointRelToAt(self.posRoadCenter, self.rDir, -self.width)
        # self.rpos=self.posRoadCenter+self.rDir*self.width
        # self.lpos=self.posRoadCenter-self.rDir*self.width
        # self.rpos=self.posRoadCenter+self.faceDir.Crossed(up)*self.width
        # self.lpos=self.posRoadCenter-self.faceDir.Crossed(up)*self.width
        # self.rpos=pos+self.dir.orthogonal()*self.width
        # self.lpos=pos-self.dir.orthogonal()*self.width
        self.inHRSection = HalfRoadSection(
            self.posRoadCenter, self.rpos, self.faceDir.Reversed(), self)
        self.outHRSection = HalfRoadSection(
            self.posRoadCenter, self.lpos, self.faceDir, self)

        cSStart[self.outEdge] = self.rpos
        cSEnd[self.inEdge] = self.lpos

    def getAllLanes(self):
        return self.inHRSection.lanes + self.outHRSection.lanes

    def setOpposite(self, js):
        self.opposite = js

    def calcLanesSplinesPts(self):
        self.inHRSection.calcLaneSplinesPts()
        self.outHRSection.calcLaneSplinesPts()

#     def calcSplinesStartPtsAtOffs(self,offs):
#         self.rSplinePts=calcRelPts(self.posRoadCenter,[(self.rDir,offs),(self.faceDir,straightShift)])
#         self.lSplinePts=calcRelPts(self.posRoadCenter,[(self.rDir,-offs),(self.faceDir,straightShift)])
#
# #tmp
#     # def calcLaneSplines(self):
#     #     self.rLane.SplinePts=calcRelPts(self.posRoadCenter,[(self.rDir,self.width/2),(self.faceDir,straightShift)])
#     #     self.lLane.SplinePts=calcRelPts(self.posRoadCenter,[(self.rDir,-self.width/2),(self.faceDir,straightShift)])
#
#     def calcSplineStartPts(self):
#         self.calcSplinesStartPtsAtOffs(self.width)
#         # self.calcLaneSplines()

    def makeSpline(self):
        pts = calcSplinePreBoundPts(
            self.rpos, self.faceDir, self.opposite.lpos, self.opposite.faceDir, reverseDirE=False)
        ptsV = [tuple_to_gp_Vec(x) for x in pts]
        self.rSpline = dbgMakeSpline(ptsV)
        return
# depr

    def discretizeCurves(self, dLength=1):
        self.discrPtsToNext = discretizeCurve(
            self.curveToNext.Value(), dLength)
        self.discrRSpline = discretizeCurve(self.rSpline.Curve(), 2)

    # def discretizeInnerCurves(self,dLength=1):
    #     self.discrPtsToNext=self.discretizeCurve(self.curveToNext.Value(),dLength)
    #     # self.discrRSpline=self.discretizeCurve(self.rSpline.Curve(),dLength)
    #     # self.discrLSpline=self.discretizeCurve(self.lSpline.Curve(),dLength)
    #
    # def discretizeSplinesCurves(self,dLength=1):
    #     # self.discrPtsToNext=self.discretizeCurve(self.curveToNext.Value(),dLength)
    #     self.discrRSpline=self.discretizeCurve(self.rSpline.Curve(),dLength)
    #     # self.discrLSpline=self.discretizeCurve(self.lSpline.Curve(),dLength)

    # dbg
    def dbgDraw(self):
        pass
        # global cSStart
        # global cSEnd
        # print('udu!')
        # center=Vector((self.tl.loc[0],self.tl.loc[1],self.h))
        # dirV=Vector((self.dir[0],self.dir[1],self.h))
        # dir=dirV-center
        # dir.normalize()
        # print('d',dirV,center,dir,dir.normalized())
        # bpy.ops.mesh.primitive_cube_add(radius=0.21, view_align=False, enter_editmode=False, location=center, layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        # bpy.ops.mesh.primitive_cube_add(radius=1, view_align=False, enter_editmode=False, location=pos, layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        # bpy.ops.mesh.primitive_cube_add(radius=0.51, view_align=False, enter_editmode=False, location=self.rpos, layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        # bpy.ops.mesh.primitive_cube_add(radius=0.51, view_align=False, enter_editmode=False, location=self.lpos, layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        # lines.append([Vector((1,1,1)),Vector((2,2,2))])


class Joint(object):

    def __init__(self, loc, graph):
        self.loc = gp_Vec(loc[0], loc[1], loc[2])  # .Multiplied(200)
        self.graph = graph
        self.sides = []

    def hasHR(self, hr):
        for s in self.sides:
            if s.inHR == hr or s.outHR == hr:
                return True
        return False

    def addInHR(self, hr):
        if not self.hasHR(hr):
            js = JointSide
            js.inHR = hr
            self.sides.append(js)

    def addSide(self, inEdge, outEdge):
        '''
        :param inEdge: graph edge
        :param outEdge:
        :return:
        '''
        self.sides.append(JointSide(inEdge, outEdge, self))

    def linkSides(self):

        def cLinkSides(s1, s2):
            s1.next = s2
            s2.prev = s1

        for i in range(0, len(self.sides) - 1):
            cLinkSides(self.sides[i], self.sides[i + 1])
            # self.sides[i].next=self.sides[i+1]
            # self.sides[i+1].prev=self.sides[i]
        cLinkSides(self.sides[-1], self.sides[0])

    # def makeArc(self,ptS,ptE,dev = 0.5):
    #     d=ptE-ptS
    #     hd=d.multiply(0.5)
    #     rd=d.cross(Vector(0,0,1))
    #     rd.normalize()
    #     midP=ptS+hd
    #     mid=midP+rd.multiply(d.Length*dev)
    #     a=Part.Arc(ptS,mid,ptE)
    #     Part.show(a.toShape())

    def linkHalfRoadsSections(self):
        for ss in self.sides:
            for sd in self.sides:
                # ss.inHalfRoadSection.links.append(sd.outHalfRoadSection)
                ss.inHRSection.linkLanes(sd.outHRSection)
            ss.outHRSection.linkLanes(ss.opposite.inHRSection)

    def calcLaneSplinesPts(self):
        for s in self.sides:
            s.calcLanesSplinesPts()

    # def linkHalfRoadsLanes(self):
    #     for ss in self.sides:
    #         for sd in self.sides:
    #             ss.lLane.links.append(sd.rLane)

    def makeToNextSideCurves(self):
        for s in self.sides:
            # s.curveToNext = makeArc(s.rpos,s.next.lpos)
            dAng = s.next.aR - s.aR
            # print(dAng,math.sin(dAng))
            s.curveToNext = makeArc(s.lpos, s.next.rpos, math.sin(dAng))

    # def calcSplineStartPts(self):
    #     for s in self.sides:
    #         s.calcSplineStartPts()
    #         # s.calcLaneSplines()

    def makeSplines(self):
        for s in self.sides:
            s.makeSpline()

    def discretizeCurves(self):
        for s in self.sides:
            s.discretizeCurves()

    def getAllBoundPtsAsSequence(self):
        ptssArr = [s.discrPtsToNext for s in self.sides]
        allPts = reduce(list.__add__, ptssArr)
        # allPts.reverse()
        return allPts

    def makePatchFromDiscretizedPointsAsBRepFilling(self):
        pts = self.getAllBoundPtsAsSequence()
        ptsc = pts
        ptsc.append(pts[0])
        # print(ptsc)
        # print('rev')
        # ptsc.reverse()
        # print(ptsc)
        self.filling = makeFilling(ptsc)

    def makePatchFromCurvesAsBRepFilling(self):
        p = [s.prev.curveToNext for s in self.sides]
        # pls=[Part.Line(s.lpos,s.rpos) for s in self.sides]
        # pls=[GC_MakeSegment(gp_Pnt(s.lpos.XYZ()),gp_Pnt(s.rpos.XYZ())) for s in self.sides]
        pls = [GC_MakeSegment(gp_Pnt(s.rpos.XYZ()), gp_Pnt(
            s.lpos.XYZ())) for s in self.sides]
        ps = zip(p, pls)
        pas = [e for l in ps for e in l]  # flatmap
        # print('dbg makePatch: tot sides, segments: ',len(self.sides),len(pas))
        # dbg
        # dhgt=4
        # hgt=dhgt

        # replace with function
        # w=BRepFill_Filling()
        #
        # for sg in pas:
        #     e=BRepBuilderAPI_MakeEdge(sg.Value())
        #     w.Add(topods_Edge(e.Shape()), GeomAbs_C0)
        #
        #     #dbg
        #     # sp=sg.Value().GetObject().Value(0.25)
        #     # dbgDrawUpStake(gp_Vec(sp.XYZ()),hgt,'RED')
        #     # Display(e.Shape())
        #     #hgt+=dhgt
        #
        #     # if not w.IsDone():
        #     #     break
        # w.Build()

        pss = [p.Value() for p in pas]
        # print(pss)
        # w = makeFilling(pss)
        f = w.Face()
        # if f.IsDone():
        # Display(f)
        p = triangulate(f)
        Display(p, update=True)

    def getAllLanes(self):
        allLanes = []
        for s in self.sides:
            allLanes.extend(s.getAllLanes())
        return allLanes

    def OCC_Display(self):
        if hasattr(self, 'filling'):
            f = self.filling.Face()
            # if f.IsDone():
            Display(f)
            p = triangulate(f)
            Display(p, update=True)

    def blend_Display(self):
        # print(self.filling.IsDone())
        BReps_triangulate_to_BMesh(
            [self.filling.Face()], objectName='Joint', textureName='road_001')

    def exportTriangulated(self):
        # return createEntry('tris','Joint',BRep_triangulate(self.filling.Face()))
        return BRep_triangulate(self.filling.Face())

    # def makePatch(self):
    #     p=[s.prev.curveToNext for s in self.sides]
    #     # pls=[Part.Line(s.lpos,s.rpos) for s in self.sides]
    #     # pls=[GC_MakeSegment(gp_Pnt(s.lpos.XYZ()),gp_Pnt(s.rpos.XYZ())) for s in self.sides]
    #     pls=[GC_MakeSegment(gp_Pnt(s.rpos.XYZ()),gp_Pnt(s.lpos.XYZ())) for s in self.sides]
    #     ps=zip(p,pls)
    #     pas=[e for l in ps for e in l]
    #     # print('dbg makePatch: tot sides, segments: ',len(self.sides),len(pas))
    #     w=BRepBuilderAPI_MakeWire()
    #     dhgt=4
    #     hgt=dhgt
    #     for sg in pas:
    #         sp=sg.Value().GetObject().Value(0.25)
    #         dbgDrawUpStake(gp_Vec(sp.XYZ()),hgt,'RED')
    #         e=BRepBuilderAPI_MakeEdge(sg.Value())
    #         Display(e.Shape())
    #         w.Add(topods_Edge(e.Shape()))
    #         if not w.IsDone():
    #             break
    #         hgt+=dhgt
    #     f=BRepBuilderAPI_MakeFace(topods_Wire(w.Shape()))
    #     if f.IsDone():
    #         Display(f.Shape())


# import Part

def makeArc(ptS, ptE, dev=-0.5):
    d = ptE - ptS
    hd = d.Multiplied(0.5)
    rd = d.Crossed(gp_Vec(0, 0, 1))
    # rd=d.cross(FreeCAD.Vector(0,0,1))
    rd.Normalize()
    midP = ptS + hd
    mid = midP - rd.Multiplied(d.Magnitude() * (0.25 * dev + 0.01))
    # dbgDrawUpStake(ptS,20,'BLUE')
    # dbgDrawUpStake(mid,20,'BLUE')
    # print(ptS,mid,ptE)
    # a=GC_MakeArcOfCircle(gp_Pnt(ptS.XYZ()),mid,gp_Pnt(ptE.XYZ()))
    a = GC_MakeArcOfCircle(gp_Pnt(ptS.XYZ()), gp_Pnt(
        mid.XYZ()), gp_Pnt(ptE.XYZ()))
    # a=GC_MakeSegment(gp_Pnt(ptS.XYZ()),gp_Pnt(ptE.XYZ()))
    # Part.show(a.toShape())
    return a  # .Value()


def dbgDrawUpStake(loc, h, color='RED'):
    tPos = loc + gp_Vec(0, 0, h)
    e = BRepBuilderAPI_MakeEdge(gp_Pnt(loc.XYZ()), gp_Pnt(tPos.XYZ()))
    Display(e.Shape(), color=color)
