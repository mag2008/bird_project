#https://www.codespeedy.com/motion-detection-using-opencv-in-python/
#python bird_client_recorder/both_receiver4.py
import socket
import cv2
import pickle
import struct
import pyshine as ps
import threading
import time
import _thread
import sys
import soundfile as sf
import numpy as np
from queue import Queue
# Client socket
# create an INET, STREAMing socket : 

host_ip = '192.168.0.137'# Standard loopback interface address (localhost)
port = 4997 # Port to listen on (non-privileged ports are > 1023)
# now connect to the web server on the specified port number
server = (host_ip, port)
#'b' or 'B'produces an instance of the bytes type instead of the str type
#used in handling binary data from network connections
event = threading.Event()
class motion:
    def __init__(self):
        self.text = "nomotion"
        self.recording_time = 10
        self.fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for the output video (XVID is a common choice)
        
        self.frame_number = 0
        self.row = 0
    def start_motiondetection(self, video_q, audio_q):
        try:
            #while not v.return_status():
                #pass
            time.sleep(5)
            self.frame1= v.video_frame()# making the background image

            self.gray1 = cv2.cvtColor(self.frame1, cv2.COLOR_BGR2GRAY)
            self.gray1 = cv2.GaussianBlur(self.gray1, (21, 21), 0)
            #cv2.imshow('window',self.frame1)
        
       
            while(True):
                #if ch.return_check():
                    #print('event is set')
                    #sys.exit()
                self.text = "nomotion"
                time.sleep(0.5)
                
                self.frame2=v.video_frame()

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
                    #print(self.row)
                    
                if self.text == "motion":
                    print(self.text)
                    print('starting capturing...')
                    self.timestr = time.strftime("%Y%m%d-%H%M%S")
                    video_record = threading.Thread(target=self.record_video)
                    audio_record = threading.Thread(target=self.record_audio)
                    video_record.start()
                    audio_record.start()
                    video_record.join()
                    audio_record.join()
                    print('finish recording')
                #cv2.putText(self.frame2,"Room Status: {}".format(self.text),(10, 20),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                #cv2.imshow('window',self.frame2)
                #self.row += 1
                if cv2.waitKey(20) == ord('q'):
                    break
            
            
            cv2.destroyAllWindows()
        except Exception as e:
            print(f"An exception occurred: {type(e).__name__}")
            print(f"Exception details: {e}")
            print('error occured1')
            event.set()
            sys.exit()
    def return_status(self):
        return self.text 
    def record_video(self):
        
        self.video_outputfile = self.timestr + '.mp4'
        self.out = cv2.VideoWriter(outputfile, self.fourcc, 10.0, (640, 480))
        self.end_time = time.time() + self.recording_time
        while time.time()< self.end_time:
            #self.one_frame_time = time.time() + 1/30
            #self.current_frame = v.movie_frame()
            #while self.one_frame_time > time.time():pass # trying capturing only one frame per 1/30 second
            #while "None" in str(type(self.current_frame)):
                #print('no frame')
            
            #print('recorded one frame')
            self.current_frame = video_q.get()
            self.out.write(self.current_frame)
            #self.frame_number += 1
            #else:
                #print('queue is empty')


        #print(self.frame_number)
        #self.frame_number = 0
        self.out.release() #necessary to make video file
    def record_audio(self):
        self.audio_outputfile = self.timestr + '.wav'
        self.end_time = time.time() + self.record_time
        self.audio_frames = audio_q.get()
        while time.time()< self.end_time:
            self.audio_frame = q.get()
            self.audio_frames = np.concatenate((self.audio_frames, self.audio_frame), axis=0,dtype=np.float32)
        sf.write(self.audio_outputfile, self.audio_frames, 48000)
        
'''
class movie:
    def __init__(self):
        self.recording_time = 5
        self.fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for the output video (XVID is a common choice)
        self.out = cv2.VideoWriter('output2.mp4', self.fourcc, 30.0, (640, 480))
        self.i = 0
    def capture(self):
        
        try:
            time.sleep(5)
            #while not v.return_status():
             #   pass
            print('starting thread movie')
            while True:
                #if ch.return_check():
                 #   print('event is set')                    
                  #  sys.exit()
                if mo.return_status() == "motion":
                    print('starting capturing...')
                    #print(v.video_frame())
                    #print(self.previous_frame)
                    self.end_time = time.time() + self.recording_time
                    while time.time()< self.end_time:
                        #self.one_frame_time = time.time() + 1/30
                        #self.current_frame = v.video_frame()
                        #while self.one_frame_time > time.time():pass # trying capturing only one frame per 1/30 second
                        if "None" in str(type(self.current_frame)):
                            print('no frame')
                        if not q.empty():
                            self.current_frame = q.get()
                            self.out.write(self.current_frame)
                            self.i += 1

                    self.out.release() 
                    print(self.i)
        except Exception as e:
            print(f"An exception occurred: {type(e).__name__}")
            print(f"Exception details: {e}")
            print('error occured2')
            sys.exit()
            
        '''        
class video:
    def __init__(self):
        self.data = b""
        self.previous_number = None
        self.frame_number = 0
        self.started = False
# Q: unsigned long long integer(8 bytes)
        self.payload_size = struct.calcsize("Q")
    def video_frame(self):
        return(self.frame) 
    
    def return_status(self):
        return self.started
    
        
    def video_streamer(self, server,q):
       # try:
        time.sleep(0.1)
        self.client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.client_socket.connect(server) 
        self.calc_frame_rate = time.time() + 1
        self.first = True
        self.first_2 = True
        while True:  
            #downloading package
            while len(self.data) < self.payload_size:
                self.packet = self.client_socket.recv(4*1024)
                if not self.packet: break
                self.data+=self.packet
            
            #turn package in opencv-frame
            self.packed_msg_size = self.data[:self.payload_size]
            self.data = self.data[self.payload_size:]
            self.msg_size = struct.unpack("Q",self.packed_msg_size)[0]
            while len(self.data) < self.msg_size:
                self.data += self.client_socket.recv(4*1024)
            self.frame_data = self.data[:self.msg_size]
            self.data  = self.data[self.msg_size:]
            self.frame = pickle.loads(self.frame_data)
            
            
            #put the frame into a queue
            if q.full():
                q.get() # remove frame from queue because queue is full
                #print('queue is full')
            q.put_nowait(self.frame)
            
            #calculate framerate
            self.frame_number += 1
            if time.time() > self.calc_frame_rate:
                #print(str(self.frame_number) + "frames per second")
                self.frame_number = 0
                self.calc_frame_rate = time.time() + 1
                
            cv2.imshow("Receiving...",self.frame)
            self.key = cv2.waitKey(10) 
            if self.key  == 13:
                break
        self.client_socket.close()
'''
        except Exception as e:
            print(f"An exception occurred: {type(e).__name__}")
            print(f"Exception details: {e}")
            print('error occured3')
            _thread.interrupt_main()
            event.set()
            sys.exit()'''
class audio:
    def __init__(self):
        self.frame_number = 0
        self.mode =  'get'
        self.name = 'CLIENT RECEIVING AUDIO'
        self.audio,self.context = ps.audioCapture(mode=self.mode)
        ps.showPlot(self.context,self.name)
        self.payload_size = struct.calcsize("Q")
        self.first = True
        self.record = False
    def record_audio(self,q):
        time.sleep(5)
        
        self.record_time = 5
        print('start recording')
        self.end_time = time.time() + self.record_time
        self.audio_frames = q.get()
        while time.time()< self.end_time:
            self.audio_frame = q.get()
            self.audio_frames = np.concatenate((self.audio_frames, self.audio_frame), axis=0,dtype=np.float32)
        sf.write('stereo_file.wav', self.audio_frames, 48000)
        
        print('finish recording')
    def audio_streamer(self, server,q):
       
        # create socket
        self.client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.host_ip , self.port= server
        self.port += 1

        self.socket_address = (self.host_ip,self.port)
        self.client_socket.connect(self.socket_address) 
        print("CLIENT CONNECTED TO",self.socket_address)
        self.data = b""
        
        self.calc_frame_rate = time.time() + 1
        #print(self.payload_size)

        while True:
            while len(self.data) < self.payload_size:
                #print('1')
                self.packet = self.client_socket.recv(4*1024) # 4K
                if not self.packet: break
                self.data+=self.packet
            self.packed_msg_size = self.data[:self.payload_size]
            self.data = self.data[self.payload_size:]
            self.msg_size = struct.unpack("Q",self.packed_msg_size)[0]

            while len(self.data) < self.msg_size:
                self.data += self.client_socket.recv(4*1024)
            self.frame_data = self.data[:self.msg_size]
            self.data  = self.data[self.msg_size:]
            self.frame = pickle.loads(self.frame_data)
            self.audio.put(self.frame)
           # if self.record:
               # self.audio_frames = np.concatenate((self.audio_frames, self.frame), axis=0,dtype=np.float32)
            if q.full():
                q.get() # remove frame from queue because queue is full
                #print('queue is full')
            q.put_nowait(self.frame)
          #  if self.first:
               # self.audio_frames = self.frame
                #print(str(type(self.frame)))
                #print(self.frame)
                #self.format = self.frame.dtype
                #print(self.format)
                #self.first = False
            self.frame_number += 1
            if time.time() > self.calc_frame_rate:
                print(self.frame_number, "frames per second")
                self.frame_number = 0
                self.calc_frame_rate = time.time() + 1
        self.client_socket.close()
        
queue_for_video = Queue(maxsize = 30)
queue_for_audio = Queue(maxsize = 10)

a = audio()
v = video()
mo = motion()

audio_thread = threading.Thread(target=a.audio_streamer, args=(server,queue_for_audio,))
video_thread = threading.Thread(target=v.video_streamer, args=(server,queue_for_video,))
motion_thread = threading.Thread(target=mo.start_motiondetection, args=(queue_for_video,))



audio_thread.start()
video_thread.start()
motion_thread.start()

motion_thread.join()
audio_thread.join()
video_thread.join()
