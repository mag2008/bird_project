import socket
import cv2
import pickle
import struct
import pyshine as ps
import threading
import time
# Client socket
# create an INET, STREAMing socket : 

host_ip = '192.168.0.137'# Standard loopback interface address (localhost)
port = 4997 # Port to listen on (non-privileged ports are > 1023)
# now connect to the web server on the specified port number
server = (host_ip, port)
#'b' or 'B'produces an instance of the bytes type instead of the str type
#used in handling binary data from network connections
class motion:
  def __init__(self):
    



self.frame1= v.video_frame() making the background image

self.gray1 = cv2.cvtColor(self.frame1, cv2.COLOR_BGR2GRAY)
self.gray1 = cv2.GaussianBlur(self.gray1, (21, 21), 0)
cv2.imshow('window',self.frame1)

while(True):
    self.frame2=v.video_frame()

    self.gray2 = cv2.cvtColor(self.frame2, cv2.COLOR_BGR2GRAY)
    self.gray2 = cv2.GaussianBlur(self.gray2, (21, 21), 0)
    
    self.deltaframe=cv2.absdiff(self.gray1,self.gray2)
    cv2.imshow('delta',self.deltaframe)
    self.threshold = cv2.threshold(self.deltaframe, 25, 255, cv2.THRESH_BINARY)[1]
    self threshold = cv2.dilate(self.threshold,None)
    cv2.imshow('threshold',self.threshold)
    self.countour,self.heirarchy = cv2.findContours(self.threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for self.i in self.countour:
        if cv2.contourArea(self.i) < 50:
            continue
 
        (self.x,self. y, self.w, self.h) = cv2.boundingRect(self.i)
        cv2.rectangle(self.frame2, (self.x, self.y), (self.x + self.w, self.y + self.h), (255, 0, 0), 2)
    
    cv2.imshow('window',self.frame2)
    
    if cv2.waitKey(20) == ord('q'):
      break

cv2.destroyAllWindows()
class movie:
    def __init__(self):
        self.recording_time = 5
        self.fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for the output video (XVID is a common choice)
        self.out = cv2.VideoWriter('output1.mp4', self.fourcc, 30.0, (640, 480))
        self.i = 0
    def capture(self):
        
        time.sleep(5)
        #print(v.video_frame())
        #print(self.previous_frame)
        self.end_time = time.time() + self.recording_time
        while time.time()< self.end_time:
            self.one_frame_time = time.time() + 1/30
            self.current_frame = v.video_frame()
            while self.one_frame_time > time.time():pass # trying capturing only one frame per 1/30 second
            while "None" in str(type(self.current_frame)):
                print('no frame')
            self.out.write(self.current_frame)
            self.i += 1
                
        self.out.release() 
        print(self.i)
class video:
    def __init__(self):
        self.data = b""
        self.previous_number = None
        self.frame_number = 1
# Q: unsigned long long integer(8 bytes)
        self.payload_size = struct.calcsize("Q")
    def video_frame(self):
        if self.frame_number != self.previous_number:
            self.previous_number = self.frame_number
            return(self.frame) 
        else:
            return None
    def video_streamer(self, server):
        self.client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.client_socket.connect(server) 
        while True:
            while len(self.data) < self.payload_size:
                self.packet = self.client_socket.recv(4*1024)
                if not self.packet: break
                self.data+=self.packet
            #print('1')
            self.packed_msg_size = self.data[:self.payload_size]
            self.data = self.data[self.payload_size:]
            self.msg_size = struct.unpack("Q",self.packed_msg_size)[0]
            while len(self.data) < self.msg_size:
                self.data += self.client_socket.recv(4*1024)
            self.frame_data = self.data[:self.msg_size]
            self.data  = self.data[self.msg_size:]
            self.frame = pickle.loads(self.frame_data)
            self.frame_number += 1
            cv2.imshow("Receiving...",self.frame)
            self.key = cv2.waitKey(10) 
            if self.key  == 13:
                break
        self.client_socket.close()
class audio:
    def __init__(self):
        
        self.mode =  'get'
        self.name = 'CLIENT RECEIVING AUDIO'
        self.audio,self.context = ps.audioCapture(mode=self.mode)
        ps.showPlot(self.context,self.name)
        self.payload_size = struct.calcsize("Q")
    def audio_streamer(self, server):
        # create socket
        self.client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.host_ip , self.port= server
        self.port += 1

        self.socket_address = (self.host_ip,self.port)
        self.client_socket.connect(self.socket_address) 
        print("CLIENT CONNECTED TO",self.socket_address)
        self.data = b""
        
        print(self.payload_size)
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
            
     

        self.client_socket.close()

a = audio()
v = video()
m = movie()
audio_thread = threading.Thread(target=a.audio_streamer, args=(server,))
video_thread = threading.Thread(target=v.video_streamer, args=(server,))
movie_thread = threading.Thread(target=m.capture)
audio_thread.start()
video_thread.start()
movie_thread.start()
movie_thread.join()
audio_thread.join()
video_thread.join()
