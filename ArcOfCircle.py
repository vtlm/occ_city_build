from OCC.GC import GC_MakeArcOfCircle
from OCC.gp import gp_Pnt, gp_Dir
from OCC.Geom import Geom_OffsetCurve, Geom_Line

from OCC.gp import gp_Pnt2d, gp_Dir2d
from OCC.GCE2d import GCE2d_MakeArcOfCircle
from OCC.Geom2d import Geom2d_OffsetCurve

from OCC.Geom2d import Geom2d_VectorWithMagnitude

from OCC.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCC.BRepAdaptor import BRepAdaptor_Curve
from OCC.GCPnts import GCPnts_UniformAbscissa

import pdb


import display
if display.OCC_FrontEnd:
    from display import start_display


def axis():
    xa=Geom_Line(gp_Pnt(),gp_Dir(1,0,0))
    display.Display(xa)
    xa=Geom_Line(gp_Pnt(),gp_Dir(0,1,0))
    display.DisplayColored(xa,'GREEN')
    xa=Geom_Line(gp_Pnt(),gp_Dir(0,0,1))
    display.DisplayColored(xa,'BLUE')

def f_aoc():
    aoc=GC_MakeArcOfCircle(gp_Pnt(),gp_Pnt(5,2,0),gp_Pnt(10,0,0))
    display.Display(aoc.Value())

    display.Display(gp_Pnt(5,4,0))

    oc=Geom_OffsetCurve(aoc.Value(),-1,gp_Dir(0,0,1))
    display.Display(oc)


def f_aoc2d():
    aoc=GCE2d_MakeArcOfCircle(gp_Pnt2d(),gp_Pnt2d(5,3),gp_Pnt2d(10,0))
    display.Display(aoc.Value())

    display.Display(gp_Pnt(5,4,0))

    oc=Geom2d_OffsetCurve(aoc.Value(),-1)
    display.Display(oc)

def f_vecs():
    v=Geom2d_VectorWithMagnitude(gp_Pnt2d(),gp_Pnt2d(10,2))
    display.Display(v)

def tst_Parms():
    bre=BRepBuilderAPI_MakeEdge(gp_Pnt(),gp_Pnt(20,10,0))
    edge=bre.Edge()
    ca=BRepAdaptor_Curve(edge)
    print(ca.FirstParameter(),ca.LastParameter())
    print(ca.Value(ca.FirstParameter()),ca.Value(ca.LastParameter()))
    absc=GCPnts_UniformAbscissa()




if __name__ == '__main__':

    tst_Parms()
    # return
    # axis()
    # f_aoc()
    # f_aoc2d()
    # f_vecs()
    # start_display()
