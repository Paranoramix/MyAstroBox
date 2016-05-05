#!/usr/bin/env python
# coding: utf-8 

import cv2
import math
import numpy
import time
import threading
import RPi.GPIO as GPIO
import imutils
from VideoCapture import VideoStream

class AutoguidingThread(threading.Thread):
	""" Managing autoguiding for telescop mount based on image analysis to detect movement of a star inside an image
	"""

	def __init__(self, config, boxSize = 15, useGPIO = False, src = 0, usePiCamera = False, useDemoSource = False, resolution = (320, 240), framerate = 32, nb_stack_frames = 5):
		threading.Thread.__init__(self)
		
		self.config = config
		self._continue_work = True
		
		self.demo_mode = None
		
		self.vs = None
		self.src = None
		self.usePiCamera = None
		self.resolution = None
		self.framerate = None
		self.nb_stack_frames = None

		self.change_source_parameter(clientsocket = None, src = src, usePiCamera = usePiCamera, useDemoSource = useDemoSource, resolution = resolution, framerate = framerate, nb_stack_frames = nb_stack_frames)
		
		if useGPIO:
			# Corrections should be sent to GPIO
			GPIO.setmode(GPIO.BCM)
			#Assign GPIO number
			self.RP = 18  #R+
			self.RN = 17  #R-
			self.DP =  4  #D+
			self.DN = 22  #D-
			#Setup up for GPIO Pin
			GPIO.setup(self.RP,  GPIO.OUT)
			GPIO.setup(self.RN,  GPIO.OUT)
			GPIO.setup(self.DP,  GPIO.OUT)
			GPIO.setup(self.DN,  GPIO.OUT)
			GPIO.output(self.RP, False)
			GPIO.output(self.RN, False)
			GPIO.output(self.DP, False)
			GPIO.output(self.DN, False)
			self.use_gpio = True
		else:
			self.use_gpio = False
		
		self._status = False
		self._pause = False

		
		self.autoguiding = False
		self.findstar = False
		
		self.brightness = numpy.dtype('float16')
		self.trackX = numpy.dtype('float16')
		self.trackY = numpy.dtype('float16')
		
		self.trackX = -1.
		self.trackY = -1.
		self.brightness = -1.
		
		self.offsetX = 0.
		self.offsetY = 0.
		self.refX = 0
		self.refY = 0
		
		self.box_size = boxSize
		
		self.max_brightness = 0.5 # Max brightness correspond au taux de remplissage de l'étoile dans la boite de suivi. Si l'étoile est trop grande par rapport à boxSize, alors le guidage sera de mauvaise qualité
		self.min_brightness = 0.05 # Min brightness correspond au taux de remplissage minimum de l'étoile dans la bote de suivi

		print("vs: " + str(self.vs))
		print("src: " + str(self.src))
		print("usePiCamera: " + str(self.usePiCamera))
		print("camera_image: " + str(self.camera_image))
		print("resolution: " + str(self.resolution))
		print("framerate: " + str(self.framerate))
		print("demo_mode: " + str(self.demo_mode))
		print("use_gpio: " + str(self.use_gpio))
		print("_status: " + str(self._status))
		print("_pause: " + str(self._pause))
		print("autoguiding: " + str(self.autoguiding))
		print("findstar: " + str(self.findstar))
		print("brightness: " + str(self.brightness))
		print("trackX: " + str(self.trackX))
		print("trackY: " + str(self.trackY))
		print("offsetX: " + str(self.offsetX))
		print("offsetY: " + str(self.offsetY))
		print("box_size: " + str(self.box_size))
		print("min_brightness: " + str(self.min_brightness))
		print("max_brightness: " + str(self.max_brightness))

	def thread_start(self, clientsocket):
		""" Méthode pour démarrer le traitement """
		self._status = True
		clientsocket.send("OK")


	def thread_stop(self, clientsocket):
		self._status = False
		clientsocket.send("OK")

	def thread_pause(self, clientsocket):
		self._pause = True
		if clientsocket is not None:
			clientsocket.send("OK")

	def thread_continue(self, clientsocket):
		self._pause = False
		if clientsocket is not None:
			clientsocket.send("OK")
		
	def start_autoguiding(self, clientsocket):
		print("Starting autoguiding...")
		self.autoguiding = True
		clientsocket.send("OK")

	def stop_autoguiding(self, clientsocket):
		print("Stopping autoguiding...")
		self.autoguiding = False
		clientsocket.send("OK")
		
	def try_findstar(self, clientsocket):
		print("Finding a good star for autoguiding...")
		self.trackX = 0.
		self.trackY = 0.
		self.brightness = 0.
		self.findstar = True
		while self.findstar == True:
			time.sleep(0.1)
			# do nothing
		# Respond to the socket with result!
		clientsocket.send("Brightness: " + str(self.brightness) + " X: " + str(self.trackX) + " Y: " + str(self.trackY))

	def force_findstar(self, starX, starY, clientsocket):
		print("User selected this star coordinates...")
		print("Try to follow this star for autoguiding")
		self.trackX = starX
		self.trackY = starY
		
	def start_calibration(self, clientsocket):
		print("Starting calibration...")
		
	def stop_calibration(self, clientsocket):
		print("Stopping calibration...")

	def get_offset(self, clientsocket):
		""" Retourne l'offset calculé dans le cadre de l'autoguidage """
		print("offset asked...")
		if self.autoguiding == True:
			clientsocket.send("OffsetX: " + str(self.offsetX) + " ; OffsetY: " + str(self.offsetY))
		else:
			clientsocket.send("Error: no guiding started")

	def define_box_size(self, newBoxSize, clientsocket):
		""" Définit la taille de la boite qui entoure l'étoile guide """
		print("defining box size...")
		self.box_size = newBoxSize
		clientsocket.send("New Box Size: " + str(self.box_size))

	def image_brightness(self, evolution, clientsocket):
		""" Définit la le nombre d'images à cumuler """
		print("defining box size...")
		b = int(self.nb_stack_frames) + evolution
		if b > 0:
			self.nb_stack_frames = str(b)
			clientsocket.send("New brightness: " + str(self.nb_stack_frames))
		else:
			clientsocket.send("ALERT Min brightness: " + str(self.nb_stack_frames))
	
	def get_tracking_star_image(self, clientsocket):
		""" Retourne l'image de l'étoile guide """
		print("send tracking star...")
		self.thread_pause(None)
		while self._continue_work:
			time.sleep(0.1)

		retval, buf = cv2.imencode('.jpg', self.trackstar)
		clientsocket.send(buf)
		self.thread_continue(None)
		
	
	def get_camera_image(self, isDecorated, clientsocket):
		""" Retourne l'image de la webcam, décorée ou non """
		print("send camera image...")
		self.thread_pause(None)
		while self._continue_work:
			time.sleep(0.1)

		if isDecorated:
			retval, buf = cv2.imencode('.jpg', self.decorated_image)
		else:
			retval, buf = cv2.imencode('.jpg', self.camera_image)

		clientsocket.send(buf)
		self.thread_continue(None)
	
	
	
	
	
	

	def change_source_parameter(self, clientsocket = None, src = 0, usePiCamera = False, useDemoSource = False, resolution = (320, 240), framerate = 32, nb_stack_frames = 5):
		""" Modifie la caméra source  """

		if self.vs is not None:
			# Dans le cas où la vidéo a été déjà initialisée, on arrête le VideoStream
			self.vs.stop()
			
		if useDemoSource: # Mode DEMO
			self.demo_mode = True
			self.camera_image = cv2.imread("/home/pi/MyAutoguider/input_examples/image_test_autoguidage.jpg", 0)
			
		else:
			# Initialisation du VideoStream
			self.vs = VideoStream(src = src, usePiCamera = usePiCamera, resolution = resolution, framerate = framerate).start()
			time.sleep(5.0)
			self.demo_mode = False
			self.usePiCamera = usePiCamera
			self.camera_image = self.vs.read()
			self.src = src
			self.resolution = resolution
			self.framerate = framerate
			self.nb_stack_frames = nb_stack_frames
	
		if clientsocket is not None:
			clientsocket.send("OK!")

		print("src: " + str(self.src))
		print("usePiCamera: " + str(self.usePiCamera))
		print("resolution: " + str(self.resolution))
		print("framerate: " + str(self.framerate))
		print("demo_mode: " + str(self.demo_mode))
		print("nb_stack_frames: " + str(self.nb_stack_frames))

	def save_parameters(self, clientsocket):
		""" Sauvegarde la configuration """
		self.config.set('RASPBERRY', 'use_gpio', str(self.use_gpio))
		self.config.set('CAMERA', 'video_source', str(self.src))
		self.config.set('CAMERA', 'use_pi_camera', str(self.usePiCamera))
		self.config.set('CAMERA', 'demo_mode', str(self.demo_mode))
		self.config.set('CAMERA', 'resolution_mode_x', str(self.resolution[0]))
		self.config.set('CAMERA', 'resolution_mode_y', str(self.resolution[1]))
		self.config.set('CAMERA', 'framerate', str(self.framerate))
		self.config.set('GUIDING', 'box_size', str(self.boxSize))
		with open("parameters.cfg", 'w') as configFile:
			self.config.write(configFile)
			
	def stop_camera(self, clientsocket):
		self.vs.stop()
		clientsocket.send("OK!")
			
	def start_camera(self, clientsocket):
		self.thread_pause(None)
		while self._continue_work:
			time.sleep(0.1)
			
		self.change_source_parameter(clientsocket = clientsocket, src = self.src, usePiCamera = self.usePiCamera, useDemoSource = self.demo_mode, resolution = self.resolution, framerate = self.framerate, nb_stack_frames = self.nb_stack_frames)
		self.thread_continue(None)







		
	def run(self):
		print("Autoguiding thread started...")
		self._status = True
		i = 0
		while self._status:
			if self._pause:
				time.sleep(0.1)
				self._continue_work = True
				continue
			else:
				i += 1
				self._continue_work = False

				# En mode démo, on utilise des images sur le disque
				if self.demo_mode:
					if i % 2 == 0:
						self.camera_image = cv2.imread("/home/pi/MyAutoguider/input_examples/image_test_autoguidage.jpg", 0)
						print("/home/pi/MyAutoguider/input_examples/image_test_autoguidage.jpg")
					else:
						self.camera_image = cv2.imread("/home/pi/MyAutoguider/input_examples/image_test_autoguidage_2.jpg", 0)
						print("/home/pi/MyAutoguider/input_examples/image_test_autoguidage_2.jpg")
				else:
					# Sinon, on récupère une trame de la webcam / raspicam convertie en N&B
					countloop = 0
					tmp_img = 0

					for countloop in range (0, int(self.nb_stack_frames)): 
						img_grey = cv2.cvtColor(self.vs.read(), cv2.COLOR_BGR2GRAY) 
						tmp_img = tmp_img + img_grey
						
					self.camera_image = tmp_img
				
				ratio = 255 / self.camera_image.max()
				self.camera_image = self.camera_image * ratio
				bY, bX = self.camera_image.shape
				
				if self.findstar == True:
					# Finding all stars in image
					uX = 1.0 * (self.camera_image.max(axis = 0))
					uY = 1.0 * (self.camera_image.max(axis = 1))
					
					nX = 0
					nY = 0
					
					X = numpy.zeros(10000)
					Y = numpy.zeros(10000)
					
					threshold = uX.max() * 0.7
					
					for c in range(0, bX - 1):
						if (uX[c] >= threshold) * (uX[c + 1] <= threshold):
							X[nX] = c
							nX = nX + 1
						else:
							uX[c] = 0
					for r in range(0, bY - 1):
						if (uY[r] >= threshold) * (uY[r + 1] <= threshold):
							Y[nY] = r
							nY = nY + 1
						else:
							uY[r] = 0
							
					uY[len(uY) - 1] = 0
					uX[len(uX) - 1] = 0
					
					# Finding the brightness star
					starCount = 0
					X1 = 0
					Y1 = 0
					
					for c in range (0, nX):
						for r in range (0, nY):
							ulX = X[c] - self.box_size
							ulY = Y[r] - self.box_size
							lrX = X[c] + self.box_size
							lrY = Y[r] + self.box_size

							if ulX <= 0:
								ulX = 0
							if ulY <= 0:
								ulY = 0
							if lrX >= bX - 1:
								lrX = bX - 1
							if lrY >= bY - 1:
								lrY = bY - 1
								
							start_brightness = 1.0 * self.camera_image[ulY:lrY, ulX:lrX].sum() / (2 * self.box_size * 2 * self.box_size)
							print ("star brightness: " + str(start_brightness))
							
							if start_brightness > self.brightness and start_brightness <= 255 * self.max_brightness and start_brightness >= 255 * self.min_brightness:
								self.trackY = Y[r]
								self.trackX = X[c]
								starCount += 1
								self.brightness = start_brightness
					
					self.decorated_image = self.camera_image.copy()
					cv2.rectangle(self.decorated_image, (int(self.trackX - self.box_size), int(self.trackY - self.box_size)), (int(self.trackX + self.box_size), int(self.trackY + self.box_size)), 255, 1)
					#cv2.imwrite("/home/pi/MyAutoguider/output_result/star_found.jpg", self.decorated_image)
					print ("End for searching a good star")
					self.findstar = False
						
				
			
				if self.autoguiding == True:
					trackBoxC = bY / 4 
					trackBoxR = bX / 4
					refX = 0.
					refY = 0.
					averageX = 0
					averageY = 0
					averageCount = 0
					temptrackStar = 0
					checkS = 0
					blurFactor = 2
					
					# On travaille sur une partie de l'image
					self.trackstar = self.camera_image[self.trackY - int(trackBoxC / 2):self.trackY + int(trackBoxC / 2), self.trackX - int(trackBoxR / 2):self.trackX + int(trackBoxR / 2)]
					self.trackstar = cv2.GaussianBlur(self.trackstar, (0, 0), blurFactor)
					
					maxBright = self.trackstar.max()
					ratio = 255 / maxBright
					self.trackstar = self.trackstar * ratio
					
					c = self.trackstar.max(axis = 0)
					r = self.trackstar.max(axis = 1)
					
					peakP = c.max() * 0.8
					count = 0
					peakY = 0
					
					for cc in range(0, len(c)):
						if c[cc] > peakP:
							peakY = peakY + cc
							count = count +1
					if count <> 0:
						peakY = 1.0 * peakY / count
					else:
						print ("Error count = 0, #111")
					
					count = 0
					peakX = 0
					for rr in range (0, len(r)):
						if r[rr] > peakP:
							peakX = peakX + rr
							count = count + 1
					
					if count > 0:
						peakX = 1.0 * peakX / count
					else:
						print ("Cannot find star!")
					
					if self.refX == 0:
						self.refX = peakX
						self.refY = peakY
					
					averageX = averageX + peakX * 1.00 - self.refX
					averageY = averageY + peakY * 1.00 - self.refY
					averageCount = averageCount + 1
					
					if averageCount == 5:
						averageCount = 0
					
					if peakY >= trackBoxR:
						peakY = trackBoxR
					if peakX > trackBoxC:
						peakX = trackBoxC

					if peakY < 0:
						peakY = 0
					if peakX < 0:
						peakX = 0
					
					self.offsetX = -1 * (peakY * 1.00 - self.refY)
					self.offsetY = -1 * (peakX * 1.00 - self.refX)
					print("OffsetX: " + str(peakY) + " ; OffsetY: " + str(peakX))
					iBox = 10
					cv2.line(self.trackstar, (0, trackBoxC / 2), (trackBoxR / 2 - iBox, trackBoxC / 2), 80, 1)
					cv2.line(self.trackstar, (trackBoxR / 2 + iBox, trackBoxC / 2), (trackBoxR, trackBoxC / 2), 80, 1)
					cv2.line(self.trackstar, (trackBoxR / 2, 0) , (trackBoxR / 2, trackBoxC / 2 - iBox), 80, 1)
					cv2.line(self.trackstar, (trackBoxR / 2, trackBoxC / 2 + iBox) , (trackBoxR / 2,trackBoxC), 80, 1)
					cv2.rectangle(self.trackstar, (trackBoxR / 2 - iBox, trackBoxC / 2 - iBox), (trackBoxR / 2 + iBox, trackBoxC / 2 + iBox), 125, 1)
					print("OffsetX: " + str(self.offsetX) + " ; OffsetY: " + str(self.offsetY))
					#cv2.imwrite("/home/pi/MyAutoguider/output_result/guiding_debug_" + str(i) + ".jpg", self.trackstar)
					
					if self.use_gpio:
						#Send correction to mount
						if self.offsetY > 1: #R+
							GPIO.output(self.RP, True)
						else:
							GPIO.output(self.RP, False)

						if self.offsetY < -1: #R-
							GPIO.output(self.RN, True)
						else:
							GPIO.output(self.RN, False)

						if self.offsetX > 1: #D+
							GPIO.output(self.DP, True)
						else:
							GPIO.output(self.DP, False)

						if self.offsetX < -1: #D-
							GPIO.output(self.DN, True)
						else:
							GPIO.output(self.DN, False)
					
				else:
					self.offsetX = 0.
					self.offsetY = 0.
					
				
			time.sleep(0.1)
