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
            self.current_frame = v.video_frame()
            
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
