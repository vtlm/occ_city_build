__author__ = 'nezx'

from random import randint, random
import c03
from c03 import makeWire
from OCC.BRepFill import brepfill_Shell
from OCC.TopoDS import topods_Wire
import display
from BRep_funx import BRep_triangulate
from funx import createEntry, appendEntry

class House(object):
    def __init__(self, baseOutline, levelH=3, levelsNumbBnds=(1,5)):
        self.baseOutline=baseOutline
        self.levelH=levelH
        self.levelsNumber=randint(levelsNumbBnds[0],levelsNumbBnds[1])
        self.levelsOutlines=[baseOutline]
        self.build()
        self.display()

    def build(self):
        self.levelsShapes=[]
        self.createOutlines()
        for i in range(0,self.levelsNumber):
            self.levelsShapes.append(self.buildLevel(i))

    def riseOutline(self,outLine,l):
        return [(pt[0],pt[1],pt[2]+l) for pt in outLine]

    def createOutlines(self):
        for i in range(0,self.levelsNumber):
            newOutline=self.riseOutline(self.levelsOutlines[-1],self.levelH)
            self.levelsOutlines.append(newOutline)

    # def buildLevel(self,numb):
    #     w1=makeWire(self.levelsOutlines[numb])
    #     w2=makeWire(self.levelsOutlines[numb+1])
    #     sh = brepfill_Shell(topods_Wire(w1.Shape()), topods_Wire(w2.Shape()))
    #
    #     if not display.OCC_FrontEnd:
    #         # BRep_triangulate_to_BMesh(sh,textureName='red_bricks_001')
    #         BRep_triangulate_to_BMesh(sh,objectName='house',textureName='wall_001')

    def buildLevel(self,numb):
        w1=makeWire(self.levelsOutlines[numb])
        w2=makeWire(self.levelsOutlines[numb+1])
        sh = brepfill_Shell(topods_Wire(w2.Shape()), topods_Wire(w1.Shape()))
        return sh

        # if not display.OCC_FrontEnd:
        #     # BRep_triangulate_to_BMesh(sh,textureName='red_bricks_001')
        #     BRep_triangulate_to_BMesh(sh,objectName='house',textureName='wall_001')

    def display(self):
        if not display.OCC_FrontEnd:
            BReps_triangulate_to_BMesh(self.levelsShapes,objectName='house',textureName='wall_001')


typesTextures={
    'basement':'sand_001',
    'house':'wall_001',
    'top':'trott_tiles_001',
}

def getTextureName(tName):
    textrName=typesTextures.get(tName)
    if textrName == None:
        textrName='colorGrid'
    return textrName


class HouseDump(object):
    def __init__(self,baseOutline, levelH=3, levelsNumbBnds=(1,5),typeN=''):
        self.baseOutline=baseOutline
        self.typeN=typeN
        levelsNumber=randint(levelsNumbBnds[0],levelsNumbBnds[1])
        self.risedOutline=[(pt[0],pt[1],pt[2]+levelH*levelsNumber) for pt in baseOutline]
        self.shell=c03.makeShell(baseOutline,self.risedOutline)
        self.topFace=c03.makeFace(self.risedOutline)

    def display(self):
        if display.OCC_FrontEnd:
            display.Display(self.shell)
            display.Display(self.topFace.Face())
        else:
            BReps_triangulate_to_BMesh([self.shell],objectName='house',textureName=getTextureName(self.typeN))
            BReps_triangulate_to_BMesh([self.topFace.Face()],objectName='house',textureName='road_001')

            # m=BRep_triangulate(self.shell)
            # m.append(BRep_triangulate(self.topFace.Face()))

            # return {'walls':BRep_triangulate(self.shell),'roof':BRep_triangulate(self.topFace.Face())}

            r=[]
            appendEntry(r,'tris','walls',BRep_triangulate(self.shell))
            appendEntry(r,'tris','roof',BRep_triangulate(self.topFace.Face()))
            return r

    def export(self):
            r=[]
            appendEntry(r,'material','material','wall_001')
            appendEntry(r,'tris','walls',BRep_triangulate(self.shell))
            appendEntry(r,'material','material','road_001')
            appendEntry(r,'tris','roof',BRep_triangulate(self.topFace.Face()))
            return r


class CompoundHouse(object):
    def __init__(self,baseOutline):
        self.baseOutline=baseOutline
        self.levels=[]

        highestPoint=max(baseOutline,key=lambda x:x.Z())
        lpt=min(baseOutline,key=lambda x:x.Z())

        basementH=highestPoint.Z()-lpt.Z()
        self.baseOutlineT=[(pt.X(),pt.Y(),lpt.Z()) for pt in baseOutline]
        bsm=HouseDump(self.baseOutlineT,levelH=basementH,levelsNumbBnds=(1,1),typeN='basement')
        self.levels.append(bsm)

        scaleFt=0.9+random()*0.2
        ho=c03.scale(bsm.risedOutline,scaleF=(scaleFt,scaleFt))
        ha=HouseDump(ho,levelsNumbBnds=(1,2),typeN='house')
        self.levels.append(ha)

        scaleFt=0.7+random()*0.3
        ho=c03.scale(ha.risedOutline,scaleF=(scaleFt,scaleFt))
        ha=HouseDump(ho,levelsNumbBnds=(3,8),typeN='house')
        self.levels.append(ha)

        if random()<0.3:
            scaleFt=0.2+random()*0.4
            ho=c03.scale(ha.risedOutline,scaleF=(scaleFt,scaleFt))
            ha=HouseDump(ho,levelH=randint(2,4),levelsNumbBnds=(1,1),typeN='top')
            self.levels.append(ha)

    def display(self):
        for l in self.levels:
            l.display()

    def export(self):
        self.comps=[]

        for l in self.levels:
            appendEntry(self.comps,'data','houseLevel',l.export())

        return createEntry('data','CompoundHouse',self.comps)
