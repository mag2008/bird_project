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

#start Flask
app = Flask(__name__)

#makes an blackscrean with cputemperature on it
def cpu_tempreture_sensor():
	
	frame_height = 400
	frame_width = 600
	frame_thickness = 10
	text_position = (50, 50)  
	font = cv2.FONT_HERSHEY_SIMPLEX
	font_scale = 1
	color = (255, 255, 255) 
	thickness = 2
	cpu = CPUTemperature()
	
	while True:
		time.sleep(1)
		#create an black background
		frame = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)
		frame_with_frame = cv2.rectangle(frame, (0, 0), (frame_width - 1, frame_height - 1), (0, 0, 0), frame_thickness)
		
		#get cpu tempreture, you can see if the cpu is burning
		tempreture_value = cpu.temperature
		float_text = "Current CPU Tempreture is: {:.2f}".format(tempreture_value)
		frame_with_text = cv2.putText(frame_with_frame, float_text, text_position, font, font_scale, color, thickness)

		# Convert the image to JPEG format
		_, buffer = cv2.imencode('.jpg', frame_with_text)
		yield (b'--frame\r\n'
		   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

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
				if int(line) < 200:
					capture_event.wait()#if capturing video it waits
					change_camera.clear()#block capturing video
					v.change_device(1)
					time.sleep(0.5)
					change_camera.set()#releasing block, capture video is possible
					day = False
					
		while not day:
			if ser.in_waiting > 0:
				line = ser.readline().decode('utf-8').rstrip()
				#print(line)
				if int(line) > 200:
					capture_event.wait()
					change_camera.clear()
					v.change_device(0)
					time.sleep(0.5)
					change_camera.set()
					day = True
			
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
				
				print(self.text,'starting capturing...')
				# the change of camera should not trigger motion
				if change_camera.is_set():
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
		
#generate WAV to stream audio, does have some delay
def genHeader(sampleRate, bitsPerSample, channels, samples):
	datasize = 2064384000*2 # Some veeery big number here instead of: #samples * channels * bitsPerSample // 8
	o = bytes("RIFF",'ascii')                                               # (4byte) Marks file as RIFF
	o += (datasize + 36).to_bytes(4,'little')                               # (4byte) File size in bytes excluding this and RIFF marker
	o += bytes("WAVE",'ascii')                                              # (4byte) File type
	o += bytes("fmt ",'ascii')                                              # (4byte) Format Chunk Marker
	o += (16).to_bytes(4,'little')                                          # (4byte) Length of above format data
	o += (1).to_bytes(2,'little')                                           # (2byte) Format type (1 - PCM)
	o += (channels).to_bytes(2,'little')                                    # (2byte)
	o += (sampleRate).to_bytes(4,'little')                                  # (4byte)
	o += (sampleRate * channels * bitsPerSample // 8).to_bytes(4,'little')  # (4byte)
	o += (channels * bitsPerSample // 8).to_bytes(2,'little')               # (2byte)
	o += (bitsPerSample).to_bytes(2,'little')                               # (2byte)
	o += bytes("data",'ascii')                                              # (4byte) Data Chunk Marker
	o += (datasize).to_bytes(4,'little')                                    # (4byte) Data size in bytes
	return o
	
	
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
		self.start_streaming = True
		self.data = wav_header# data will be in WAV format
		self.data += self.stream.read(self.chunk_size)#get the audio frame
		yield(self.data)
		
		while True:
			
			self.http_frame = self.stream.read(self.chunk_size)
			self.data = self.http_frame
			if audio_q.full():
				audio_q.get() # remove frame from queue because queue is full
				#print('queue is full')
			audio_q.put_nowait(self.http_frame) # put the audio raw frame to the queue have some delay      
			yield(self.data)#send wav frame to web page
		
		
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
		
	def change_http_queue(self,new_delay):
		#change the delay by the frame number, new_delay stands for the new frame number
		self.video_delay_q = queue.Queue(maxsize=new_delay)
		
	def change_device(self,device_number):
		#change the camera by device_index
		self.vid = cv2.VideoCapture(device_number)
		
	def get_frame(self):
		#video stream
		global video_q, video_event
		video_event.set()
		while self.vid.isOpened():
			self.img,self.frame = self.vid.read()#get the video frames without any delay
			
			if self.video_delay_q.full():
				self.delayed_frame = self.video_delay_q.get()#get the video with delay
			self.video_delay_q.put_nowait(self.frame)#add the new frame at the end of the queue
			
			if video_q.full():
				video_q.get() # remove frame from queue because queue is full
				#print('queue is full')
			video_q.put_nowait(self.frame)#put the video frame without delay
			
			#convert the delayed video frame into jpg format and send it to the web page 
			self.ret, self.buffer = cv2.imencode('.jpg', self.delayed_frame)
			yield (b'--frame\r\n'
				   b'Content-Type: image/jpeg\r\n\r\n' + self.buffer.tobytes() + b'\r\n')
				   
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
				self.ftp.storbinary(f"STOR {self.video_filename[-18:]}", file)
				
			#sending the audio	
			self.ftp.cwd('/audio')
			self.target_path = '/audio/' + self.folder_name
			self.go_to_dir(self.target_path)
			with open(self.audio_filename, "rb") as file:
				# use FTP's STOR command to upload the file
				self.ftp.storbinary(f"STOR {self.audio_filename[-18:]}", file)
				
			#sending the merged file
			self.ftp.cwd('/both')
			self.target_path = '/both/' + self.folder_name
			self.go_to_dir(self.target_path)
			with open(self.both_filename, "rb") as file:
				# use FTP's STOR command to upload the file
				self.ftp.storbinary(f"STOR {self.both_filename[-18:]}", file)
				
			#remove all files from local storage
			os.remove(self.audio_filename)
			os.remove(self.video_filename)
			os.remove(self.both_filename)
			
	def go_to_dir(self,dir):
		#try to go to path, if not it will be created
		try:
			self.ftp.cwd(self.target_path)
		except:
			self.ftp.mkd(self.target_path)
			self.ftp.cwd(self.target_path)

#regulate the video stream delay				   
def regulate_video_delay(v):
	#video dely of stream can be changed at any time, to synchronize the audio and video exactely
	global video_event,audio_event,capture_event
	video_event.wait()
	audio_event.wait()
	
	while True:
		print('please enter delay value')
		answer= input()
		#the delay is adjusted by the frame number which is stored in a queue
		new_delay= int(float(answer)*30)
		v.change_http_queue(new_delay)
		print('successfully changed max_size to', new_delay)
		
wav_header = genHeader(RATE, bitsPerSample, CHANNELS, CHUNK)

#web adresses
@app.route('/audio_unlim')
def audio_unlim():
	# start Recording
	return Response(a.sound(), mimetype="audio/x-wav")
	
	
@app.route('/video_unlim')
def video_unlim():
	
	return Response(v.get_frame(),mimetype='multipart/x-mixed-replace; boundary=frame')
	
#cpu tempreture is displayed on a frame
@app.route('/tempreture')
def tempreture():
	return Response(cpu_tempreture_sensor(),mimetype='multipart/x-mixed-replace; boundary=frame')
	

# change the camera settings, they are stored in the bashscript
subprocess.call(["bash","/home/pi/Documents/v4l2_bash.sh"])
a = audio()
v = video(delay=3)
mo = motion()
ftp = ftp_server()

#start all threads
regulator = threading.Thread(target=regulate_video_delay, args=(v,))
voltage_sensor= threading.Thread(target=voltage)
motion_thread = threading.Thread(target=mo.start_motion_detection)
ftp_thread = threading.Thread(target=ftp.send_file)

motion_thread.start()
voltage_sensor.start()
regulator.start()
ftp_thread.start()

app.run(host='192.168.0.137', threaded=True,port=5000)
