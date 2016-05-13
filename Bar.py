#-*-coding:utf-8-*-
import time
class Bar(object):
	def __init__(self):
		self.width = 60.0 #バーの幅[cm]
		self.position = 100.0 #バーの位置(x座標)[cm]
		self.velocity = 0.0 #バーの移動速度[cm/s]
		self.time = time.time()
		self.region = [-120.,120.] #バーが存在できる領域(壁から壁)
		self.calib=[-0.85,+0.85] #重心位置の許容範囲
	def calculate(self,client,slope): #コントローラーの傾きのデータ(-1～1)からバーの位置と速度を計算する
		val=min(self.calib[1],max(self.calib[0],slope))#self.calibの範囲内に
		movable=[self.region[0]+self.width/2.0,self.region[1]-self.width/2.0]#バーの中心の移動可能域
		pos=movable[0]+(movable[1]-movable[0])*(val-self.calib[0])/(self.calib[1]-self.calib[0])#重心位置を移動可能域と線形に対応付け
		self.position = pos
		client.sendData('bar_position',['Client','Game'],pos)