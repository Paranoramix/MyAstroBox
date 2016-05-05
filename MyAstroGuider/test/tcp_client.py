import socket
import time
import os, sys
import select

MAXSIZE = 65535
TIMEOUT = 10
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("", 1111))

if len(sys.argv) == 2:
	s.send(sys.argv[1])

elif len(sys.argv) == 3:
	s.send(sys.argv[1] + " " + sys.argv[2])

elif len(sys.argv) == 4:
	s.send(sys.argv[1] + " " + sys.argv[2] + " " + sys.argv[3])

elif len(sys.argv) == 5:
	s.send(sys.argv[1] + " " + sys.argv[2] + " " + sys.argv[3] + " " + sys.argv[4])



if sys.argv[1] == "GET_CAMERA_IMG" or sys.argv[1] == "GET_CAMERA_IMG_DECORATED" or sys.argv[1] == "GET_TRACKING_IMG":
	r = ""
	gotData = select.select([s],[],[],TIMEOUT)
	if gotData[0]:
		while True:
			gotData2 = select.select([s],[],[],0.5)
			if gotData2[0]:
				moreData = s.recv(MAXSIZE)
				r += moreData
			else:
				break
	
	print (len(r))
	with open(sys.argv[1] + ".jpg", "wb") as _file:
		_file.write(r)
else:
	r = s.recv(1024)
	print(r)

s.close()

