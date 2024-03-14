import socket, cv2, pickle,struct,time, threading, wave, pyaudio,queue,sys,subprocess,os,datetime,serial
from flask import Flask, Response,render_template
import numpy as np
from gpiozero import CPUTemperature

CHUNK = 1024 
RATE = 48000
bitsPerSample = 16 
CHANNELS = 2
FORMAT = pyaudio.paInt16

video_event = threading.Event()
audio_event = threading.Event()
capture_event = threading.Event()

app = Flask(__name__)


def cpu_tempreture_sensor():
	
	self.frame_height = 400
	self.frame_width = 600
	self.frame_thickness = 10
	self.text_position = (50, 50)  
	self.font = cv2.FONT_HERSHEY_SIMPLEX
	self.font_scale = 1
	self.color = (255, 255, 255) 
	self.thickness = 2
	self.cpu = CPUTemperature()
	
	
	while True:
		time.sleep(1)
	
		self.frame = np.zeros((self.frame_height, self.frame_width, 3), dtype=np.uint8)
		self.frame_with_frame = cv2.rectangle(self.frame, (0, 0), (self.frame_width - 1, self.frame_height - 1), (0, 0, 0), self.frame_thickness)
		
		self.tempreture_value = self.cpu.tempreture
		self.float_text = "Current CPU Tempreture is: {:.2f}".format(self.tempreture_value)
		self.frame_with_text = cv2.putText(self.frame_with_frame, self.float_text, self.text_position, self.font, self.font_scale, self.color, self.thickness)

		# Convert the image to JPEG format
		_, self.buffer = cv2.imencode('.jpg', self.frame_with_text)
		yield (b'--frame\r\n'
		   b'Content-Type: image/jpeg\r\n\r\n' + self.buffer.tobytes() + b'\r\n')
		   
def voltage():
	day = True
	#connect with arduino
	ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
	ser.reset_input_buffer()

	
	# Encode the frame as bytes
	while True:
		while day:
			time.sleep(1)
			if ser.in_waiting > 0:
				line = ser.readline().decode('utf-8').rstrip()
				print(line)
				if int(line) < 200:
					v.change_device(1)
					day = False
		while not day:
			time.sleep(1)
			if ser.in_waiting > 0:
				line = ser.readline().decode('utf-8').rstrip()
				print(line)
				if int(line) > 200:
					v.change_device(0)
					day = True
			
class motion:
	def __init__(self):
		
		global video_event, audio_event,capture_event
	def start_motiondetection(self):
		
		#wait for event
		video_event.wait()
		audio_event.wait()
		capture_event.set()
		time.sleep(1)
		
		print('started...')
   
		while(True):
			
			self.detect_motion(0.5)
			
			
			if self.text == "motion":
				print(self.text)
				print('starting capturing...')
				record_class = record()
	def detect_motion(self,delay):
		self.frame1= v.return_frame()# making the background image

		self.gray1 = cv2.cvtColor(self.frame1, cv2.COLOR_BGR2GRAY)
		self.gray1 = cv2.GaussianBlur(self.gray1, (21, 21), 0)
		self.text = "nomotion"
		time.sleep(delay)
		self.frame2=v.return_frame()
		#print('working2')
		
		self.gray2 = cv2.cvtColor(self.frame2, cv2.COLOR_BGR2GRAY)
		self.gray2 = cv2.GaussianBlur(self.gray2, (21, 21), 0)

		self.deltaframe=cv2.absdiff(self.gray1,self.gray2)
		#cv2.imshow('delta',self.deltaframe)
		self.threshold = cv2.threshold(self.deltaframe, 25, 255, cv2.THRESH_BINARY)[1]
		self.threshold = cv2.dilate(self.threshold,None)
		#cv2.imshow('threshold',self.threshold)
		self.countour,self.heirarchy = cv2.findContours(self.threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		for self.i in self.countour:
			if cv2.contourArea(self.i) < 50:
				continue

			#(self.x,self. y, self.w, self.h) = cv2.boundingRect(self.i)
			#cv2.rectangle(self.frame2, (self.x, self.y), (self.x + self.w, self.y + self.h), (255, 0, 0), 2)
			self.text = "motion"
		   
			
		
		#cv2.putText(self.frame2,"Room Status: {}".format(self.text),(10, 20),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
		#cv2.imshow('window',self.frame2)
		
		#if cv2.waitKey(20) == ord('q'):
			#break
			
		
		#cv2.destroyAllWindows()
		print(self.text)
	def return_status(self):
		return self.text 
		
	def motion_duration(self):
		while not capture_event.is_set():
			self.detect_motion(0.5)
			if self.text == "nomotion":
				capture_event.set()	
			print(self.text)
class record:
	def __init__(self):
		global capture_event,mo
		capture_event.clear()
		
		self.fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Codec for the output video (XVID is a common choice)
		self.timestr = time.strftime("%Y%m%d-%H%M%S")
		self.video_output_filename = '/home/pi/FTP/video/'+ self.timestr + '.avi'
		self.out = cv2.VideoWriter(self.video_output_filename, self.fourcc, 30.0, (640, 480))
		video_record = threading.Thread(target=self.record_video)
		audio_record = threading.Thread(target=self.record_audio)
		motion_duration = threading.Thread(target=mo.motion_duration)
		motion_duration.start()
		video_record.start()#start audio and video recording
		audio_record.start()
		video_record.join()
		audio_record.join()
		capture_event.set()
		
	def record_video(self):
		global video_q,capture_event
		self.video_counter = 0
		self.video_start_time = datetime.datetime.now()
		while not capture_event.is_set():   
			self.current_frame = video_q.get()
			self.out.write(self.current_frame)  
			self.video_counter += 1    
		self.out.release() #necessary to make video file
		
		
	def record_audio(self):
		global audio_q, CHANNELS, FORMAT, RATE, CHUNK,capture_event
		self.audio_counter = 0
		self.frames = []
		self.frame_number = 0
		self.calc_frame_rate = time.time() + 1
		while not capture_event.is_set():
			self.audio_frame = audio_q.get()
			self.frames.append(self.audio_frame)
			
			
			self.frame_number += 1
			if time.time() > self.calc_frame_rate:
				print(self.frame_number,"frames per second")
				self.frame_number = 0
				self.calc_frame_rate = time.time() + 1
			
		self.audio_output_filename = '/home/pi/FTP/audio/'+self.timestr + '.wav'
		wf = wave.open(self.audio_output_filename, 'wb')
		wf.setnchannels(CHANNELS)
		wf.setsampwidth(a.audio.get_sample_size(FORMAT))
		wf.setframerate(RATE)
		wf.writeframes(b''.join(self.frames))
		wf.close()
		self.output_filename ='/home/pi/FTP/both/' + self.timestr + 'both.mp4'
		subprocess.call(["sudo","ffmpeg", "-i",self.video_output_filename , "-i", self.audio_output_filename, "-c:v", "copy", "-c:a", "aac", self.output_filename])
		
		
		#os.remove(self.video_output_filename)
		#os.remove(self.audio_output_filename)
		#subprocess.call(["sudo", "rm", self.video_output_filename])
		#subprocess.call(["sudo", "rm", self.audio_output_filename])

		print('finish recording')
		print('video frame number is', self.video_counter)
		print('audio frame number is', self.frame_number)
		

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
		self.data = wav_header
		self.frame_number = 0
		self.data += self.stream.read(self.chunk_size)
		yield(self.data)
		
		while True:
			
			self.http_frame = self.stream.read(self.chunk_size)
			self.data = self.http_frame
			if audio_q.full():
				audio_q.get() # remove frame from queue because queue is full
				#print('queue is full')
			audio_q.put_nowait(self.http_frame)        
			yield(self.data)
		
		
class video:
	def __init__(self,delay):
		self.maxsize = delay*30
		self.video_delay_q = queue.Queue(maxsize=self.maxsize)
		self.vid = cv2.VideoCapture(0)
		
		while not self.video_delay_q.full():
			self.img,self.frame = self.vid.read()
			self.video_delay_q.put_nowait(self.frame)
			
			
	def return_frame(self):
		return self.frame
		
	def change_http_queue(self,new_delay):
		self.video_delay_q = queue.Queue(maxsize=new_delay )
		
	def change_device(self,device_number):
		self.vid = cv2.VideoCapture(device_number)
		
	def get_frame(self):
		global video_q, video_event
		video_event.set()
		while self.vid.isOpened():
			self.img,self.frame = self.vid.read()
			if self.video_delay_q.full():
				self.delayed_frame = self.video_delay_q.get()
			self.video_delay_q.put_nowait(self.frame)
			if video_q.full():
				video_q.get() # remove frame from queue because queue is full
				#print('queue is full')
			video_q.put_nowait(self.frame)
			
			self.ret, self.buffer = cv2.imencode('.jpg', self.delayed_frame)
			yield (b'--frame\r\n'
				   b'Content-Type: image/jpeg\r\n\r\n' + self.buffer.tobytes() + b'\r\n')
				   
				   
def regulate_video_delay(v):
	global video_event,audio_event
	video_event.wait()
	audio_event.wait()
	while True:
		print('please enter delay value')
		answer= input()
		#if answer == "end":
			#print('successfully synchronized')
			#regulation_event.set()
			#sys.exit()
		new_delay= float(answer)*30
		
		v.change_http_queue(int(new_delay))
		print('successfully changed max_size to', int(new_delay))
		
wav_header = genHeader(RATE, bitsPerSample, CHANNELS, CHUNK)


@app.route('/audio_unlim')
def audio_unlim():
	# start Recording
	return Response(a.sound(), mimetype="audio/x-wav")
	
	
@app.route('/video_unlim')
def video_unlim():
	
	return Response(v.get_frame(),mimetype='multipart/x-mixed-replace; boundary=frame')
	
	
@app.route('/tempreture')
def tempreture():
	return Response(cpu_tempreture_sensor(),mimetype='multipart/x-mixed-replace; boundary=frame')
	
	
audio_q= queue.Queue(maxsize=48)
video_q = queue.Queue(maxsize=30)


if __name__ == "__main__":
	a = audio()
	v = video(delay=3)
	mo = motion()
	
	regulator = threading.Thread(target=regulate_video_delay, args=(v,))
	voltage_sensor= threading.Thread(target=voltage)
	motion_thread = threading.Thread(target=mo.start_motiondetection)
	
	motion_thread.start()
	voltage_sensor.start()
	
	regulator.start()
	app.run(host='192.168.0.137', threaded=True,port=5000)



