#!/usr/bin/env python
# coding: utf-8 

import socket
import threading
import os
import sys
import ConfigParser
from Autoguiding import AutoguidingThread

class ClientThread(threading.Thread):

	def __init__(self, ip, port, clientsocket, autoguidageThread):
		threading.Thread.__init__(self)
		self.ip = ip
		self.port = port
		self.clientsocket = clientsocket
		self.autoguidingthread = autoguidageThread
		print("[+] Nouveau thread pour %s %s" % (self.ip, self.port, ))

	def run(self): 
		print("Connection de %s %s" % (self.ip, self.port, ))
		r = self.clientsocket.recv(2048)
		if r == "START_AUTOGUIDING":
			self.autoguidingthread.start_autoguiding(self.clientsocket)
		
		if r == "STOP_AUTOGUIDING":
			self.autoguidingthread.stop_autoguiding(self.clientsocket)
		
		if r == "FINDSTAR":
			self.autoguidingthread.try_findstar(self.clientsocket)
			
		if r == "GET_OFFSET":
			self.autoguidingthread.get_offset(self.clientsocket)

		if r.startswith("SET_BOXSIZE"):
			print(r)
			self.autoguidingthread.define_box_size(int(r.split(' ')[1]), self.clientsocket)
			
		if r.startswith("FORCE_FINDSTAR"):
			self.autoguidingthread.force_findstar(int(r.split(' ')[1]), int(r.split(' ')[2]), self.clientsocket)
		
		if r == "GET_TRACKING_IMG":
			self.autoguidingthread.get_tracking_star_image(self.clientsocket)
			
		if r == "GET_CAMERA_IMG":
			self.autoguidingthread.get_camera_image(False, self.clientsocket)
			
		if r == "GET_CAMERA_IMG_DECORATED":
			self.autoguidingthread.get_camera_image(True, self.clientsocket)
			
		if r == "DECREASE_BRIGHTNESS":
			self.autoguidingthread.image_brightness(-1, self.clientsocket)
			
		if r == "INCREASE_BRIGHTNESS":
			self.autoguidingthread.image_brightness(+1, self.clientsocket)
		
		if r == "STOP_CAMERA":
			self.autoguidingthread.stop_camera(self.clientsocket)
			
		if r == "START_CAMERA":
			self.autoguidingthread.start_camera(self.clientsocket)
			
			
		if r == "STOP":
			self.autoguidingthread.thread_stop(self.clientsocket)


# Chargement du fichier de propriétés
config = ConfigParser.RawConfigParser()
config.read('parameters.cfg')




tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcpsock.bind(("", config.getint('TCP_SERVER', 'port')))

guidingthread = AutoguidingThread(config, useGPIO = config.getboolean('RASPBERRY', 'use_gpio'), src = config.getint('CAMERA', 'video_source'), usePiCamera = config.getboolean('CAMERA', 'use_pi_camera'), useDemoSource = config.getboolean('CAMERA', 'demo_mode'), resolution = (config.getint('CAMERA', 'resolution_mode_x'), config.getint('CAMERA', 'resolution_mode_y')), boxSize = config.getint('GUIDING', 'box_size'), framerate = config.getint('CAMERA', 'framerate'), nb_stack_frames = config.get('CAMERA', 'nb_stack_frames'))

guidingthread.start()
while True:
	tcpsock.listen(10)
	print( "En écoute...")
	(clientsocket, (ip, port)) = tcpsock.accept()
	newthread = ClientThread(ip, port, clientsocket, guidingthread)
	
	newthread.start()
