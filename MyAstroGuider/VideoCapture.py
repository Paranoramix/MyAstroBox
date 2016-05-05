#!/usr/bin/env python
# coding: utf-8 
# import the necessary packages
import imutils
from imutils.video import WebcamVideoStream


class VideoStream:
	""" Unifying picamera and cv2.VideoCapture into a single class with OpenCV
	    http://www.pyimagesearch.com/2016/01/04/unifying-picamera-and-cv2-videocapture-into-a-single-class-with-opencv/
	"""
	
	def __init__(self, src = 0, usePiCamera = False, resolution = (320, 240), framerate = 32):
		# Check to see if the PiCamera module should be used.
		if usePiCamera:
			# only import the picamera packages unless we are
			# explicity told to do so -- this helps remove the
			# requirement of `picamera[array]` from desktops or
			# laptops that still want to use the `imutils` package			
			from imutils.video.pivideostream import PiVideoStream
			# initialize the picamera stream and allow the camera
			# sensor to warmup
			self.stream = PiVideoStream(resolution = resolution, framerate = framerate)

		else:
			# otherwise, we are using OpenCV so initialize the webcam
			# stream
			self.stream = WebcamVideoStream(src = src)
	
	def start(self):
		# start the threaded video stream
		return self.stream.start()
 
	def update(self):
		# grab the next frame from the stream
		self.stream.update()
 
	def read(self):
		# return the current frame
		return self.stream.read()
 
	def stop(self):
		# stop the thread and release any resources
		self.stream.stop()
 