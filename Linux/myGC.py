#-*-coding:utf-8-*-
import os,sys
sys.path.append(os.path.join(os.getcwd(),os.pardir))
from Bar import Bar
from sioclient import SioClient
import wiiboard
import pygame
from pygame.locals import *
import time
def drawText(screen,text,arias,col,pos,fontSize=24):
	font = pygame.font.SysFont(None, fontSize)
	screen.blit(font.render(text, arias, col), pos)
class Button:
	def __init__(self,pos=(0,0),size=(50,20),text="Button",bgCol=(180,180,180),txtCol=(0,0,0),fontSize=24):
		self.pos=pos
		self.text=text
		self.bgCol=bgCol
		self.txtCol=txtCol
		self.txtPos=(pos[0]+10,pos[1]+10)
		self.fontSize=fontSize
		self.size=size
	def render(self,screen):
		pygame.draw.rect(screen,self.bgCol,Rect(self.pos[0],self.pos[1],self.size[0],self.size[1]))
		drawText(screen,self.text,True,self.txtCol,self.txtPos,self.fontSize)
	def isClicked(self,pos):
		return (self.pos[0]<=pos[0] and self.pos[1]<=pos[1] and pos[0]<=self.pos[0]+self.size[0] and pos[1]<=self.pos[1]+self.size[1])
class Controller:
	def __init__(self):
		self.cogX=0.
		self.cogY=0.
		self.clickPos=(0,0)
		self.width=480
		self.height=480
		self.recvQueue=[]
		self.sendArrow=False
		self.pushed=False
		self.barInit=False
	def screenUpdate(self):
		self.screen.fill((255,255,255))
		pygame.draw.line(self.screen, (0,0,0), (0,self.height/2), (self.width,self.height/2))
		pygame.draw.line(self.screen, (0,0,0), (self.width/2,0), (self.width/2,self.height))
		pygame.draw.circle(self.screen, (255,0,0), (int(0.5*(1+self.cogX)*self.width),int((1-0.5*(1+self.cogY))*self.height)), 5)
		#pygame.draw.circle(self.screen, (255,255,0), self.clickPos, 5)
		send="Enabled" if self.sendArrow else "Disabled"
		if(self.barInit):
			drawText(self.screen,"S key: Enable/Disable Sending (Now "+send+")",True,(0,0,0),(30,20),fontSize=24)
		else:
			drawText(self.screen,"S key: Enable/Disable Sending (Now Waiting bar_width)",True,(0,0,0),(30,20),fontSize=24)
		drawText(self.screen,"C key: Calibrate (or push Board button)",True,(0,0,0),(30,40),fontSize=24)
		drawText(self.screen,"Q key: Quit",True,(0,0,0),(30,60),fontSize=24)
		pygame.display.update()  # 画面を更新
	def connectServer(self):
		self.client=SioClient()
		#受信するイベント名一覧をリストとしてclientに渡す
		eventList=["bar_width"];
		self.client.setEventList(eventList)
		#自身を表す部屋名を設定する(Game Serverなら例えば"Game"と決める)
		self.client.setMyRoom("Controller")
		#受信データを格納するキューを追加する
		self.client.setDataQueue(self.recvQueue)
		#URLを指定して接続開始
		#self.client.start("http://ailab-mayfestival2016-base.herokuapp.com")
		self.client.start("http://192.168.1.58:8000")
		#self.client.start("http://localhost:8000")
	def main(self):
		pygame.init()
		self.connectServer()
		self.bar=Bar()
		self.board = wiiboard.Wiiboard()
		self.address = self.board.discover()
		#self.address ="00:1F:C5:AA:4F:6D"
		self.board.connect(self.address) #The wii board must be in sync mode at this time
		time.sleep(0.1)
		self.board.setLight(True)
		self.sysfont = pygame.font.SysFont(None, 80)
		self.screen = pygame.display.set_mode((self.width,self.height))
		# タイトルバーの文字列をセット
		pygame.display.set_caption(u"Wii Board Controller")
		self.screenUpdate()
		send=False
		done = False
		validity=False
		while (not done):
			time.sleep(1./30.)
			self.screenUpdate()
			while(len(self.recvQueue)>0):
				e=self.recvQueue[0]
				del self.recvQueue[0]
				if(e[0]=="bar_config"):
					self.barInit=True
					self.bar.width=e[1]["width"]
					self.bar.region=e[1]["region"][:]
					self.bar.calib=e[1]["calib"][:]
					print "bar width initialized"
			for event in pygame.event.get():
				if event.type == KEYDOWN:  # キーを押したとき
					# ESCキーならスクリプトを終了
					if event.key == K_s:
						if(self.barInit):
							self.sendArrow=not self.sendArrow
						else:
							self.sendArrow=False
					elif(event.key==K_b):
						self.barInit=True
					elif event.key==K_c:
						self.board.calibrate()
					elif event.key==K_o:
						self.client.sendData("px_ready",["Manager"],True)
					elif event.key==K_p:
						self.client.sendData("px_ready",["Manager"],False)
					elif event.key == K_q:
						done=True
				if event.type == wiiboard.WIIBOARD_MASS:
					if (event.mass.totalWeight > 10):
						self.cogX = ((event.mass.topRight + event.mass.bottomRight) - (event.mass.topLeft + event.mass.bottomLeft))/(event.mass.totalWeight)
					        self.cogY = ((event.mass.topRight + event.mass.topLeft) - (event.mass.bottomRight + event.mass.bottomLeft))/(event.mass.totalWeight)
						validity=True
						#print "COG (x,y)=("+`self.cogX`+","+`self.cogY`+")"
					else:
						validity=False
						self.cogX = 0.
					        self.cogY = 0.
				elif event.type == wiiboard.WIIBOARD_BUTTON_PRESS:
					print "Button pressed!"
	
				elif event.type == wiiboard.WIIBOARD_BUTTON_RELEASE:
					print "Button released"
					self.board.calibrate()
#					done = True
				elif event.type == QUIT:
					print "Quit"
					done=True
							
				#Other event types:
				#wiiboard.WIIBOARD_CONNECTED
				#wiiboard.WIIBOARD_DISCONNECTED
			if(self.client.isConnected and self.sendArrow):
				if(self.cogX>1):
					self.cogX=1.0
				elif(self.cogX<-1.0):
					self.cogX=-1.0
				if(validity):
					self.bar.calculate(self.client,self.cogX)
					print "send : cog=X",self.cogX,",pos=",self.bar.position
		self.board.disconnect()
		pygame.quit()
	
	#Run the script if executed
if __name__ == "__main__":
	c=Controller()
	c.main()
