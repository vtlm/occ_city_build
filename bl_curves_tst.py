"""
from importlib import reload
filename = "/media/50G/v/c/City_Py_OCC/bl_curves_tst.py"
exec(compile(open(filename).read(), filename, 'exec'))
"""

import sys
sys.path.append("/media/50G/v/c/City_Py_OCC")

import mathutils
import c03
from bl_bmesh import BReps_triangulate_to_BMesh

def getPts(spline):
    if len(spline.bezier_points) >= 2:
        r = 4#spline.resolution_u + 1
        print('r=',r)
        segments = len(spline.bezier_points)
        if not spline.use_cyclic_u:
            segments -= 1

        points = []
        for i in range(segments):
            inext = (i + 1) % len(spline.bezier_points)

            knot1 = spline.bezier_points[i].co
            handle1 = spline.bezier_points[i].handle_right
            handle2 = spline.bezier_points[inext].handle_left
            knot2 = spline.bezier_points[inext].co

            _points = mathutils.geometry.interpolate_bezier(knot1, handle1, handle2, knot2, r)
            points.extend(_points)

            #  dbg display
            # for p in _points:
                # bpy.ops.mesh.primitive_cube_add(radius=0.01,location=p)


    return points


def dbgPrintArray(icrvsV):
    # print(crsV)
    for c in icrvsV:
        print('curve:')#,c)#list(c))
        for pt in c:
            print(round(pt.x,3),round(pt.y,3),round(pt.z,3))


def prepare_Discr_Curves(inPtss,tolDist=0.01):

    def isNearestThan(ptA,ptB,dist):
        diff=ptA - ptB
        print('compare:',ptA,ptB,diff.length)
        res = diff.length < dist
        print(res)
        return diff.length < dist

    print('onEnter:')
    l=len(inPtss)
    procPtss=[]
    print('procPtss:')
    dbgPrintArray(procPtss)

    z=inPtss.pop(0)
    print('z=',z)
    procPtss.append(z)#inPtss.pop(0))
    print('procPtss:')
    dbgPrintArray(procPtss)

    print('-----------------------')
    print('in')
    dbgPrintArray(inPtss)
    print('proc')
    dbgPrintArray(procPtss)


    while inPtss:

        if l == len(inPtss):
            print('no matching curve found!')
            break

        startPt=procPtss[0][0]
        endPt=procPtss[-1][-1]
        l=len(inPtss)

        print('iter -----------------------')
        print('in')
        dbgPrintArray(inPtss)
        print('proc')
        dbgPrintArray(procPtss)

        for i in range(0,len(inPtss)):
            currPtss=inPtss[i]

            if isNearestThan(endPt, currPtss[0], tolDist):
                procPtss.append(inPtss.pop(i))
                break

            if isNearestThan(endPt, currPtss[-1], tolDist):
                cc=inPtss.pop(i)
                cc.reverse()
                procPtss.append(cc)
                break

            if isNearestThan(startPt, currPtss[0], tolDist):
                procPtss.insert(0,inPtss.pop(i).reverse())
                break

            if isNearestThan(startPt, currPtss[-1], tolDist):
                procPtss.insert(0,inPtss.pop(i))
                break

    print('onExit -----------------')
    dbgPrintArray(procPtss)
    for i in range(0,len(procPtss)-1):
        procPtss[i][-1]=procPtss[i+1][0]
    procPtss[-1][-1]=procPtss[0][0]
    return procPtss


if __name__ == '__main__':

    crvs=[]
    crvsV=[]
    for i in range(0,len(bpy.data.curves)):
        ptsVec=getPts(bpy.data.curves[i].splines[0])
        ptsTup=[(pt.x,pt.y,pt.z) for pt in ptsVec]
        crvs.append(ptsTup)
        crvsV.append(ptsVec)

        # print('ptsTup=',len(ptsTup),ptsTup)


    pc=prepare_Discr_Curves(crvsV)

    for c in pc:
        print('curve:',list(c))

    # map two-dim array
    pct=[[(pt.x,pt.y,pt.z) for pt in ptsV] for ptsV in pc]


    crvsP=[
    [(0,0,0),(5,5,0),(10,0,0)],
    [(10,0,0),
    (5,-5,0),(0,0,0)]
    ]

    crvsP=crvs

    # print(crvs)
    # r=crvsP[0].reverse()
    crvs[1][-1] = crvs[0][0]
    # crvsP[0]=r
    # print('crvs[0]=',crvs[0])
    # print('crvs[1]=',crvs[1])

    # crvs=[c03.toShapes(p) for p in crvsP]
    crvs=[c03.toShapes(p) for p in pct]

    # crvsFlat=[el for crv in crvs for el in crv]  # flatten
    crvsFlat=[el for crv in crvs for el in crv]  # flatten

    f=c03.makeFilling(crvsFlat)#,dbgOutput=True)
    BReps_triangulate_to_BMesh([f.Face()])

    # bpy.ops.mesh.primitive_cube_add(radius=0.01)
