from OCC.gp import gp_Vec

__author__ = 'nezx'
import c03
import display
# if not display.OCC_FrontEnd:
from BRep_funx import BRep_triangulate
from OCC.gp import gp_Pnt, gp_Dir
from OCC.GC import GC_MakeLine
from OCC.BRepBuilderAPI import BRepBuilderAPI_GTransform
from OCC.BRepFill import brepfill_Shell
from OCC.BRepPrimAPI import BRepPrimAPI_MakeCylinder
from OCC.TopoDS import topods_Wire
from OCC.GProp import GProp_PGProps
from OCC.gp import gp_GTrsf

from shapely.geometry import Polygon
from shapely.affinity import scale

from house import CompoundHouse
from subdiv import subDiv, getBoundary
from funx import createEntry, appendEntry
from parabols import makeDome, copyTo

tex_colors = {
    'bordersVertical': ('bw_stripe', 'YELLOW', False),
    'bordersHorizontal': ('bw_stripe', 'GREEN', True),
    'trottoirs': ('tiles_001', 'YELLOW', True)
}


class RoadBorder(object):

    def __init__(self, baseOutline, dir=-1):
        self.baseOutline = baseOutline
        self.dir = dir
        self.geoms = {}
        self.geoms['bordersVertical'] = []
        self.geoms['bordersHorizontal'] = []
        self.geoms['trottoirs'] = []
        self.geoms['grassy'] = []
        self.geoms['innerPatches'] = []
        self.create(c03.toShapes(self.baseOutline))

    def create(self, re):
        bordH = 0.5
        bordScl = 1 + 0.02 * self.dir
        trottScl = 1 + 0.16 * self.dir
        upper = c03.translShapes(re, gp_Vec(0, 0, bordH))
        reSc = c03.scaleShapes(upper, bordScl)
        self.reSc2 = c03.scaleShapes(upper, trottScl)

        w0 = c03.makeWire(re)
        w1 = c03.makeWire(upper)
        w2 = c03.makeWire(reSc)
        w3 = c03.makeWire(self.reSc2)

        # display.DisplayColored(w1.Shape(),'RED')
        # display.DisplayColored(w2.Shape(),'RED')
        # display.DisplayColored(w3.Shape(),'RED')
        # self.geoms['innerPatches'].append(reSc)

        sh = brepfill_Shell(topods_Wire(w1.Shape()), topods_Wire(w0.Shape()))
        # display.DisplayColored(sh, color='GREEN')
        self.geoms['bordersVertical'].append(sh)

        sh = brepfill_Shell(topods_Wire(w1.Shape()), topods_Wire(w2.Shape()))
        # display.DisplayColored(sh, color='GREEN')
        self.geoms['bordersHorizontal'].append(sh)

        sh = brepfill_Shell(topods_Wire(w3.Shape()), topods_Wire(w2.Shape()))
        # display.DisplayColored(sh, color='GREEN')
        self.geoms['trottoirs'].append(sh)

        # f=c03.makeFilling(reSc)
        # # DisplayColored(f.Face())
        # geoms['lArea'].append(f)

    def getSidewalkInnerOutline(self):
        return self.reSc2

    def display(self):

        ress = []

        def displayFor(key):
            gs = self.geoms[key]
            for g in gs:
                if display.OCC_FrontEnd:
                    display.DisplayColored(g, tex_colors.get(key)[1])
                else:
                    # BRep_triangulate_to_BMesh(g,textureName='grass_001')
                    BReps_triangulate_to_BMesh([g], objectName=key, textureName=tex_colors.get(key)[
                                               0], reTestNormals=tex_colors.get(key)[2])
                    ress.extend(BRep_triangulate(g))

        keys = tex_colors.keys()
        for key in keys:
            displayFor(key)

        # print(list(ress))

        return ress

    def export(self):

        ress = []

        def exportFor(key):
            gs = self.geoms[key]
            for g in gs:
                # BReps_triangulate_to_BMesh([g], objectName=key, textureName=tex_colors.get(key)[
                #                            0], reTestNormals=tex_colors.get(key)[2])
                return BRep_triangulate(g, reTestNormals=tex_colors.get(key)[2])

        keys = tex_colors.keys()
        for key in keys:
            # print('key=',key)
            tris=exportFor(key)
            appendEntry(ress,'material','material',tex_colors.get(key)[0])
            appendEntry(ress,'tris',key,tris)

        return ress

        # gs = self.geoms['bordersVertical']
        # for g in gs:
        #     if display.OCC_FrontEnd:
        #         display.DisplayColored(g,'YELLOW')
        #     else:
        #         # BRep_triangulate_to_BMesh(g,textureName='grass_001')
        #         BRep_triangulate_to_BMesh(g,textureName='bw_stripe',reTestNormals=False)
        #
        # gs = self.geoms['bordersHorizontal']
        # for g in gs:
        #     if display.OCC_FrontEnd:
        #         display.DisplayColored(g,'GREEN')
        #     else:
        #         # BRep_triangulate_to_BMesh(g,textureName='grass_001')
        #         BRep_triangulate_to_BMesh(g,textureName='bw_stripe')#,reTestNormals=False)
        #
        # gs = self.geoms['trottoirs']
        # for g in gs:
        #     if display.OCC_FrontEnd:
        #         display.DisplayColored(g,'YELLOW')
        #     else:
        #         # BRep_triangulate_to_BMesh(g,textureName='grass_001')
        #         BRep_triangulate_to_BMesh(g,textureName='trott_tiles_001')
        #
        #     # gs = self.geoms['lArea']
        #     # for g in gs:
        #     #     BRep_triangulate_to_BMesh(g.Face(),textureName='sand_001')


class CityBlock(object):
    """docstring for """
    def __init__(self, baseOutlineEdges, baseOutlinePts, offsetDir=-1):
        self.baseOutlineEdges = baseOutlineEdges
        self.baseOutlinePts = baseOutlinePts
        self.offsetDir = offsetDir
        self.hShapes=[]

    def create(self):
        self.roadBorder=RoadBorder(self.baseOutlineEdges,self.offsetDir)
        # blocks.append(blo)
        outl=self.roadBorder.getSidewalkInnerOutline()

        if self.offsetDir == -1:
            # fl=c03.makeFilling(outl)
            # Display(fl.Face())
            #
            # ffaces.append(fl.Face())

            self.mainPatch=ShelledPatch(outl) # fillWithShells(outl)
            allFaces=self.mainPatch.getAllFaces()#shells[0].shell

            ds = [(gd.X(), gd.Y(), gd.Z()) for gd in self.baseOutlinePts]

            allFacesAdaptors=[c03.BRepFace_to_GeomAdaptor(x) for x in allFaces]

            # lb=extrs[i][1][2]
            p0 = Polygon(ds)
            p=scale(p0, xfact=0.75, yfact=0.75)
            # print(p.area)
            # print(p)
            ps = subDiv(p)
            self.houses=[]
            for p in ps:
                # print(p.area)
                # print(list(p.boundary.coords))
                p2 = scale(p, xfact=0.85, yfact=0.85)
                pl = []
                cpts=getBoundary(p2)
                pl.extend(cpts)#p2.boundary.coords)

                toPrjPts=[gp_Pnt(c[0],c[1],100) for c in pl]
                prjdPts=c03.projectPointsOnSurfaces(toPrjPts,gp_Dir(0,0,-1),allFacesAdaptors)

                cont=GProp_PGProps()
                for p in prjdPts:
                    cont.AddPoint(p)

                cm=cont.CentreOfMass()

                # print(cont.CentreOfMass())
                # l=GC_MakeLine(cm,gp_Dir(0,0,1))
                # display.DisplayColored(l.Value(),'RED')

                c=BRepPrimAPI_MakeCylinder(3,10)
                # display.DisplayColored(c.Shape(),'WHITE')
                gt=gp_GTrsf()
                # gt.SetTranslationPart(gp_Vec(cm.XYZ()))
                gt.SetTranslationPart(cm.XYZ())
                t=BRepBuilderAPI_GTransform(gt)
                t.Perform(c.Shape())
                display.DisplayColored(t.Shape(),'WHITE')

                do=makeDome()
                d=copyTo(do,cm.X(),cm.Y(),cm.Z()+10)
                display.DisplayColored(d.Shape(),'RED')


                self.hShapes.extend([t.Shape(),d.Shape()])
                # self.hShapes.extend([d.Shape()])

                # self.houses.append(CompoundHouse(prjdPts))
                # houses_tris.extend(c.tris)

                # appendEntry(cdmp,'house','house',c.comps)
        else:
            self.gProps = c03.getConstructedSurfaceGProps(self.roadBorder.getSidewalkInnerOutline())
            self.outerGrass=ShellArea(self.roadBorder.getSidewalkInnerOutline(),1.2,self.gProps.CentreOfMass())

            pass

    def display(self):
        self.roadBorder.display()
        if self.offsetDir == -1:
            self.mainPatch.display()
            for h in self.houses:
                h.display()
        else:
            self.outerGrass.display()

    def export(self):
        acc=[]
        appendEntry(acc,'data','RoadBorder',self.roadBorder.export())
        if self.offsetDir == -1:
            for h in self.houses:
                acc.append(h.export())
            appendEntry(acc,'material','material','grass_001')
            acc.append(self.mainPatch.export())
            for s in self.hShapes:
                appendEntry(acc,'tris','walls3',BRep_triangulate(s))
        else:
            appendEntry(acc,'material','material','grass_001')
            acc.append(self.outerGrass.export())
        return createEntry('data','CityBlock',acc)




class ShellArea(object):

    def __init__(self, baseOutline, scaleS, transfCenter):
        self.baseOutline = baseOutline
        self.build(scaleS, transfCenter)

    def build(self, scaleS, transfCenter):
        self.scaledOutline = c03.scaleShapes(
            self.baseOutline, scaleS, transfCenter)
        wb = c03.makeWire(self.baseOutline)
        ws = c03.makeWire(self.scaledOutline)
        self.shell = brepfill_Shell(topods_Wire(
            wb.Shape()), topods_Wire(ws.Shape()))

    def getAllFaces(self):
        return c03.getAllFaces(self.shell)

    def display(self):
        if display.OCC_FrontEnd:
            display.Display(self.shell)

    def export(self):
        return createEntry('tris','ShellArea',BRep_triangulate(self.shell))


class ShelledPatch(object):

    def __init__(self, baseOutline):
        self.baseOutline = baseOutline
        self.gProps = c03.getConstructedSurfaceGProps(baseOutline)

        self.shells = []
        shapeToScale = self.baseOutline

        for i in range(0, 3):
            scShell = ShellArea(shapeToScale, 0.7, self.gProps.CentreOfMass())
            self.shells.append(scShell)
            shapeToScale = scShell.scaledOutline

        # print('makeFilling for', self)
        self.fill = c03.makeFilling(shapeToScale)

    def getAllFaces(self):
        allFaces = [self.fill.Face()]
        for s in self.shells:
            allFaces.extend(s.getAllFaces())
        return allFaces

    def display(self):
        for s in self.shells:
            s.display()
        display.Display(self.fill.Face())

    def export(self):
        acc=[createEntry('tris','ShellArea',BRep_triangulate(self.fill.Face()))]
        for s in self.shells:
            acc.append(s.export())
        return createEntry('data','ShelledPatch',acc)


# def fillWithShells(shapes):
#
#     sp = ShelledPatch(shapes)
#     # sp.display()
#     return sp

    # while True:
    #     nextShell=scaleShapes(shapes,0.7)
    #     bf=makeFilling(nextShell)
    #     gp = GProp_GProps()
    #     brepgprop_SurfaceProperties(bf.Face(), gp)
    #     cm = gp.Mass()
    #
    #     if cm > 100:
    #         w0=makeWire(shapes)
    #         w1=makeWire(nextShell)
    #         sh=brepfill_Shell(topods_Wire(w0.Shape()),topods_Wire(w1.Shape()))
    #         display.Display(sh)
    #         shapes=nextShell
    #     else:
    #         break
