import display
import json
import os

from OCC.Geom import Geom_Parabola,Geom_Line
from OCC.gp import gp_Ax1,gp_Ax2,gp_Pnt,gp_Dir,gp_XYZ
from OCC.GC import GC_MakeCircle
from OCC.Geom import Geom_OffsetCurve,Handle_Geom_Curve,Geom_Curve

from layout import discretizeCurveD1, tuple_to_gp_Pnt

if display.OCC_FrontEnd:
    from display import start_display


def draw_parab():
    ax1=gp_Ax1(gp_Pnt(0,0,0),gp_Dir(gp_XYZ(0,0,1)))
    pt=gp_Pnt(0,0,1)
    # parab=Geom_Parabola(ax1,pt)
    parab=Geom_Parabola(gp_Ax2(),5)
    parab2=Geom_Parabola(gp_Ax2(),25)
    # parab=Geom_Parabola(gp_Ax1(),gp_Pnt())
    # parab=Geom_Parabola()#ax1,gp_Pnt())
    l=Geom_Line(ax1)
    display.Display(l)
    display.Display(parab)
    display.Display(parab2)

    offDir=gp_Dir(1,0,0)
    cc=parab.Copy()
    print(type(cc))
    # oc=Geom_OffsetCurve(Geom_Curve(cc),6,offDir)

def draw_cir():
    ax1=gp_Ax1(gp_Pnt(0,0,0),gp_Dir(gp_XYZ(0,0,1)))
    pt=gp_Pnt(0,0,1)
    # parab=Geom_Parabola(ax1,pt)
    parab=GC_MakeCircle(gp_Ax2(),50)
    display.Display(parab.Value())
    ptss=discretizeCurveD1(parab.Value())
    print(ptss)
    json.dump(ptss,open('pathpts.json','w'))

    for pt in ptss:
        print(pt[0])
        display.Display(tuple_to_gp_Pnt(pt[0]))

if __name__ == "__main__":
    print(__file__)
    print(os.path.abspath(__file__))
    print(os.path.dirname(__file__))
    print(os.path.realpath(__file__))
    dn = os.path.dirname(os.path.abspath(__file__))

    print(dn)

    os.chdir(dn)

    print(os.getcwd())
    draw_parab()
    draw_cir()
    start_display()
