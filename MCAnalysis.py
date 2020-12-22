# -*- coding:utf-8 -*-
# @Time     : 2020/11/26 16:25
# @Author   : Penghui Zhang
# @Email    : penghui@tongji.edu.cn
# @File     : MCAnalysis_X.py
# @Software : PyCharm

from openseespy.opensees import *
import numpy as np
import os
import matplotlib.pyplot as plt
import shutil


class MC():
	def __init__(self, sectName, direction):
		"""
		:param sectName: section name
		:param direction: calculated direction ('X' or 'Y')
		"""
		self.sectName = sectName
		self.direction = direction

	def MCAnalysis(self, axialLoad, moment, maxMu=30, numIncr=100):
		"""
		Moment curvature analysis for definded section
		:param axialLoad: axial load
		:param moment: moment in the other direction
		:param maxMu: target ductility for analysis
		:param numIncr: number of analysis increments
		"""
		if self.direction == 'X':
			flagx = 1
			flagy = 0
		else:
			flagx = 0
			flagy = 1

		wipe()
		model('basic', '-ndm', 3, '-ndf', 6)

		node(1, 0.0, 0.0, 0.0)
		node(2, 0.0, 0.0, 0.0)

		fix(1, 1, 1, 1, 1, 1, 1)
		fix(2, 0, 1, 1, 1, 0, 0)

		coverParameter = np.loadtxt(self.sectName+"/coverParameter.txt")
		uniaxialMaterial('Concrete04', 1, coverParameter[0], coverParameter[1], coverParameter[2], coverParameter[3])
		coreParameter = np.loadtxt(self.sectName+"/coreParameter.txt")
		uniaxialMaterial('Concrete04', 2, coreParameter[0], coreParameter[1], coreParameter[2], coreParameter[3])
		barParameter = np.loadtxt(self.sectName+"/barParameter.txt")
		uniaxialMaterial('ReinforcingSteel', 3, barParameter[0], barParameter[1], barParameter[2], barParameter[3], barParameter[4], barParameter[5])

		section('Fiber', 1, '-GJ', 1E10)
		coverfibers = np.loadtxt(self.sectName+"/coverDivide.txt")
		for coverfiber in coverfibers:
			fiber(coverfiber[0], coverfiber[1], coverfiber[2], 1)
		corefibers = np.loadtxt(self.sectName+"/coreDivide.txt")
		for corefiber in corefibers:
			fiber(corefiber[0], corefiber[1], corefiber[2], 2)
		barfibers = np.loadtxt(self.sectName+"/barDivide.txt")
		for barfiber in barfibers:
			fiber(barfiber[0], barfiber[1], barfiber[2], 3)

		element('zeroLengthSection', 1, 1, 2, 1, '-oirent', 1, 0, 0, 0, 1, 0)

		if os.path.exists('coreRecorder'):
			shutil.rmtree('coreRecorder')
		if os.path.exists('barRecorder'):
			shutil.rmtree('barRecorder')
		os.makedirs('coreRecorder')
		os.makedirs('barRecorder')

		setMaxOpenFiles(2000)
		recorder('Node','-file','MomentCurvature.txt','-time','-node',2,'-dof',6-flagy,'disp')
		for i in range(len(corefibers)):
			recorder('Element','-file','coreRecorder/'+str(i+1)+'.txt','-time','-ele',1,'section','fiber',str(corefibers[i,0]),str(corefibers[i,1]),'stressStrain')
		for j in range(len(barfibers)):
			recorder('Element','-file','barRecorder/'+str(j+1)+'.txt','-time','-ele',1,'section','fiber',str(barfibers[j,0]),str(barfibers[j,1]),'stressStrain')

		# Define constant axial load
		timeSeries('Constant', 1)
		pattern('Plain', 1, 1)
		load(2, -axialLoad, 0.0, 0.0, 0.0, moment*flagx, moment*flagy)

		# Define analysis parameters
		integrator('LoadControl', 0.0)
		system('SparseGeneral', '-piv')
		test('NormUnbalance', 1e-9, 10)
		numberer('Plain')
		constraints('Plain')
		algorithm('Newton')
		analysis('Static')

		# Do one analysis for constant axial load
		analyze(1)
		loadConst('-time', 0.0)

		# Define reference moment
		timeSeries('Linear', 2)
		pattern('Plain', 2, 2)
		load(2, 0.0, 0.0, 0.0, 0.0, flagy, flagx)

		# Compute curvature increment
		if self.direction == 'X':
			ky = np.loadtxt(self.sectName+"/yieldCurvature.txt")[0]
		else:
			ky = np.loadtxt(self.sectName + "/yieldCurvature.txt")[1]
		maxK = ky*maxMu
		dK = maxK / numIncr

		# Use displacement control at node 2 for section analysis
		integrator('DisplacementControl', 2, 6-flagy, dK)

		# Do the section analysis
		analyze(numIncr)
		wipe()
		print('MomentCurvature is OK!')

	def mmToInches (self, mm):
		#mm transform to inches
		inches=mm*0.0393700787
		return inches

	def plotLinearRegre (self,x1,y1,x2,y2,xyield,yyield,xmax,ymax):
		#plot moment-curvature curve
		xscat=np.array(x1)
		yscat=np.array(y1)
		xliner=np.array(x2)
		yliner=np.array(y2)
		width=self.mmToInches(90)
		height=self.mmToInches(55)
		plt.figure(1, figsize=(width, height))
		plt.subplot(111)
		p1=plt.plot(xscat,yscat)
		p2=plt.plot(xliner,yliner)
		p3=plt.plot(xyield,yyield,"o")
		p4=plt.plot(xmax,ymax,"o")

		plt.setp(p1, linewidth=1,color='g')
		plt.setp(p2, color='r',linestyle='--',linewidth=1)

		if not os.path.exists('MCFig'):
			os.makedirs('MCFig')

		plt.grid(c='k',linestyle='--',linewidth=0.3)
		plt.xlabel("curvature")
		plt.ylabel("moment(kN.m)")
		plt.xlim(0.0, 1.01*max(xscat))
		plt.ylim(3, 1.3*max(yscat))
		plt.title(self.sectName+'-'+self.direction+'-'+str(int(yliner[2])))
		plt.savefig('MCFig/'+self.sectName+'-'+self.direction+'-'+str(int(yliner[2]))+".png",dpi = 600,bbox_inches="tight")
		plt.show()

	def MCCurve(self):

		fsy = np.loadtxt(self.sectName + "/barParameter.txt")[0]
		Es = np.loadtxt(self.sectName + "/barParameter.txt")[2]
		ey = fsy/Es
		esu = np.loadtxt(self.sectName + "/barParameter.txt")[5]
		ecu = np.loadtxt(self.sectName + "/coreParameter.txt")[2]

		try:
			barDir =  os.listdir('barRecorder/')
			coreDir =  os.listdir('coreRecorder/')
		except:
			print("Please road MC Analysis")

		momentCurvature=np.loadtxt("MomentCurvature.txt")
		sectCurvature=momentCurvature[:, 1]
		sectMoment = momentCurvature[:, 0]
		barYieldIndexList=[]

		#寻找钢筋首次屈服点
		for eachFilePath in barDir:
			barStressStrain=np.loadtxt('barRecorder/'+eachFilePath)
			barStrain=barStressStrain[:,2]
			try:
				indexNum=np.where(barStrain>=ey)[0][0]
				barYieldIndexList.append(indexNum)
			except:
				pass
		barYieldIndex=min(barYieldIndexList)
		barYieldCurvature=sectCurvature[barYieldIndex]
		barYieldMoment=sectMoment[barYieldIndex]
		print('yieldM,yielde',barYieldMoment,barYieldCurvature)

		#寻找核心混凝土压溃或者纵筋达到极限应变的点
		barCrackIndex = len(sectMoment)-1
		barCrackIndexList = []
		for eachFilePath in barDir:
			barStressStrain=np.loadtxt('barRecorder/'+eachFilePath)
			barStrain=barStressStrain[:,2]
			try:
				indexNum=np.where(barStrain>esu)[0][0]
				barCrackIndexList.append(indexNum)
			except:
				pass
		try:
			barCrackIndex=min(barCrackIndexList)
		except:
			pass

		coreCrackIndex = len(sectMoment)-1

		coreCrackIndexList = []
		for eachFile1 in coreDir:
			coreStressStrain=np.loadtxt('coreRecorder/'+eachFile1)
			coreStain=coreStressStrain[:,2]
			try:
				indexNum=np.where(coreStain < ecu)[0][0]
				coreCrackIndexList.append(indexNum)
			except:
				pass
		try:
			coreCrackIndex=min(coreCrackIndexList)
		except:
			pass
		crackIndex = min(barCrackIndex, coreCrackIndex)
		if crackIndex == len(sectMoment)-1:
			print("A larger mu is required")

		ultimateMoment = sectMoment[crackIndex]
		ultimateCurvature = sectCurvature[crackIndex]
		print('ultM,ulte：',ultimateMoment,ultimateCurvature)

		#寻找截面弯矩达到最大点
		momentMaxMoment = max(sectMoment[:crackIndex+1])
		momentMaxIndex = np.where(sectMoment[:crackIndex+1] == momentMaxMoment)[0][0]
		momentMaxCurvature = sectCurvature[:crackIndex+1][momentMaxIndex]
		print('maxM, maxe：',momentMaxMoment,momentMaxCurvature)

		#计算等效屈服弯矩和曲率
		totArea=np.trapz(sectMoment[:crackIndex], sectCurvature[:crackIndex])
		barYieldX=barYieldCurvature
		barYieldY=barYieldMoment
		tanXY=barYieldY/barYieldX

		epsilon=0.001*totArea
		low=0.0
		high=momentMaxMoment
		momentEffictive=(low+high)/2.0
		while abs(momentEffictive*ultimateCurvature-momentEffictive*0.5*momentEffictive/float(tanXY)-totArea)>=epsilon:
			if momentEffictive*ultimateCurvature-momentEffictive/float(tanXY)*momentEffictive*0.5<totArea:
				low=momentEffictive
			else:
				high=momentEffictive
			momentEffictive=(high+low)/2.0

		curvatureEffective=momentEffictive/float(tanXY)
		blinerX=[0,curvatureEffective,ultimateCurvature]
		blinerY=[0,momentEffictive,momentEffictive]
		print('effM, effe：', momentEffictive, curvatureEffective)

		self.plotLinearRegre(sectCurvature[:crackIndex],sectMoment[:crackIndex],blinerX,blinerY,\
		                 barYieldCurvature,barYieldMoment,momentMaxCurvature,momentMaxMoment)
		return momentEffictive
