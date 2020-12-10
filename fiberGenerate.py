#-*-coding: UTF-8-*-
######################################################################################
#  Author: Junjun Guo
#  E-mail: guojj@tongji.edu.cn/guojj_ce@163.com
#    Date: 05/02/2020
#  Environemet: Successfully excucted in python 3.6
######################################################################################
# import necessary modules
import matplotlib.pyplot as plt
import numpy as np
from scipy.linalg import solve
import math
import time
import pygmsh
import meshio
import matplotlib.tri as tri
from pointInPolygon import is_in_2d_polygon
########################################################################################################################
########################################################################################################################
class CircleSection():
    """
    Circle section fibers generate
    Input: ax-axes
          d0-concreate cover length (m)
          outD-outside diameter (m)
          inD-inner diameter (m)
          if inD==None,the section is solid circle, otherwise is torus
    #######################---solid section circle example---#########################
    from fiberGenerate import CircleSection
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(5, 5))
    ax = fig.add_subplot(111)
    outbarD = 0.03  # outside bar diameter
    outbarDist = 0.15  # outside bar space
    d0 = 0.06  # the thinckness of the cover concrete
    eleSize = 0.15  # the size of core concrete fiber
    coverSize = 0.15  # the size of cover concrete fiber
    outD = 3  # the diameter of the outside circle
    circleInstance = CircleSection(ax, d0, outD)  # call the circle section generate class
    circleInstance.initSectionPlot()  # plot profile of the circle
    coreFiber = circleInstance.coreMesh(eleSize)  # generate core concrete fiber elements [(x1,y1,area1),...]
    coverFiber = circleInstance.coverMesh(coverSize)  # generate cover concrete fiber elements [(x1,y1,area1),...]
    barFiber = circleInstance.barMesh(outbarD, outbarDist)  # generate the bar fiber elements [(x1,y1,area1),...]
    plt.show()
    #######################---torus section example---#########################
    from fiberGenerate import CircleSection
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(5, 5))
    ax = fig.add_subplot(111)
    outbarD = 0.03  # outside bar diameter
    outbarDist = 0.15  # outside bar space
    inBarD = 0.03  # inside bar diameter
    inBarDist = 0.15  # inside bar space
    d0 = 0.1  # the thinckness of the cover concrete
    coreSize = 0.15  # the size of core concrete fiber
    coverSize = 0.15  # the size of cover concrete fiber
    outD = 3  # the diameter of the outside circle
    inD = 1  # the diameter of the inner circle
    circleInstance = CircleSection(ax, d0, outD, inD)  # call the circle section generate class
    circleInstance.initSectionPlot()  # plot profile of the circle
    coreFiber = circleInstance.coreMesh(coreSize)  # generate core concrete fiber elements
    coverFiber = circleInstance.coverMesh(coverSize)  # generate cover concrete fiber elements
    barFiber = circleInstance.barMesh(outbarD, outbarDist, inBarD, inBarDist)  # generate the bar fiber elements
    plt.show()
    """
    ####################################################
    def __init__(self, coverThick, outDiameter, innerDiameter=None):
        """
        Initialize the class
        """
        self.coverThick = coverThick
        self.outDiameter = outDiameter
        self.innerDiameter = innerDiameter
    ####################################################
    def initSectionPlot(self):
        """
        Plot the original section
        """
        xListPlot = []
        yListPlot = []
        theta = np.arange(0, 2 * np.pi, 0.01)
        outxList = (self.outDiameter / 2.0) * np.cos(theta)
        outyList = (self.outDiameter / 2.0) * np.sin(theta)
        xListPlot.append(outxList)
        yListPlot.append(outyList)
        if self.innerDiameter != None:
            inxList = (self.innerDiameter / 2.0) * np.cos(theta)
            inyList = (self.innerDiameter / 2.0) * np.sin(theta)
            xListPlot.append(inxList)
            yListPlot.append(inyList)
        return xListPlot,yListPlot
    ####################################################
    def _triEleInfo(self,points, triangles):
        """
        Calculate the area and the centroid coordinates of triangle element
        Input：points-vertex of triangel element[[x1,y1,Z1],[x2,y2,Z2]]
             triangles-triangle element list[[I1,J1,K1],[I2,J2,K2]]
        Output：
			inFoList:fiber element information [(xc1,yc1,area1),(xc2,yc2,area2)]
        """
        inFoList = []
        for each in triangles:
            I, J, K = each[0], each[1], each[2]
            x1 = points[I][0]
            y1 = points[I][1]
            x2 = points[J][0]
            y2 = points[J][1]
            x3 = points[K][0]
            y3 = points[K][1]
            area = 0.5 * (x1 * y2 - x2 * y1 + x2 * y3 - x3 * y2 + x3 * y1 - x1 * y3)
            xc = (x1 + x2 + x3) / 3.0
            yc = (y1 + y2 + y3) / 3.0
            inFoList.append((xc, yc, area))
        return inFoList
    ####################################################
    def coreMesh(self,eleSize):
        """
        Core concrete fiber generate
        Input: eleSize- fiber element size
        Output: coreFiberInfo:core concrete fiber elment informaiton [(xc1,yc1,area1),(xc2,yc2,area2)]
        """
        outDiameterNew = self.outDiameter - self.coverThick * 2.0
        if self.innerDiameter != None:
            innerDiameterNew = self.innerDiameter + self.coverThick * 2.0
            geom = pygmsh.opencascade.Geometry()
            diskOut = geom.add_disk([0.0, 0.0, 0.0], outDiameterNew/2.0, radius1=None, char_length=eleSize)
            diskInner = geom.add_disk([0.0,0.0, 0.0], innerDiameterNew/2.0, radius1=None, char_length=eleSize)
            geom.boolean_difference([diskOut], [diskInner])
            mesh = pygmsh.generate_mesh(geom)
            points=mesh.points
            triangles=mesh.cells[-1].data
            coreFiberInfo = self._triEleInfo(points, triangles)
        else:
            geom = pygmsh.opencascade.Geometry()
            disk = geom.add_disk([0.0, 0.0, 0.0], outDiameterNew / 2.0, radius1=None, char_length=eleSize)
            mesh = pygmsh.generate_mesh(geom)
            points = mesh.points
            triangles = mesh.cells[-1].data
            coreFiberInfo = self._triEleInfo(points, triangles)
        return coreFiberInfo,points,triangles
    ####################################################
    def _coverDivide(self, coverSize, pos="out"):
        """
        Cover concrete fiber generate
        coverSize-fiber size
        pos-outSize cover("out"),inner cover("in)"
        """
        if pos == "out":
            D = self.outDiameter
            DNew = self.outDiameter - self.coverThick * 2.0
            circumLength = np.pi * self.outDiameter
            Area = (np.pi * self.outDiameter ** 2) / 4.0
            NewArea = (np.pi * DNew ** 2) / 4.0
            nCover = int(circumLength / coverSize)
            coverArea = (Area - NewArea) / nCover
            R = self.outDiameter / 2.0
            NewR = DNew / 2.0
        elif pos == "in":
            D = self.innerDiameter
            DNew = self.innerDiameter + self.coverThick * 2.0
            circumLength = np.pi * D
            Area = (np.pi * D ** 2) / 4.0
            NewArea = (np.pi * DNew ** 2) / 4.0
            nCover = int(circumLength / coverSize)
            coverArea = (NewArea - Area) / nCover
            R = self.innerDiameter / 2.0
            NewR = DNew / 2.0
        else:
            print("Please select pos=out or pos=in!")
        Angle = 2 * np.pi / nCover
        NodeList = [(R * np.cos(Angle * i1), R * np.sin(Angle * i1)) for i1 in range(nCover)]
        NewNodeList = [(NewR * np.cos(Angle * i2), NewR * np.sin(Angle * i2)) for i2 in range(nCover)]
        fiberNCover = nCover
        fiberAngle = (2 * np.pi) / fiberNCover
        FiberRadius = (D + DNew) / 4.0
        FiberXList = [FiberRadius * np.cos((2 * i3 - 1) * 0.5 * fiberAngle) for i3 in range(1, fiberNCover + 1)]
        FiberYList = [FiberRadius * np.sin((2 * i4 - 1) * 0.5 * fiberAngle) for i4 in range(1, fiberNCover + 1)]
        coverFiberInfo = [(xc, yc, coverArea) for xc, yc in zip(FiberXList, FiberYList)]
        return coverFiberInfo, FiberXList, FiberYList, NodeList, NewNodeList
    ####################################################

    def coverMesh(self, coverSize):
        """
        Cover concrete mesh
        Input:
            coverSize: cover concrete fiber size
        Output:
            coverFiberInfo: cover fiber information [(xc1,yc1,area1),(xc2,yc2,area2)]
        """
        coverFiberInfo = None
        xListPLot = []
        yListPlot = []
        xBorderPlot = []
        yBorderPlot = []
        outCoverFiberInfo, outFiberXList, outFiberYList, outNodeList, \
            outNewNodeList = self._coverDivide(coverSize,pos="out")
        coverFiberInfo = outCoverFiberInfo
        borderOutNodeList = outNewNodeList
        borderOutNodeList.append(outNewNodeList[0])
        xBorderPlot.append([each1[0] for each1 in borderOutNodeList])
        yBorderPlot.append([each2[1] for each2 in borderOutNodeList])
        # self.ax.scatter(outFiberXList,outFiberYList,s=10,c="k",zorder = 2)
        for i5 in range(len(outNodeList)):
            xList = [outNodeList[i5][0], outNewNodeList[i5][0]]
            yList = [outNodeList[i5][1], outNewNodeList[i5][1]]
            xListPLot.append(xList)
            yListPlot.append(yList)
        if self.innerDiameter != None:
            inDNew = self.innerDiameter + 2.0 * self.coverThick
            inCoverFiberInfo, inFiberXList, inFiberYList, inNodeList, inNewNodeList \
                = self._coverDivide(coverSize, pos="in")
            coverFiberInfo = coverFiberInfo + inCoverFiberInfo
            borderInNodeList = inNewNodeList
            borderInNodeList.append(inNewNodeList[0])
            xBorderPlot.append([each3[0] for each3 in borderInNodeList])
            yBorderPlot.append([each4[1] for each4 in borderInNodeList])
            # self.ax.scatter(inFiberXList,inFiberYList,s=10,c="k",zorder = 2)
            for i5 in range(len(inNodeList)):
                xList = [inNodeList[i5][0], inNewNodeList[i5][0]]
                yList = [inNodeList[i5][1], inNewNodeList[i5][1]]
                xListPLot.append(xList)
                yListPlot.append(yList)
        return coverFiberInfo,xListPLot,yListPlot,xBorderPlot,yBorderPlot
    ####################################################
    def _barDivide(self, barD, barDist, pos="out"):
        """
        Bar fiber divide
        Input：barD-bar diameter (m)
             barDist-bar space (m)
        """
        newR=None
        area = (np.pi * barD ** 2) / 4.0
        if pos == "out":
            newR = (self.outDiameter - 2.0 * self.coverThick) / 2.0-barD/2.0
        elif pos == "in":
            newR = (self.innerDiameter + 2.0 * self.coverThick)/2.0 +barD/2.0
        circumLength = 2 * np.pi * newR
        nBar = int(circumLength / barDist)
        angle = (2 * np.pi) / nBar
        fiberXList = [newR * np.cos(angle * i1) for i1 in range(1, nBar + 1)]
        fiberYList = [newR * np.sin(angle * i2) for i2 in range(1, nBar + 1)]
        barFiberInfo = [(xb, yb, area) for xb, yb in zip(fiberXList, fiberYList)]
        return barFiberInfo, fiberXList, fiberYList
    ####################################################
    def barMesh(self, outBarD, outBarDist, inBarD=None, inBarDist=None):
        """
        Bar mesh
        Input:
            outBarD: bar diameter in outside cover zone
            outBarDist: bar space in outside cover zone
            inBarD: bar diameter in inner cover zone
            inBarDist: bar space in inner cover zone
        Output:
            barFiberInfo:bar fiber infomation [(xc1,yc1,area1),(xc2,yc2,area2)]
        """
        barFiberInfo = None
        barXListPlot = []
        barYListPlot = []
        outFiberInfo, outFiberXList, outFiberYList = self._barDivide(outBarD, outBarDist, pos="out")
        barFiberInfo = outFiberInfo
        barXListPlot.append(outFiberXList)
        barYListPlot.append(outFiberYList)
        if self.innerDiameter != None:
            inFiberInfo, inFiberXList, inFiberYList = self._barDivide(inBarD, inBarDist, pos="in")
            barFiberInfo = barFiberInfo + inFiberInfo
            barXListPlot.append(inFiberXList)
            barYListPlot.append(inFiberYList)
        return barFiberInfo,barXListPlot,barYListPlot
########################################################################################################################
########################################################################################################################
class PolygonSection():
    """
	Polygon section fiber mesh (bar, core conrete and cover concrete)
	###########################---Polygon section example---######################################
    from fiberGenerate import PolygonSection
    from fiberGenerate import figureSize
    import matplotlib.pyplot as plt
    outSideNode = {1: (3.5, 3), 2: (1.5, 5), 3: (-1.5, 5), 4: (-3.5, 3), 5: (-3.5, -3), 6: (-1.5, -5), 7: (1.5, -5),
                   8: (3.5, -3)}
    outSideEle = {1: (1, 2), 2: (2, 3), 3: (3, 4), 4: (4, 5), 5: (5, 6), 6: (6, 7), 7: (7, 8), 8: (8, 1)}
    w, h = figureSize(outSideNode)
    fig = plt.figure(figsize=(w,h))
    ax = fig.add_subplot(111)
    coverThick = 0.06  # the thinck of the cover concrete
    coreSize = 0.2  # the size of the core concrete fiber elements
    coverSize = 0.3  # the size of the cover concrete fiber elements
    outBarDist = 0.2  # outside bar space
    outBarD = 0.032  # outside bar diameter
    sectInstance = PolygonSection(ax, outSideNode, outSideEle)
    sectInstance.sectPlot()
    outLineList = sectInstance.coverLinePlot(coverThick)
    coreFiber = sectInstance.coreMesh(coreSize, outLineList)
    coverFiber = sectInstance.coverMesh(coverSize, coverThick)
    barFiber = sectInstance.barMesh(outBarD, outBarDist,coverThick)
    plt.show()
    ###########################---PolygonHole section example---######################################
    from fiberGenerate import PolygonSection
    from fiberGenerate import figureSize
    import matplotlib.pyplot as plt
    outSideNode = {1: (3.5, 3), 2: (1.5, 5), 3: (-1.5, 5), 4: (-3.5, 3), 5: (-3.5, -3), 6: (-1.5, -5), 7: (1.5, -5),
                   8: (3.5, -3)}
    outSideEle = {1: (1, 2), 2: (2, 3), 3: (3, 4), 4: (4, 5), 5: (5, 6), 6: (6, 7), 7: (7, 8), 8: (8, 1)}
    inSideNode = [
        {1: (1.9, 2.4), 2: (1.1, 3.2), 3: (-1.1, 3.2), 4: (-1.9, 2.4), 5: (-1.9, -2.4), 6: (-1.1, -3.2), 7: (1.1, -3.2),
         8: (1.9, -2.4)}]
    inSideEle = [{1: (1, 2), 2: (2, 3), 3: (3, 4), 4: (4, 5), 5: (5, 6), 6: (6, 7), 7: (7, 8), 8: (8, 1)}]
    w,h=figureSize(outSideNode)
    fig = plt.figure(figsize=(w,h))
    ax = fig.add_subplot(111)
    coverThick = 0.06  # the thinck of the cover concrete
    coreSize = 0.2  # the size of the core concrete fiber elements
    coverSize = 0.3  # the size of the cover concrete fiber elements
    outBarDist = 0.2  # outside bar space
    outBarD = 0.032  # outside bar diameter
    inBarD = 0.032
    inBarDist = 0.2
    sectInstance = PolygonSection(ax, outSideNode, outSideEle, inSideNode, inSideEle)
    sectInstance.sectPlot()
    outLineList = sectInstance.coverLinePlot(coverThick)
    inLineList = sectInstance.innerLinePlot(coverThick)
    coreFiber = sectInstance.coreMesh(coreSize, outLineList, inLineList)
    coverFiber = sectInstance.coverMesh(coverSize, coverThick)
    barFiber = sectInstance.barMesh(outBarD, outBarDist,coverThick, inBarD, inBarDist)
    plt.show()
    ###########################---PolygonTwoHole section example---######################################
    from fiberGenerate import PolygonSection
    from figerGenerate import figureSize
    import matplotlib.pyplot as plt

    outSideNode = {1: (4.5, 6.655), 2: (2.5, 8.655), 3: (-2.5, 8.655), 4: (-4.5, 6.655), 5: (-4.5, -6.655),
                   6: (-2.5, -8.655), 7: (2.5, -8.655),
                   8: (4.5, -6.655)}
    outSideEle = {1: (1, 2), 2: (2, 3), 3: (3, 4), 4: (4, 5), 5: (5, 6), 6: (6, 7), 7: (7, 8), 8: (8, 1)}
    inSideNode = [{1: (2.5, 5.855), 2: (1.7, 6.655), 3: (-1.7, 6.655), 4: (-2.5, 5.855), 5: (-2.5, 1.3), 6: (-1.7, 0.5),
                   7: (1.7, 0.5), 8: (2.5, 1.3)},
                  {1: (2.5, -1.3), 2: (1.7, -0.5), 3: (-1.7, -0.5), 4: (-2.5, -1.3), 5: (-2.5, -5.855),
                   6: (-1.7, -6.655), 7: (1.7, -6.655), 8: (2.5, -5.855)}]
    inSideEle = [{1: (1, 2), 2: (2, 3), 3: (3, 4), 4: (4, 5), 5: (5, 6), 6: (6, 7), 7: (7, 8), 8: (8, 1)},
                 {1: (1, 2), 2: (2, 3), 3: (3, 4), 4: (4, 5), 5: (5, 6), 6: (6, 7), 7: (7, 8), 8: (8, 1)}]
    w,h=figureSize(outSideNode)
    fig = plt.figure(figsize=(w,h))
    ax = fig.add_subplot(111)
    coverThick = 0.06  # the thinck of the cover concrete
    coreSize = 0.2  # the size of the core concrete fiber elements
    coverSize = 0.3  # the size of the cover concrete fiber elements
    outBarDist = 0.2  # outside bar space
    outBarD = 0.032  # outside bar diameter
    inBarD = 0.032
    inBarDist = 0.2
    sectInstance = PolygonSection(ax, outSideNode, outSideEle, inSideNode, inSideEle)
    sectInstance.sectPlot()
    outLineList = sectInstance.coverLinePlot(coverThick)
    inLineList = sectInstance.innerLinePlot(coverThick)
    coreFiber = sectInstance.coreMesh(coreSize, outLineList, inLineList)
    coverFiber = sectInstance.coverMesh(coverSize, coverThick)
    barFiber = sectInstance.barMesh(outBarD, outBarDist,coverThick, inBarD, inBarDist)
    plt.show()
    """

    def __init__(self, outNode, outEle, inNode=None, inEle=None):
        """
        Initialize:
        ax: axes
        outNode:outSide node dict--outSideNode={1:(3.5,3),2:(1.5,5),3:(-1.5,5),4:(-3.5,3)}
        outEle: outSide element dict (anticolckwise) outSideEle = {1: (1, 2), 2: (2, 3), 3: (3, 4), 4: (4,1)}
        inNode: innner node dict, a dict for each hole inSideNode=[{1:(1.9,2.4),2:(1.1,3.2),3:(-1.1,3.2),4:(-1.9,2.4)}]
        inEle: inner element dict, a dict for each hole --inSideEle = [{1: (1, 2), 2: (2, 3), 3: (3, 4), 4: (4, 1)}]
        """
        self.outNode = outNode
        self.outEle = outEle
        self.inNode = inNode
        self.inEle = inEle
        self.outNewNodeDict = None  # 新生成的外侧保护层混凝土线节点字典
        self.inNewNodeDict = None  # 新生成的内侧保护层混凝土线节点字典列表
    ####################################################
    def sectPlot(self):
        """
        Plot the original section
        """
        returnList = []
        outLineList = self._lineNodeList(self.outNode, self.outEle) #返回每个线单元两端节点的X，Y坐标列表[([x1,x2],[y1,y2])]
        returnList = outLineList
        if self.inNode != None:
            for eachNode, eachEle in zip(self.inNode, self.inEle):
                innerLineList= self._lineNodeList(eachNode, eachEle)#返回每个线单元两端节点的X，Y坐标列表[([x1,x2],[y1,y2])]
                returnList = returnList + innerLineList
        return returnList
    ####################################################
    def _lineNodeList(self, nodeDict, eleDict):
        """
        返回每个线单元两端节点的X，Y坐标列表[([x1,x2],[y1,y2])]
        输入：nodeDict-节点字典{1:(3.5,3),2:(1.5,5),3:(-1.5,5),4:(-3.5,3)}
             eleDict-单元及其两端节点字典，{1: (1, 2), 2: (2, 3), 3: (3, 4), 4: (4,1)}
        """
        nEle = len(eleDict)
        keysList = list(eleDict.keys())
        lineList = []
        for i1 in range(nEle):
            nodeI = eleDict[keysList[i1]][0]
            nodeJ = eleDict[keysList[i1]][1]
            nodeIx = nodeDict[nodeI][0]
            nodeIy = nodeDict[nodeI][1]
            nodeJx = nodeDict[nodeJ][0]
            nodeJy = nodeDict[nodeJ][1]
            lineList.append(([nodeIx, nodeJx], [nodeIy, nodeJy]))
        return lineList
    ####################################################
    def coverLinePlot(self, coverThick):
        """
        Plot the border line of outside cover concrete and core concrete
        Input:
            coverThick: cover thick
        Output:
            returnNodeList:the border line intersect points coordinates [(x1,y1),(x2,y2),...,(xn,yn)]
        """
        #计算分界线节点列表[(x1, y1), (x2, y2), ..., (xn, yn)]
        returnNodeList = self._middleLineNode(self.outNode, coverThick, pos="outLine")
        outNodeNewDict = {(i1 + 1): returnNodeList[i1] for i1 in range(len(returnNodeList))}
        self.outNewNodeDict = outNodeNewDict  ##外层混凝土保护层线节点字典，与外轮廓节点一一对应
        outEleDict = self.outEle
        # 返回每个线单元两端节点的X，Y坐标列表[([x1,x2],[y1,y2])]
        coverlineList = self._lineNodeList(outNodeNewDict, outEleDict)
        return returnNodeList,coverlineList
    ####################################################
    def innerLinePlot(self, coverThick):
        """
        Plot the border line of inner cover concrete and core concrete
        Input:
            coverThick--cover thick
        Output:
            innerList:border line intersect points coordinates [[(x1,y1),(x2,y2),...,(xn,yn)],...,]
        """
        if self.inNode != None:
            innerList = []
            innerListDict = []
            inlineList = []
            for eachNodeDict, eachEleDict in zip(self.inNode, self.inEle):
                #计算分界线各节点的列表[(x1,y1),(x2,y2),...,(xn,yn)]
                returnNodeList = self._middleLineNode(eachNodeDict,coverThick,pos="innerLine")
                innerList.append(returnNodeList)
                innerListDict.append({(j1 + 1): returnNodeList[j1] for j1 in range(len(returnNodeList))})
                inNodeDict = {(i1 + 1): returnNodeList[i1] for i1 in range(len(returnNodeList))}
                inEleDict = eachEleDict
                #返回每个线单元两端节点的X，Y坐标列表[([x1,x2],[y1,y2])]
                tempList = self._lineNodeList(inNodeDict, inEleDict)
                inlineList = inlineList + tempList
            self.inNewNodeDict = innerListDict
            return innerList,inlineList
    ####################################################
    def _pointToLineD(self,a,b,c,nodeIx,nodeIy,nodeJx,nodeJy):
        """
        得到一条线段垂直中线距线段距离为d的点的坐标
        输入: a,b,c直线一般方程系数 ax+by+c=0
              nodeIx,nodeIy,nodeJx,nodeJy-线段I,J段节点坐标
        输出：newNode-直线外一点坐标[(xi,yi)]
        """
        a1,b1,c1=a,b,c
        c22=(a*0.5*(nodeIy+nodeJy)-b*0.5*(nodeIx+nodeJx))
        a2,b2,c2=b,-a,c22
        A = np.array([[a1, b1], [a2, b2]])
        B = np.array([-c1, -c2])
        newNode = list(solve(A, B))
        return newNode
    ####################################################
    def _interNodeCoord(self,nodeDict,coverThick,pos):
        """
        计算多边形整体缩放后的交点坐标
        输入:nodeDict-节点字典 {1:(2.3,4.3)}
             coverThick-保护层厚度
             pos-外侧分界线（"outLine"),内侧分界线("innerLine")
        输出：NodeList-新节点坐标列表 [(x1,y1),(x2,y2),...,(xn,yn)]
        """
        closedNodeValues = list(nodeDict.values())
        closedNodeValues.append(closedNodeValues[0])   #闭合多边形节点坐标[(x0,y0),(x1,y1),...,(x0,y0)]
        NodeKeys = list(nodeDict.keys())
        NodeKeys.append(NodeKeys[0])
        NodeKeys.append(NodeKeys[1])
        IterNode = []
        for i1 in range(len(nodeDict)):
            IterNode.append((NodeKeys[i1], NodeKeys[i1 + 1], NodeKeys[i1 + 2]))
        NodeList = []
        for each1 in IterNode:
            nodeI = nodeDict[each1[0]]
            nodeJ = nodeDict[each1[1]]
            nodeK = nodeDict[each1[2]]
            nodeIx, nodeIy = nodeI[0], nodeI[1]
            nodeJx, nodeJy = nodeJ[0], nodeJ[1]
            nodeKx, nodeKy = nodeK[0], nodeK[1]
            a1 = (nodeJy - nodeIy)  #两点法确定直线方程 （y2-y1）x+(x1-x2)y+(x2-x1)y1-x1(y2-y1)=0
            b1 = -(nodeJx - nodeIx)
            c1 = (nodeJx - nodeIx) * nodeIy - (nodeJy - nodeIy) * nodeIx
            a2 = (nodeKy - nodeJy)
            b2 = -(nodeKx - nodeJx)
            c2 = (nodeKx - nodeJx) * nodeJy - (nodeKy - nodeJy) * nodeJx
            c1_1 = c1 - math.sqrt(a1 ** 2 + b1 ** 2) * coverThick
            c1_2 = c1 + math.sqrt(a1 ** 2 + b1 ** 2) * coverThick
            c2_1 = c2 - math.sqrt(a2 ** 2 + b2 ** 2) * coverThick
            c2_2 = c2 + math.sqrt(a2 ** 2 + b2 ** 2) * coverThick

            nodeD1_1=self._pointToLineD(a1,b1,c1_1,nodeIx,nodeIy,nodeJx,nodeJy)
            D1_1Index=is_in_2d_polygon(nodeD1_1,closedNodeValues)
            nodeD2_1 = self._pointToLineD(a2,b2,c2_1,nodeJx,nodeJy,nodeKx,nodeKy)
            D2_1Index = is_in_2d_polygon(nodeD2_1, closedNodeValues)
            if pos == "outLine":
                c11 = c1_1 if D1_1Index==True else c1_2
                c22 = c2_1 if D2_1Index==True else c2_2
            elif pos == "innerLine":
                c11 = c1_1 if D1_1Index==False else c1_2
                c22 = c2_1 if D2_1Index==False else c2_2
            else:
                print("Error!Please select outLine or innerLine mode!")
            A = np.array([[a1, b1], [a2, b2]])
            B = np.array([-c11, -c22])
            newNode = list(solve(A, B))
            NodeList.append((newNode[0], newNode[1]))
        NodeList.insert(0, NodeList[-1])
        del NodeList[-1]
        return NodeList
    ####################################################
    def _middleLineNode(self, nodeDict,coverThick,pos="outLine"):
        """
        计算分界线各节点的列表
        输入：
            nodeDict:节点字典 {1:(2.3,4.3)}
            coverThick:保护层厚度
            pos:外侧分界线（"outLine"),内侧分界线("innerLine")
        返回：
            NodeList:外分界线节点列表[(x1,y1),(x2,y2),...,(xn,yn)]
        """
        newNodeList=self._interNodeCoord(nodeDict, coverThick, pos)#计算多边形整体缩放后的交点坐标
        return newNodeList
    ####################################################
    def _triEleInfo(self, nodeNArray, eleNArray):
        """
        计算生成的三角纤维单元的面积与形心坐标
        输入：
            nodeNArray:节点坐标列表[[x1,y1],[x2,y2]]
            eleNArray:单元列表[[I1,J1,K1],[I2,J2,K2]
        返回：
            inFoList:纤维单元信息列表[(xc1,yc1,area1),(xc2,yc2,area2)]
        """
        inFoList = []
        for each in eleNArray:
            I, J, K = each[0], each[1], each[2]
            x1 = nodeNArray[I][0]
            y1 = nodeNArray[I][1]
            x2 = nodeNArray[J][0]
            y2 = nodeNArray[J][1]
            x3 = nodeNArray[K][0]
            y3 = nodeNArray[K][1]
            area = 0.5 * (x1 * y2 - x2 * y1 + x2 * y3 - x3 * y2 + x3 * y1 - x1 * y3)
            xc = (x1 + x2 + x3) / 3.0
            yc = (y1 + y2 + y3) / 3.0
            inFoList.append((xc, yc, area))
        return inFoList
    ####################################################
    def coreMesh(self, eleSize, outLineList, inLineList=None):
        """
        Core concrete mesh
        Input:
            eleSize: fiber size
            outLineList: border line intersect points between outside cover and core [(x1,y1),(x2,y2),...,(xn,yn)]
            inLineList:border line intersect points between inner cover and core[[(x1,y1),(x2,y2),...,(xn,yn)],
                       [(x1,y1),(x2,y2),...,(xn,yn)]]
        Output:
            triEleInfoList: core fiber infomation [(xc1,yc1,area1),(xc2,yc2,area2)]
        """
        triEleInfoList = None
        outNOdeList=[[outLineList[i1][0],outLineList[i1][1],0] for i1 in range(len(outLineList))]

        if inLineList == None:
            geom = pygmsh.opencascade.Geometry()
            geom.add_polygon(outNOdeList,lcar=eleSize)
            mesh = pygmsh.generate_mesh(geom)
            points = mesh.points
            triangles = mesh.cells[-1].data
            triEleInfoList = self._triEleInfo(points, triangles)
        else:
            geom=pygmsh.opencascade.Geometry()
            outPolygon=geom.add_polygon(outNOdeList, lcar=eleSize)
            for eachInnerList in inLineList:
                inNodeList = [[eachInnerList[i2][0], eachInnerList[i2][1], 0] for i2 in range(len(eachInnerList))]
                inPolygon=geom.add_polygon(inNodeList, lcar=eleSize)
                differencePolygon=geom.boolean_difference([outPolygon],[inPolygon])
                outPolygon=differencePolygon
            mesh = pygmsh.generate_mesh(geom)
            points = mesh.points
            triangles = mesh.cells[-1].data
            triEleInfoList = self._triEleInfo(points, triangles)
        return triEleInfoList,points,triangles
    ####################################################
    def _coverDivide(self, outNodeDict, inNodeDict, eleDict, eleSize, coverThick):
        """
        保护层混凝土纤维的分割
        输入:
            outNodeDict:外侧轮廓节点字典--{1:(3.5,3),2:(1.5,5),3:(-1.5,5),4:(-3.5,3)}
            inNodeDict:内侧轮廓节对应点字典--{1:(2.5,2),2:(0.5,4),3:(-0.5,4),4:(-2.5,2)}
            eleDict:外侧轮廓单元字典:--{1:(1,2),2:(2,3),3:(3,4),4:(4,1)}
            eleSize:保护层混凝土纤维单元尺寸
            coverThick:混凝土保护层厚度
        返回：
            centerCoordList:保护层纤维单元中心坐标及面积列表--[(xc1,yc1,A1),(xc2,yc2,A2),...,)
            outPlotNode:外侧分割后各个节点坐标列表--[(x1,y1),(x2,y2),...,(xn,yn)]
            inPlotNode:内侧分割后各个节点坐标列表--[(xin1,yin1),...,(xinn,yinn)]
        """
        nLine = len(eleDict)
        outPlotNode = []
        inPlotNode = []
        centerCoordList = []
        for i1 in range(1, nLine + 1):
            nodeI = eleDict[i1][0]
            nodeJ = eleDict[i1][1]
            outNodeIx = outNodeDict[nodeI][0]
            outNodeIy = outNodeDict[nodeI][1]
            outNodeJx = outNodeDict[nodeJ][0]
            outNodeJy = outNodeDict[nodeJ][1]
            inNodeIx = inNodeDict[nodeI][0]
            inNodeIy = inNodeDict[nodeI][1]
            inNodeJx = inNodeDict[nodeJ][0]
            inNodeJy = inNodeDict[nodeJ][1]
            length = math.sqrt((outNodeJx - outNodeIx) ** 2 + (outNodeJy - outNodeIy) ** 2)
            nEle = int(length /float(eleSize))
            totalOutNodeList = []
            totalInNodeList = []
            totalOutNodeList.append((outNodeIx, outNodeIy))
            totalInNodeList.append((inNodeIx, inNodeIy))
            for i2 in range(1, nEle):
                outxi = ((nEle - i2) * outNodeIx + i2 * outNodeJx) / nEle  # n等分点公式
                outyi = ((nEle - i2) * outNodeIy + i2 * outNodeJy) / nEle
                inxi = ((nEle - i2) * inNodeIx + i2 * inNodeJx) / nEle
                inyi = ((nEle - i2) * inNodeIy + i2 * inNodeJy) / nEle
                totalOutNodeList.append((outxi, outyi))
                totalInNodeList.append((inxi, inyi))
            totalOutNodeList.append((outNodeJx, outNodeJy))
            totalInNodeList.append((inNodeJx, inNodeJy))
            inLength = math.sqrt((totalInNodeList[1][0] - totalInNodeList[0][0]) ** 2 \
                                 + (totalInNodeList[1][1] - totalInNodeList[0][1]) ** 2)
            outLength = math.sqrt((totalOutNodeList[1][0] - totalOutNodeList[0][0]) ** 2 + \
                                  (totalOutNodeList[1][1] - totalOutNodeList[0][1]) ** 2)
            eleArea = (inLength + outLength) * coverThick / 2.0
            for j2 in range(len(totalOutNodeList) - 1):
                outPlotNode.append(totalOutNodeList[j2])
                inPlotNode.append(totalInNodeList[j2])
            for i3 in range(len(totalOutNodeList) - 1):
                outI = totalOutNodeList[i3]
                outJ = totalOutNodeList[i3 + 1]
                inI = totalInNodeList[i3]
                inJ = totalInNodeList[i3 + 1]
                outCenter = ((outI[0] + outJ[0]) / 2.0, (outI[1] + outJ[1]) / 2.0)
                inCenter = ((inI[0] + inJ[0]) / 2.0, (inI[1] + inJ[1]) / 2.0)
                centerCoord = (
                (outCenter[0] + inCenter[0]) / 2.0, (outCenter[1] + inCenter[1]) / 2.0, eleArea)  # 纤维中心坐标及其面积
                centerCoordList.append(centerCoord)
        return centerCoordList, outPlotNode, inPlotNode
    ####################################################
    def coverMesh(self, eleSize, coverThick):
        """
        cover fiber mesh
        Input:
            eleSize: fiber size
            coverThick: cover thick
        Output:
            coverFiberInfo:cover fiber information [(xc1,yc1,area1),(xc2,yc2,area2)]
        """
        outNodeReturn = []
        inNodeReturn = []
        coverFiberInfo = None
        nodeOutDict = self.outNode
        eleOutDict = self.outEle
        nodeNewOutDict = self.outNewNodeDict  # 新生成的外侧保护层混凝土线节点字典
        nodeNewInDict = self.inNewNodeDict  # 新生成的内侧保护层混凝土线节点字典列表
        nodeInDict = self.inNode
        eleInDict = self.inEle
        #外侧保护层混凝土纤维的分割
        fiberInfo, outNodeInfo, inNodeInfo = self._coverDivide(nodeOutDict, nodeNewOutDict,\
                                                               eleOutDict,eleSize,coverThick)
        coverFiberInfo = fiberInfo
        outNodeInfo.append(outNodeInfo[0])
        inNodeInfo.append(inNodeInfo[0])
        outNodeReturn = outNodeInfo
        inNodeReturn = inNodeInfo
        ##内部保护层混凝土的划分
        if self.inNode != None:
            nInhole = len(self.inNode)
            inxList = []
            inyList = []
            inareaList = []
            for i4 in range(nInhole):
                Innerfiber, innerOut, innerIn = self._coverDivide(nodeInDict[i4],\
                        nodeNewInDict[i4], eleInDict[i4],eleSize,coverThick)
                coverFiberInfo = coverFiberInfo + Innerfiber
                innerOut.append(innerOut[0])
                innerIn.append(innerIn[0])
                outNodeReturn = outNodeReturn + innerOut
                inNodeReturn = inNodeReturn + innerIn
                # self.ax.scatter(inxList,inyList,s=2,c="r")
        return coverFiberInfo,outNodeReturn,inNodeReturn
    ####################################################
    def _outBarLineNode(self,barToEdgeDist):
        """
        计算外侧钢筋所在直线交点坐标
        输入：barToEdgeDist-钢筋中心到混凝土边缘最短距离
        输出: outBarLineNodeDict-钢筋中心交点坐标字典 {1:(x1,y1),2:(x2,y2),...,n:(xn,yn)}
        """
        # 计算分界线节点列表[(x1, y1), (x2, y2), ..., (xn, yn)]
        returnNodeList = self._middleLineNode(self.outNode, barToEdgeDist, pos="outLine")
        outBarLineNodeDict = {(i1 + 1): returnNodeList[i1] for i1 in range(len(returnNodeList))}
        return outBarLineNodeDict
    ####################################################
    def _innerBarLineNode(self,barToEdgeDist):
        """
        计算内侧钢筋所在直线交点坐标
        输入：barToEdgeDist-钢筋中心到混凝土边缘最短距离
        输出: innerListDict-钢筋中心交点坐标字典 [{1:(x1,y1),2:(x2,y2),...,n:(xn,yn)},{},...{}]
        """
        if self.inNode != None:
            innerList = []
            innerListDict = []
            for eachNodeDict, eachEleDict in zip(self.inNode, self.inEle):
                #计算分界线各节点的列表[(x1,y1),(x2,y2),...,(xn,yn)]
                returnNodeList = self._middleLineNode(eachNodeDict,barToEdgeDist,pos="innerLine")
                innerList.append(returnNodeList)
                innerListDict.append({(j1 + 1): returnNodeList[j1] for j1 in range(len(returnNodeList))})
            return innerListDict
    ####################################################
    def _barDivide(self, barD, barDist, nodeDict, lineEleDict):
        """
        钢筋纤维的划分
        输入：
            barD-单个纵筋直径
            barDist-纵筋间距
            nodeDict-钢筋线节点字典 {1:(x1,y1),2:(x2,y2),...,(xn,yn)}
            lineEleDict-钢筋线单元字典 {1:(1,2),2:(2,3),3:(3,1)}
        返回：
            barFiberList:钢筋纤维单元列表 [(xb1,yb1,A1),(xb2,yb2,A2),...,(xbn,ybn,An)]
            xRetrunList:钢筋纤维横坐标列表[xb1,xb2,...,xbn]
            yReturnList:钢筋纤维纵坐标列表[yb1,yb2,...,ybn]
        """
        area = np.pi * barD ** 2 / 4.0
        nLine = len(lineEleDict)
        barFiberList = []
        xReturnList = []
        yReturnList = []
        for i1 in range(1, nLine + 1):
            nodeI = lineEleDict[i1][0]
            nodeJ = lineEleDict[i1][1]
            nodeIx = nodeDict[nodeI][0]
            nodeIy = nodeDict[nodeI][1]
            nodeJx = nodeDict[nodeJ][0]
            nodeJy = nodeDict[nodeJ][1]
            length = math.sqrt((nodeJx - nodeIx) ** 2 + (nodeJy - nodeIy) ** 2)
            nEle = int(length / barDist)
            lineBarCoorList = []
            lineBarCoorList.append((nodeIx, nodeIy))
            for i2 in range(1, nEle):
                outxi = ((nEle - i2) * nodeIx + i2 * nodeJx) / nEle  # n等分点公式
                outyi = ((nEle - i2) * nodeIy + i2 * nodeJy) / nEle
                lineBarCoorList.append((outxi, outyi))
            for i3 in range(len(lineBarCoorList)):
                barFiberList.append((lineBarCoorList[i3][0], lineBarCoorList[i3][1], area))
                xReturnList.append(lineBarCoorList[i3][0])
                yReturnList.append(lineBarCoorList[i3][1])
        return barFiberList, xReturnList, yReturnList
    ###################################################
    def barMesh(self, coverThick, outBarD=None, outBarDist=None, inBarD=None, inBarDist=None):
        """
        bar fiber mesh
        Input:
            outBarD: bar diameter in outside zone
            outBarDist: bar space in outside zone
            inBarD: bar diameter in inner zone
            inBarDist: bar space in inner zone
        Output:
            barFiberInfo: bar fiber infomation [(xc1,yc1,area1),(xc2,yc2,area2)]
        """
        barFiberInfo = []
        outXList = []
        outYList = []
        if outBarD != None:
            outBarLineDict=self._outBarLineNode(coverThick+outBarD/2.0) #计算外侧钢筋所在直线交点坐标
            outBarListEle=self.outEle
            # 外侧钢筋纤维的划分
            outBarFiber, outXList, outYList = self._barDivide(outBarD, outBarDist, outBarLineDict, outBarListEle)
            barFiberInfo = barFiberInfo + outBarFiber
        #内侧额钢筋纤维的划分
        if inBarD != None:
            inBarLineDict = self._innerBarLineNode(coverThick+inBarD/2.0) #计算内侧钢筋所在直线交点坐标
            inBarLineEle = self.inEle
            nEle = len(inBarLineEle)
            for i1 in range(nEle):
                inBarFiber, inXList, inYList = self._barDivide(inBarD, inBarDist, inBarLineDict[i1], inBarLineEle[i1])
                barFiberInfo = barFiberInfo + inBarFiber
                outXList = outXList + inXList
                outYList = outYList + inYList
        return barFiberInfo,outXList,outYList
    ###################################################
    def userBarMesh(self, barControlNodeDict,barEleDict):
        """
        用户手动指定每条直线段开始与结束钢筋的坐标，以及每段钢筋的直接与间距
        输入：barControlNodeDDict:各个钢筋段的端点坐标字典{1:(y1,z1),2:(y2,z2),...}
              barEleDict:各个钢筋段单元信息字典{1:(nodeI,nodeJ,barD,barDist)},barD-钢筋直径，barDist-钢筋间距
        输出：barFiberInfo: bar fiber infomation [(xc1,yc1,area1),(xc2,yc2,area2)]
        """
        barFiberInfo =[]
        XListInfo=[]
        YListInfo=[]
        for each in barEleDict.values():
            BarFiber, XList, YList = self._barDivide(each[2], each[3], barControlNodeDict, {1:(each[0],each[1])})
            barFiberInfo+=BarFiber
            XListInfo+=XList
            YListInfo+=YList
        return barFiberInfo, XListInfo,YListInfo
########################################################################################################################
def figureSize(outSideNode):
    """
    计算图形窗口的宽与高
    输入：outSideNode-外侧轮廓节点字典{1:(x1,x2),2(x2,y2),...,n:(xn,yn)}
    输出：figSize-图形窗口宽与高列表 [w,h]
    """
    dictValues=outSideNode.values()
    xValues=[each1[0] for each1 in dictValues]
    yValues = [each2[1] for each2 in dictValues]
    minX,maxX=min(xValues),max(xValues)
    minY,maxY=min(yValues),max(yValues)
    w=np.abs(maxX-minX)
    h=np.abs(maxY-minY)
    return [w,h]
########################################################################################################################
########################################################################################################################
