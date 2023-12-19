#works with host_server8.py
import socket
import cv2
import numpy as np
import pyaudio
import threading
'''
class Client:
    def __init__(self):
        self.host = '192.168.0.137'  # Server IP address
        self.port = 9200  # Server port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.video_capture = cv2.VideoCapture(0)
        self.audio = pyaudio.PyAudio()
        self.audio_stream = self.audio.open(format=pyaudio.paInt16, channels=1, rate=44100, output=True, frames_per_buffer=1024)
    
    def start(self):
        self.client_socket.connect((self.host, self.port))
        print("Connected to {}:{}".format(self.host, self.port))

        while True:
            data = self.client_socket.recv(65535)
            if not data:
                break
            parts = data.split(b'|||')
            print("Number of parts:", len(parts))
            # Split video and audio frames
            if len(parts) == 2:
                img_data, audio_data = parts
                print("Received img_data size:", len(img_data))
                print("Received audio_data size:", len(audio_data))

                img_encoded = np.frombuffer(img_data, dtype=np.uint8)
                img_decoded = cv2.imdecode(img_encoded, cv2.IMREAD_COLOR)
                print("Decoded image shape:", img_encoded.shape)

                # Play audio
                self.audio_stream.write(audio_data)

                # Display video frame
                #cv2.imshow('Received Video', img_decoded)
                #if cv2.waitKey(1) & 0xFF == ord('q'):
                    #break
        
        # Clean up
        self.client_socket.close()
        self.video_capture.release()
        cv2.destroyAllWindows()

# Create an instance of the Client class
client = Client()
client.start()
'''

#importing libraries
import socket
import cv2
import pickle
import struct

# Client socket
# create an INET, STREAMing socket : 
client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host_ip = '192.168.0.137'# Standard loopback interface address (localhost)
port = 10050 # Port to listen on (non-privileged ports are > 1023)
# now connect to the web server on the specified port number
client_socket.connect((host_ip,port)) 
#'b' or 'B'produces an instance of the bytes type instead of the str type
#used in handling binary data from network connections
data = b""
# Q: unsigned long long integer(8 bytes)
payload_size = struct.calcsize("Q")
while True:
    while len(data) < payload_size:
        packet = client_socket.recv(4*1024)
        if not packet: break
        data+=packet
    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack("Q",packed_msg_size)[0]
    while len(data) < msg_size:
        data += client_socket.recv(4*1024)
    frame_data = data[:msg_size]
    data  = data[msg_size:]
    frame = pickle.loads(frame_data)
    cv2.imshow("Receiving...",frame)
    key = cv2.waitKey(10) 
    if key  == 13:
        break
client_socket.close()

