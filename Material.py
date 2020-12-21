# -*- coding:utf-8 -*-
# @Time     : 2020/11/26 19:25
# @Author   : Penghui Zhang
# @Email    : penghui@tongji.edu.cn
# @File     : Material.py
# @Software : PyCharm
import math
from Mander import Mander
import numpy as np

class Material():
	def __init__ (self, sectName):
		self.sectName = sectName

	def barParameter(self, steelTag):
		"""
		steelTag --unique material object integer tag
		fy --Yield stress in tension(kPa)
	    fu --Ultimate stress in tension(kPa)
		Es--Initial elastic tangent(kPa)
		Esh--Tangent at initial strain hardening(kPa)
		esh--Strain corresponding to initial strain hardening
		eult--Strain at peak stress
		"""
		fy = eval("".join(list(filter(str.isdigit, steelTag))))*1000
		Es = 2e8
		Esh = 2e6
		esh = 0.045
		eult = 0.1
		fu = 0.01*Es*(eult-esh)+fy
		barPara = [fy, fu, Es, Esh, esh, eult]
		np.savetxt(self.sectName + "/barParameter.txt", barPara, fmt="%0.6f")
		return barPara

	def coverParameter(self, concreteTag):
		"""
		concreteTag --unique material object integer tag
		fc --concrete compressive strength at 28 days(kPa)
	    ec --concrete strain at maximum strength
		ecu-- concrete strain at crushing strength
		Ec--initial stiffness(kPa)
		"""
		def factor1(R):
			if R<=50:
				return 0.76
			elif R==80:
				return 0.82
			else:
				return 0.76+0.06*(R-50)/30
		def factor2(R):
			if R<40:
				return 1.00
			elif R==80:
				return 0.87
			else:
				return 1-0.13*(R-40)/40
		R = eval("".join(list(filter(str.isdigit, concreteTag))))
		fc = -R*0.88*factor1(R)*factor2(R)*1000
		ec = -0.002
		ecu = -0.004
		Ec = math.sqrt(-fc/1000)*5e6
		coverPara = [fc, ec, ecu, Ec]
		np.savetxt(self.sectName + "/coverParameter.txt", coverPara, fmt="%0.6f")
		return coverPara

	def coreParameterCircular(self, concreteTag, hoop, d, coverThick, roucc, s, ds, fyh):
		"""
		:param concreteTag: 混凝土标号
		:param hoop:箍筋类型，'Circular'圆形箍筋，'Spiral'螺旋形箍筋
		:param d: 截面直径
		:param coverThick: 保护层厚度
		:param roucc: 纵筋配筋率,计算时只计入约束混凝土面积
		:param s: 箍筋纵向间距（螺距）
		:param ds: 箍筋直径
		:param fyh: 箍筋屈服强度(MPa)
		"""
		fco = self.coverParameter(concreteTag)[0]
		Ec = math.sqrt(-fco / 1000) * 5e6
		confinedConcrete = Mander()
		fc, ec, ecu = confinedConcrete.circular(hoop, d, coverThick, roucc, s, ds, fyh, -fco/1000)
		corePara = [1000*fc, ec, ecu, Ec]
		np.savetxt(self.sectName + "/coreParameter.txt", corePara, fmt="%0.6f")
		return corePara

	def coreParameterRectangular(self, concreteTag, lx, ly, coverThick, roucc, sl, dsl, roux, rouy, st, dst, fyh):
		"""
		:param concreteTag: 混凝土标号
		:param lx: x方向截面的宽度
		:param ly: y方向截面宽度
		:param coverThick:保护层厚度
		:param roucc:纵筋配筋率,计算时只计入约束混凝土面积
		:param sl:纵筋间距
		:param dsl:纵筋直径
		:param roux:x方向的体积配箍率,计算时只计入约束混凝土面积
		:param rouy:y方向的体积配箍率,计算时只计入约束混凝土面积
		:param st:箍筋间距
		:param dst:箍筋直径
		:param fyh:箍筋屈服强度(MPa)
		"""
		fco = self.coverParameter(concreteTag)[0]
		Ec = math.sqrt(-fco / 1000) * 5e6
		confinedConcrete = Mander()
		fc, ec, ecu = confinedConcrete.rectangular(lx, ly, coverThick, roucc, sl, dsl, roux, rouy, st, dst, fyh, -fco/1000)
		corePara = [1000*fc, ec, ecu, Ec]
		np.savetxt(self.sectName + "/coreParameter.txt", corePara, fmt="%0.6f")
		return corePara



