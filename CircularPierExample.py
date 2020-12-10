######################################################################################
#  Author: Junjun Guo
#  E-mail: guojj@tongji.edu.cn/guojj_ce@163.com
#    Date: 05/02/2020
#  Environemet: Successfully excucted in python 3.6
######################################################################################
import os
import numpy as np
import matplotlib.pyplot as plt
from sectionFiberMain import circleSection,polygonSection
from sectionFiberMain import circleSection
from Material import Material
from MCAnalysis import MC

#Define section
outD = 2  # the diameter of the outside circle
coverThick = 0.06  # the thinckness of the cover concrete
outbarD = 0.032  # outside bar diameter
outbarDist = 0.119  # outside bar space
coreSize = 0.2  # the size of core concrete fiber
coverSize = 0.2  # the size of cover concrete fiber
plotState = True # plot the fiber or not plot=True or False
coreFiber, coverFiber, barFiber = circleSection('CircularPier', outD, coverThick, outbarD, outbarDist, coreSize, coverSize, plotState)

# Define material
roucc = np.sum(barFiber, axis=0)[2]/(np.sum(coverFiber, axis=0)[2]+np.sum(coreFiber, axis=0)[2])
material = Material('CircularPier')
barParameter = material.barParameter("HRB400")
coverParameter = material.coverParameter("C40")
coreParameter = material.coreParameterCircular("C40", "Spiral", outD, coverThick, roucc, 0.1, 0.014, 400)

#Estimate the yield curvature of circular section
D = 2 #length of the outer section in x direction
kx = 2.213*barParameter[0]/barParameter[2]/D
ky =kx
np.savetxt("CircularPier/yieldCurvature.txt", [kx, ky],  fmt="%0.6f")

##Estimate the yield curvature of rectangular section
#lx = 2 #length of the outer section in x direction
#ly = 2 #length of the outer section in y direction
#kx = 1.957*barParameter[0]/barParameter[2]/lx
#ky = 1.957*barParameter[0]/barParameter[2]/lx

#Moment curvature analysis
mcInstance = MC('CircularPier', 'Y')
mcInstance.MCAnalysis(200, 0)
momEff = mcInstance.MCCurve()
