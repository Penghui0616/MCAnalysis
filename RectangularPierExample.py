# -*- coding:utf-8 -*-
# @Time     : 2020/11/26 16:25
# @Author   : Penghui Zhang
# @Email    : penghui@tongji.edu.cn
# @File     : MCAnalysis_X.py
# @Software : PyCharm

import os
import numpy as np
import matplotlib.pyplot as plt
from sectionFiberMain import circleSection,polygonSection
from sectionFiberMain import circleSection
from Material import Material
from MCAnalysis import MC

#Define section
sectName = 'RectangularPier'
outSideNode = {1: (0.8,1.6), 2: (-0.8,1.6), 3: (-0.8,-1.6), 4: (0.8,-1.6)}
outSideEle = {1: (1, 2), 2: (2, 3), 3: (3, 4), 4: (4, 1)}

coverThick = 0.06  # the thinckness of the cover concrete(m)
coreSize = 0.2  # the size of core concrete fiber
coverSize = 0.3  # the size of cover concrete fiber
outBarDist = 0.1846153846 #bar space(m)
outBarD = 0.028 #bar diameter(m)
plotState = True # plot the fiber or not plot=True or False
plotState=True  # plot the fiber or not plot=True or False
autoBarMesh=True #if false provide the barControlNodeDict and barEleDict
userBarNodeDict=None # {1:(y1,z1),2:(y2,z2),...} bar line end nodes
userBarEleDict=None # {1:(nodeI,nodeJ,barD,barDist),...}  bar line end nodes number and diameter and distance
coreFiber,coverFiber,barFiber=polygonSection(sectName, outSideNode, outSideEle, coverThick, coreSize, coverSize,
								   outBarD, outBarDist,plotState,autoBarMesh)

# Define material
roucc = np.sum(barFiber, axis=0)[2]/np.sum(coreFiber, axis=0)[2]
lx = 1.6 #length of the outer section in x direction(m)
ly = 3.2 #length of the outer section in y direction(m)
sl = 0.1846153846 #longitudinal bar space(m)
dsl = 0.028 #longitudinal bar diameter(m)
roux = 0.005 #stirrup reinforcement ratio in x direction
rouy = 0.005 #stirrup reinforcement ratio in y direction
st = 0.15 #transverse bar space(m)
dst = 0.012 #transverse bar diameter(m)
fyh = 400 #transverse bar yield stress(MPa)

material = Material(sectName)
barParameter = material.barParameter("HRB400")
coverParameter = material.coverParameter("C40")
coreParameter = material.coreParameterRectangular("C40", lx, ly, coverThick, roucc, sl, dsl, roux, rouy, st, dst, fyh)

#Estimate the yield curvature of rectangular section
kx = 1.957*barParameter[0]/barParameter[2]/lx
ky = 1.957*barParameter[0]/barParameter[2]/lx
np.savetxt(sectName+"/yieldCurvature.txt", [kx, ky],  fmt="%0.6f")

#Moment curvature analysis
mcInstance = MC('RectangularPier', 'X')
mcInstance.MCAnalysis(23000, 0)
momEff = mcInstance.MCCurve()
