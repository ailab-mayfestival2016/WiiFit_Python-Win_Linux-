#-*-coding:utf-8-*-

import sioclientCpp as sio

class SioClient:
	def __init__(self):
		self.client=sio.Client()
		self.queue={}
	def start(self,uri,waitUntilConnected=False):
		self.client.set_close_listener(self.onOpen)
		self.client.set_socket_open_listener(self.onSocketOpen)
		self.client.set_socket_close_listener(self.onSocketClose)
		self.client.set_close_listener(self.onClose)
		self.client.connect(uri)
		if(waitUntilConnected):
			while(not self.isConnected()):
				import time
				time.sleep(0.03)
	def isConnected(self):
		return self.client.opened()
	def onOpen(self):
		pass
	def onFail(self):
		pass
	def onClose(self,reason):
		pass
	def onSocketOpen(self,nsp):
		for e in self.eventList:
			self.client.socket(nsp).on(e,self.onEvent)
		self.client.socket(nsp).emit('enter_room',{'room':self.myRoom})
	def onSocketClose(self,nsp):
		pass
	def onEvent(self,event):
		name=event.get_name()
		if(name in self.queue):
			for q in self.queue[name]:
				q.append([name,event.get_message()])
		else:
			self.defaultQueue.append([name,event.get_message()])
	def setEventList(self,list):
		self.eventList=list[:]
	def setMyRoom(self,name):
		self.myRoom=name
	def setDataQueue(self,_queue,_eventList=None):
		if(_eventList is None):
			self.defaultQueue=_queue
		else:
			for e in _eventList:
				if(e in self.queue):
					self.queue[e].append(_queue)
				else:
					self.queue[e]=[_queue]
	def emit(self,event,data,nsp=None):
		if(nsp is None):
			self.client.socket().emit(event,data)
		else:
			self.client.socket(nsp).emit(event,data)
	def sendData(self,eventName,dstRooms,data):
		self.client.socket().emit('transfer',{
				'event':eventName,
				'room':dstRooms,
				'data':data
			})
	


