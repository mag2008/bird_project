'''import socket,cv2, pickle,struct

# create socket
client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host_ip = '192.168.0.136' # paste your server ip address here
port = 9997
client_socket.connect((host_ip,port)) # a tuple
data = b""
payload_size = struct.calcsize("Q")
while True:
	while len(data) < payload_size:
		packet = client_socket.recv(4*1024) # 4K
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
	cv2.imshow("RECEIVING VIDEO",frame)
	if cv2.waitKey(1) == '13':
		break
client_socket.close()'''
import cv2
import pyaudio
import socket
import threading
import numpy as np
import io

# Video display setup
cv2.namedWindow('Video', cv2.WINDOW_NORMAL)

# Audio playback setup
audio = pyaudio.PyAudio()
audio_stream = audio.open(format=pyaudio.paInt16, channels=1, rate=44100, output=True, frames_per_buffer=1024)

# Socket setup
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('192.168.0.137', 8000))  # Replace with your Raspberry Pi's IP address

# Synchronization variables (timestamps or sequence numbers)
video_timestamp = -1
audio_timestamp = -1
global data 
data = b''
def receive_video():
    while True:
        if data[:5] == b'VIDEO':
            if first:
                first = False 
                print('could disect')
                print(information)
            #timestamp = int(parts[1])
            #frame_data = data[6:]
            #print(str(len(frame_data)))
            #if timestamp > video_timestamp:
                #video_timestamp = timestamp
            frames = np.frombuffer(data[6:], dtype=np.uint8)
            if not frames:
                print('empty')
            frame = cv2.imdecode(frames, cv2.IMREAD_COLOR)
            cv2.imshow('Video', frame)
def receive_audio():
    while True:
        if data[:5] == b'AUDIO':
            #timestamp = int(parts[1])
            #audio_data = data[6:]
            #if timestamp > audio_timestamp:
                #audio_timestamp = timestamp
            audio_stream.write(data[6:])
            print('1')
# Create threads for video and audio reception
video_thread = threading.Thread(target=receive_video)
audio_thread = threading.Thread(target=receive_audio)

# Start the threads
video_thread.start()
audio_thread.start()   
first = True


while True:
 
    data = client_socket.recv(4096)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
'''
def receive_audio():
    global audio_timestamp
while True:
    try:
        audio_chunk = client_socket.recv(4096)
        parts = audio_chunk.split(b"|")
        if len(parts) == 2 and parts[0] == b'AUDIO':
            #timestamp = int(parts[1])
            audio_data = parts[1]
            #if timestamp > audio_timestamp:
                #audio_timestamp = timestamp
            audio_stream.write(audio_data)
    except Exception as e:
        print("Error receiving audio:", str(e))
        break

# Create threads for video and audio reception
#video_thread = threading.Thread(target=receive_video)
#audio_thread = threading.Thread(target=receive_audio)

# Start the threads
#video_thread.start()
#audio_thread.start()
'''
# Continue to process and synchronize data.
# Proper synchronization and error handling are crucial for real-time applications.


# Cleanup when done
cv2.destroyAllWindows()
audio_stream.stop_stream()
audio_stream.close()
audio.terminate()
client_socket.close()