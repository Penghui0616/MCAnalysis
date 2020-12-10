# -*- coding:utf-8 -*-
# @Time     : 2020/11/30 18:04
# @Author   : Penghui Zhang
# @Email    : penghui@tongji.edu.cn
# @File     : Mander.py
# @Software : PyCharm

import math
from decimal import Decimal, getcontext


class Mander():
	def __init__ (self):
		self.eco = 0.002 #无约束混凝土最大应力时的应变
		self.esu = 0.09 #箍筋拉断应变

	def william_warnke(self, sigma1, sigma2, sigma3):
		"""
		William-Warnke混凝土五参数模型确定的破坏面
		:param sigma1: 第一主应力
		:param sigma2: 第二主应力
		:param sigma3: 第三主应力
		:return: 破坏面函数值
		"""
		getcontext().prec = 30
		sigma1, sigma2, sigma3 = Decimal(sigma1), Decimal(sigma2), Decimal(sigma3)
		sigmaa = (sigma1 + sigma2 + sigma3) / Decimal(3)
		taoa = ((sigma1 - sigma2) ** Decimal(2) + (sigma2 - sigma3) ** Decimal(2) + (sigma3 - sigma1) ** Decimal(2)) ** Decimal(0.5) / Decimal(15) ** Decimal(0.5)

		#若根据实验数据对破坏面进行标定，则按如下公式取值
		#alphat, alphac, kexi, rou1, rou2=Decimal(0.15),Decimal(1.8),Decimal(3.67),Decimal(1.5),Decimal(1.94)
		#a2 = Decimal(9)*(Decimal(1.2)**Decimal(0.5)*kexi*(alphat-alphac)-Decimal(1.2)**Decimal(0.5)*alphat*alphac+rou1*(Decimal(2)*alphac+alphat))/((Decimal(2)*alphac+alphat)*(Decimal(3)*kexi-Decimal(2)*alphac)*(Decimal(3)*kexi+alphat))
		#a1 = (Decimal(2)*alphac-alphat)*a2/Decimal(3)+Decimal(1.2)**Decimal(0.5)*(alphat-alphac)/(Decimal(2)*alphac+alphat)
		#a0 = Decimal(2)*alphac*a1/Decimal(3)-Decimal(4)*alphac**Decimal(2)*a2/Decimal(9)+(Decimal(2)/Decimal(15))**Decimal(0.5)*alphac
		#kexi0 = (-a1-(a1**2-Decimal(4)*a0*a2)**Decimal(0.5))/(Decimal(2)*a2)
		#b2 = Decimal(9)*(rou2*(kexi0+Decimal(1)/Decimal(3))-(Decimal(2)/Decimal(15))**Decimal(0.5)*(kexi0+kexi))/((kexi+kexi0)*(Decimal(3)*kexi-Decimal(1))*(Decimal(3)*kexi0+Decimal(1)))
		#b1 = (kexi+Decimal(1)/Decimal(3))*b2+(Decimal(1.2)**Decimal(0.5)-Decimal(3)*rou2)/(Decimal(3)*kexi-Decimal(1))
		#b0 = -kexi0*b1-kexi0**Decimal(2)*b2
		#r1 = a0+a1*sigmaa+a2*sigmaa**Decimal(2)
		#r2 = b0+b1*sigmaa+b2*sigmaa**Decimal(2)

		# 参考Schickert-Winkler的实验数据得到的结果
		r1 = Decimal(0.053627)-Decimal(0.512079)*sigmaa-Decimal(0.038226)*sigmaa**Decimal(2)
		r2 = Decimal(0.095248)-Decimal(0.891175)*sigmaa-Decimal(0.244420)*sigmaa**Decimal(2)

		r21 = r2**Decimal(2)-r1**Decimal(2)
		cosxita = (Decimal(2)*sigma1-sigma2-sigma3)/(Decimal(2)**Decimal(0.5)*((sigma1-sigma2)**Decimal(2)+(sigma2-sigma3)**Decimal(2)+(sigma3-sigma1)**Decimal(2))**Decimal(0.5))
		rxita = (Decimal(2)*r2*r21*cosxita+r2*(Decimal(2)*r1-r2)*(Decimal(4)*r21*cosxita**Decimal(2)+Decimal(5)*r1**Decimal(2)-Decimal(4)*r1*r2)**Decimal(0.5))/(Decimal(4)*r21*cosxita**Decimal(2)+(r2-Decimal(2)*r1)**Decimal(2))
		return taoa/rxita-1

	def confinedStrengthRatio(self, confiningStrengthRatio1, confiningStrengthRatio2):
		"""
		根据两个方向的约束应力比计算核心混凝土的强度提高系数
		:param confiningStrengthRatio1: x方向的约束应力比
		:param confiningStrengthRatio2: y方向的约束应力比
		:return: 核心混凝土强度提高系数
		"""
		sigma1 = -min(confiningStrengthRatio1, confiningStrengthRatio2)
		sigma2 = -max(confiningStrengthRatio1, confiningStrengthRatio2)
		sigma3Min = -4
		sigma3Max = -1
		while True:
			sigma3Mid = (sigma3Min + sigma3Max) / 2
			fun_min = self.william_warnke(sigma1, sigma2, sigma3Min)
			fun_max = self.william_warnke(sigma1, sigma2, sigma3Max)
			fun_mid = self.william_warnke(sigma1, sigma2, sigma3Mid)
			if abs(fun_mid) < 0.001:   # 当误差小于设定范围时，输出值
				return -sigma3Mid
				break
			elif fun_min * fun_mid < 0:
				sigma3Max = sigma3Mid
			elif fun_max * fun_mid < 0:
				sigma3Min = sigma3Mid

	def circular(self, hoop, d, coverThick, roucc, s, ds, fyh, fco):
		"""
		计算圆截面混凝土柱的Mander模型参数
		:param hoop:箍筋类型，Circular圆形箍筋，Spiral螺旋形箍筋
		:param d: 截面直径
		:param coverThick: 保护层厚度
		:param roucc: 纵筋配筋率,计算时只计入约束混凝土面积
		:param s: 箍筋纵向间距（螺距）
		:param ds: 箍筋直径
		:param fyh: 箍筋屈服强度(MPa)
		:param fco: 无约束混凝土抗压强度标准值(MPa)
		:return:核心混凝土抗压强度(MPa)、核心混凝土抗压强度对应的应变、核心混凝土极限应变
		"""
		de = d - 2*coverThick - ds
		if hoop=='Circular':
			ke = (1 - 0.5*s / de) ** 2 / (1 - roucc)
		elif hoop=='Spiral':
			ke = (1 - 0.5*s / de) / (1 - roucc)
		rous = 3.14159*ds**2/(de*s)
		fle = 0.5*ke*rous*fyh
		fcc = fco*(-1.254+2.254*math.sqrt(1+7.94*fle/fco)-2*fle/fco)
		ecc = self.eco*(1+5*(fcc/fco-1))
		ecu = 0.004+1.4*rous*fyh*self.esu/fcc
		return -fcc, -ecc, -ecu

	def rectangular(self, lx, ly, coverThick, roucc, sl, dsl, roux, rouy, st, dst, fyh, fco):
		"""
		计算矩形截面混凝土柱的Mander模型参数
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
		:param fco:无约束混凝土抗压强度标准值(MPa)
		:return:核心混凝土抗压强度(MPa)、核心混凝土抗压强度对应的应变、核心混凝土极限应变
		"""
		lxe = lx - 2*coverThick-dst
		lye = ly - 2*coverThick-dst
		nsl = 2*(lxe+lye-4*dsl)*sl #绕截面一圈需要布置的纵筋数
		ke = (1-nsl*sl**2/6)*(1-0.5*st/lxe)*(1-0.5*st/lye)/(1-roucc)
		flxe = ke * roux * fyh
		flye = ke * rouy * fyh
		fcc = fco *self.confinedStrengthRatio(flxe/fco, flye/fco)
		ecc = self.eco*(1+5*(fcc/fco-1))
		ecu = 0.004+1.4*(roux+rouy)*fyh*self.esu/fcc
		return -fcc, -ecc, -ecu



