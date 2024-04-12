import  cv2,time, threading, wave, pyaudio,queue,sys,subprocess,os,datetime,serial
from flask import Flask, Response
import numpy as np
from gpiozero import CPUTemperature
from ftplib import FTP

#audio settings
CHUNK = 1024 
RATE = 48000
bitsPerSample = 16 
CHANNELS = 2
FORMAT = pyaudio.paInt16

# threading events work between threads
video_event = threading.Event()
audio_event = threading.Event()
capture_event = threading.Event()
change_camera = threading.Event()
created_new_file = threading.Event()

# make the global queues 	
audio_q= queue.Queue(maxsize=48)
video_q = queue.Queue(maxsize=30)
recorded_audio= queue.Queue()
recorded_video= queue.Queue()
recorded_both = queue.Queue()



#makes an blackscrean with cputemperature on it
def cpu_tempreture_sensor():
	
	
	cpu = CPUTemperature()
	
	while True:
		time.sleep(1)
		
		#get cpu tempreture, you can see if the cpu is burning
		tempreture_value = cpu.temperature
		if int(tempreture_value)>75:
			print('high tempreture warning')
		

#measures voltage of solarpanel to look wether it is day or night		   
def voltage():
	global capture_event, change_camera
	day = True
	#connect with arduino
	ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
	ser.reset_input_buffer()
	change_camera.set()#no change in camera
	time.sleep(1)
	# measuring the voltage if lower than 200 it is to dark so the day camera is switched to ir night camera
	while True:
		while day:
			if ser.in_waiting > 0:
				line = ser.readline().decode('utf-8').rstrip()
				#print(line)
				if int(line) < 800:
					capture_event.wait()#if capturing video it waits
					change_camera.clear()#block capturing video
					v.change_device(1)
					time.sleep(2)#delay nessesary
					change_camera.set()#releasing block, capture video is possible
					day = False
		print("changed camera")			
		while not day:
			if ser.in_waiting > 0:
				line = ser.readline().decode('utf-8').rstrip()
				#print(line)
				if int(line) > 800:
					capture_event.wait()
					change_camera.clear()
					v.change_device(0)
					time.sleep(2)
					change_camera.set()
					day = True
		print("changed camera")	
class motion:
	def __init__(self):
		global video_event, audio_event,capture_event,change_camera
	def start_motion_detection(self):
		
		#wait for audio and video to be streamed
		video_event.wait()
		audio_event.wait()
		capture_event.set()#meaning that no videos are captured
		print('started...')
   
		while(True):
			#compare the frames between 0.5 seconds every time
			self.detect_motion(0.5)
			if self.text == "motion":
				
				print(self.text)
				# the change of camera should not trigger motion
				if change_camera.is_set():
					print('start recording')
					#starts recording, whole process happens in the initialization
					record_class = record()
	def detect_motion(self,delay):
		#https://www.codespeedy.com/motion-detection-using-opencv-in-python/
		# making the background image
		self.frame1= v.return_frame()
		self.gray1 = cv2.cvtColor(self.frame1, cv2.COLOR_BGR2GRAY)#makes the ficture gray
		self.gray1 = cv2.GaussianBlur(self.gray1, (21, 21), 0)#and then blurry
		self.text = "nomotion"
		time.sleep(delay)
		self.frame2=v.return_frame()
		self.gray2 = cv2.cvtColor(self.frame2, cv2.COLOR_BGR2GRAY)
		self.gray2 = cv2.GaussianBlur(self.gray2, (21, 21), 0)
		self.deltaframe=cv2.absdiff(self.gray1,self.gray2)#the difference is showed here
		#cv2.imshow('delta',self.deltaframe)
		self.threshold = cv2.threshold(self.deltaframe, 25, 255, cv2.THRESH_BINARY)[1]
		self.threshold = cv2.dilate(self.threshold,None)
		#cv2.imshow('threshold',self.threshold)
		self.countour,self.heirarchy = cv2.findContours(self.threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		for self.i in self.countour:
			if cv2.contourArea(self.i) < 50:
				continue
			#uncomment to add red boundary were the motion object
			#(self.x,self. y, self.w, self.h) = cv2.boundingRect(self.i)
			#cv2.rectangle(self.frame2, (self.x, self.y), (self.x + self.w, self.y + self.h), (255, 0, 0), 2)
			
			#motion was detected
			self.text = "motion"
		#cv2.putText(self.frame2,"Room Status: {}".format(self.text),(10, 20),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
		#cv2.imshow('window',self.frame2)
		
		#if cv2.waitKey(20) == ord('q'):
			#break
			
		
		#cv2.destroyAllWindows()
		#print(self.text)
	def return_status(self):
		return self.text 
		
	def motion_duration(self):
		#is looking for motion until we no motion is detected anymore
		self.motion_number = 0
		time.sleep(3)#minimum video length
		while not capture_event.is_set():
			self.detect_motion(0.5)
			if self.text == "nomotion":
				capture_event.set()	
			#print(self.text)
class record:
	def __init__(self):
		global capture_event,mo, created_new_file,recorded_audio,recorded_video,recorded_both
		capture_event.clear()
		
		# distributing the year,month, day to all directories
		self.current_date = datetime.datetime.now()
		self.date = self.current_date.strftime("%m-%d-%Y")
		self.path_to_video_date = '/home/pi/FTP/video/' + self.date
		self.path_to_audio_date = '/home/pi/FTP/audio/' + self.date
		self.path_to_both_date = '/home/pi/FTP/both/' + self.date
		
		#make the date directory
		if not os.path.exists(self.path_to_video_date):
			os.mkdir(self.path_to_video_date)
		if not os.path.exists(self.path_to_audio_date):
			os.mkdir(self.path_to_audio_date)
		if not os.path.exists(self.path_to_both_date):
			os.mkdir(self.path_to_both_date)
			
		#start the opencv video writer
		self.fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Codec for the output video (XVID is a common choice)
		self.timestr = time.strftime("%Y%m%d-%H%M%S")
		self.video_output_filename = self.path_to_video_date + '/' + self.timestr + '.avi'
		self.out = cv2.VideoWriter(self.video_output_filename, self.fourcc, 30.0, (640, 480))
		
		#start recording the video and audio simultaniously , they have no delay
		video_record = threading.Thread(target=self.record_video)
		audio_record = threading.Thread(target=self.record_audio)
		motion_duration = threading.Thread(target=mo.motion_duration)
		motion_duration.start()# records until no motion anymore
		video_record.start()#start audio and video recording
		audio_record.start()
		video_record.join()
		audio_record.join()
		capture_event.set()#release the event, video ended
		
		#put the paths in a queue, for the ftp transmittion
		recorded_audio.put(self.audio_output_filename)
		recorded_video.put(self.video_output_filename)
		recorded_both.put(self.output_filename)
		created_new_file.set()#triggers the ftp file transfer
		
	def record_video(self):
		global video_q,capture_event
		
		#record the video until no motion is found anymore
		while not capture_event.is_set(): 
			self.current_frame = video_q.get()#gets the video frame directly from the stream with no delay
			self.out.write(self.current_frame)# write the frame to the video writer 
			
		self.out.release() #necessary to make video file
		
		
	def record_audio(self):
		global audio_q, CHANNELS, FORMAT, RATE, CHUNK,capture_event
		self.audio_counter = 0
		self.frames = []
		
		# write the audio frmaes to an array
		while not capture_event.is_set():
			self.audio_frame = audio_q.get()# get the audio frame without delay
			self.frames.append(self.audio_frame)#append it to the array
			
		# save the array as a WAV data		
		self.audio_output_filename = self.path_to_audio_date + '/' + self.timestr + '.wav'
		wf = wave.open(self.audio_output_filename, 'wb')
		wf.setnchannels(CHANNELS)
		wf.setsampwidth(a.audio.get_sample_size(FORMAT))
		wf.setframerate(RATE)
		wf.writeframes(b''.join(self.frames))
		wf.close()
		
		#merge video with audio, should be no delay, use subprocess to execute ffmpeg command
		self.output_filename = self.path_to_both_date +'/' + self.timestr + '.mp4'
		subprocess.call(["sudo","ffmpeg", "-i",self.video_output_filename , "-i", self.audio_output_filename, "-c:v", "copy", "-c:a", "aac", self.output_filename])
		print('finish recording')

	
class audio:
	def __init__(self):
		global CHUNK,RATE,CHANNELS,FORMAT
		self.chunk_size = CHUNK
		self.sample_rate = RATE
		self.channels = CHANNELS
		self.format = FORMAT
		self.http_frame = None
		
		#start the audio device with pyaudio, audio device can be specified with input_device_index at the end
		self.audio = pyaudio.PyAudio()
		self.stream = self.audio.open(format=self.format,
							channels=self.channels,
							rate=self.sample_rate,
							input=True,
							frames_per_buffer=self.chunk_size)
		
		
	def sound(self):
		global audio_q, audio_event
		audio_event.set()
		
		
		while True:
			
			self.http_frame = self.stream.read(self.chunk_size)
			if audio_q.full():
				audio_q.get() # remove frame from queue because queue is full
				#print('queue is full')
			audio_q.put_nowait(self.http_frame) # put the audio raw frame to the queue have some delay      
		
		
class video:
	def __init__(self,delay):
		# start video with device index '0', delay queue to synchronise video and audio for the stream -> default delay is 3 sec
		self.maxsize = delay*30
		self.video_delay_q = queue.Queue(maxsize=self.maxsize)
		self.vid = cv2.VideoCapture(0)
		
		# fill the delay queue with video frames
		while not self.video_delay_q.full():
			self.img,self.frame = self.vid.read()
			self.video_delay_q.put_nowait(self.frame)
			
	def return_frame(self):
		return self.frame
		
	
	def change_device(self,device_number):
		#change the camera by device_index
		self.vid = cv2.VideoCapture(device_number)
		
	def get_frame(self):
		#video stream
		global video_q, video_event
		video_event.set()
		while self.vid.isOpened():
			self.img,self.frame = self.vid.read()#get the video frames without any delay
			
			
			if video_q.full():
				video_q.get() # remove frame from queue because queue is full
				#print('queue is full')
			video_q.put_nowait(self.frame)#put the video frame without delay
		  #time.sleep(0.1)
				   
class ftp_server:
	def __init__(self):
		# connect to ftp
		self.ftp = FTP('192.168.0.38')  
		self.ftp.login(user='pi',passwd="yBV4Lq'C")     
		global recorded_audio,recorded_video,recorded_both#call all events
		
	def send_file(self):
		while True:
			#wait_until new file is created
			created_new_file.wait()
			created_new_file.clear()
			self.audio_filename = recorded_audio.get()
			self.video_filename = recorded_video.get()
			self.both_filename= recorded_both.get()
			self.folder_name = self.both_filename[18:28]
			#print(self.folder_name)
			
			#sending the video file
			self.ftp.cwd('/video')
			self.target_path = '/video/' + self.folder_name
			self.go_to_dir(self.target_path)
			with open(self.video_filename, "rb") as file:
				# use FTP's STOR command to upload the file
				self.ftp.storbinary(f"STOR {self.video_filename[-19:]}", file)
				
			#sending the audio	
			self.ftp.cwd('/audio')
			self.target_path = '/audio/' + self.folder_name
			self.go_to_dir(self.target_path)
			with open(self.audio_filename, "rb") as file:
				# use FTP's STOR command to upload the file
				self.ftp.storbinary(f"STOR {self.audio_filename[-19:]}", file)
				
			#sending the merged file
			self.ftp.cwd('/both')
			self.target_path = '/both/' + self.folder_name
			self.go_to_dir(self.target_path)
			with open(self.both_filename, "rb") as file:
				# use FTP's STOR command to upload the file
				self.ftp.storbinary(f"STOR {self.both_filename[-19:]}", file)
				
			#remove all files from local storage
			os.remove(self.audio_filename)
			os.remove(self.video_filename)
			os.remove(self.both_filename)
			
	def go_to_dir(self,dir):
		#try to go to path, if not it will be created
		try:
			self.ftp.cwd(dir)
		except:
			self.ftp.mkd(dir)
			self.ftp.cwd(dir)

#regulate the video stream delay				   

		


	

# change the camera settings, they are stored in the bashscript
subprocess.call(["bash","/home/pi/Documents/v4l2_bash.sh"])
a = audio()
v = video(delay=3)
mo = motion()
ftp = ftp_server()

#start all threads
tempreture_sensor = threading.Thread(target=cpu_tempreture_sensor)
voltage_sensor= threading.Thread(target=voltage)
motion_thread = threading.Thread(target=mo.start_motion_detection)
ftp_thread = threading.Thread(target=ftp.send_file)
audio_thread = threading.Thread(target=a.sound)
video_thread = threading.Thread(target=v.get_frame)

audio_thread.start()
video_thread.start()
motion_thread.start()
voltage_sensor.start()
ftp_thread.start()
tempreture_sensor.start()
