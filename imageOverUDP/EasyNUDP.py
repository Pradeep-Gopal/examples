import urllib2
import numpy as np
import cv2
import time
from cv2 import cv
import socket


# A class to communicate with the EasyN IP Camera
class EasyN:

	#camera resolutions
	Resolutions = {
		"160x120": 2,
		"320x240": 8,
		"640x480": 32,
	}

	#camera frame rate
	Rate = {
		"full": 0,
		"20": 1,
		"15": 3,
		"10": 6,
		"5": 11,
		"4": 12,
		"3": 13,
		"2": 14,
		"1": 15,
		"1p2": 17,
		"1p3": 19,
		"1p4": 21,
		"1p5": 23,
	}

	# A Basic Class Constructor
	def __init__(self, ip, port, user, password, resolution=Resolutions["640x480"], frame_rate=Rate["20"], debug=True):
		self.ip = ip
		self.port = str(port)
		self.user = user
		self.password = password
		self.resolution = resolution
		self.frame_rate = frame_rate
		self._debug = debug
		self._connection = None
		self._connection_url = None
		# the header obtained via sniffing the reply
		self._stream_header = "--ipcamera\r\nContent-Type: image/jpeg\r\nContent-Length: "

	# A local function to generate the video stream url
	def _get_stream_url(self):
		return "http://%s:%s/videostream.cgi?user=%s&pwd=%s&resolution=%s&rate=%s" % (
			self.ip,
			self.port,
			self.user,
			self.password,
			self.resolution,
			self.frame_rate
		)

	# Open a Stream Connection to a url
	def _connect(self, url):

		if self._connection is None:
			self._connection_url = url
			self._connection = urllib2.urlopen(self._connection_url)
		else:
			if not self._connection_url == url:
				self._connection = None
				self._connection_url = url
				self._connection = urllib2.urlopen(self._connection_url)

	# Close a Connection
	def _close(self):
		self._connection = None
		self._connection_url = None
		
	# A user accessible close function
	def close(self):
		self._close()

	# Get a JPEG Image from the video stream
	def _get_stream_jpeg(self):
		image = None
		self._connect(self._get_stream_url())

		while True:
			restart = False
			# skip the observed header
			for item in self._stream_header:
				data = self._connection.read(1)
				if not data == item:
					restart = True
					if self._debug:
						print "skipping data", ord(data)
					break

			# if the header failed retry processing
			if restart:
				continue

			# get the length of the jpeg
			str_jpeg_length = ""
			while True:
				item = self._connection.read(1)
				if item == "\r":
					break
				else:
					str_jpeg_length += item

			# skip the last line LF and the next line CR LF combo (len('\r+\n+\r') = 3)
			item = self._connection.read(3)

			# now cast string to int
			jpeg_length = 0
			try:
				jpeg_length = int(str_jpeg_length)
			except ValueError:
				jpeg_length = 0

			# if zero this is bad so return None
			if jpeg_length == 0:
				return image

			#else read the image
			image = self._connection.read(jpeg_length)

			# skip the ending CR LF so the buffer is ready for a new jpeg reply
			item = self._connection.read(2)

			return image

	# get a single raw jpeg image from the camera
	def get_raw_frame(self, auto_close=True):
		image = self._get_stream_jpeg()
		if auto_close:
			self._close()
		return image

	# get a single jpeg image from the camera
	def get_frame(self, filename, auto_close=True):
		image = self._get_stream_jpeg()

		f = open(filename, 'wb')
		f.write(image)
		f.close()
		if auto_close:
			self._close()

	# get a number of images from the camera
	def get_frames(self, filename, number):
		count = 0
		while True:

			if count >= number:
				break

			self.get_frame(filename % (count), False)
			count += 1

		self._close()






if __name__ == "__main__":
## ---------- UDP Start ---------------
      UDP_IP = "127.0.0.1"
      UDP_PORT = 5005
#      MESSAGE = "Hello, World!"
      sock = socket.socket(socket.AF_INET, # Internet
                           socket.SOCK_DGRAM) # UDP
## ---------- UDP End -----------------



      ip = "192.168.11.172"
      port = 80
      user = "robot"
      password = "robot1234"


	# Demo 3 - Get 1 Raw Frame 
      ipCam = EasyN(ip,port,user,password)
      while(True):
	img_str = ipCam.get_raw_frame()

        sock.sendto(img_str, (UDP_IP, UDP_PORT))
      # CV2
        nparr = np.fromstring(img_str, np.uint8)
        frame = cv2.imdecode(nparr, cv2.CV_LOAD_IMAGE_COLOR)

    # Display the resulting frame
    # Convert BGR to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # define range of blue color in HSV
        lower_blue = np.array([110, 50, 50], dtype=np.uint8)
        upper_blue = np.array([130,255,255], dtype=np.uint8)


    # Threshold the HSV image to get only blue colors
        mask = cv2.inRange(hsv, lower_blue, upper_blue)

    # Bitwise-AND mask and original image
#    res = cv2.bitwise_and(frame,frame, mask= mask)

        cv2.imshow('frame',frame)
##        cv2.imshow('mask',mask)
#    cv2.imshow('res',res)





        cv2.imshow('frame',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
	   ipCam.close()
           break
