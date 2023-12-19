import socket, cv2, pickle,struct,time, threading
import pyshine as ps
host_ip = '192.168.0.137'
port = 4997
backlog = 5
server = host_ip, port, backlog
class audio:
    def __init__(self):
        self.mode =  'send'
        self.name = 'SERVER TRANSMITTING AUDIO'
        self.audio,context= ps.audioCapture(mode=self.mode)
        self.server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

        #ps.showPlot(context,name)
    def audio_streamer(self, server):
        self.host_ip, self.port, self.backlog = server  
        
        self.port += 1
        self.socket_address = (self.host_ip,self.port)
        print('STARTING AUDIO_SERVER AT',self.socket_address,'...')
        self.server_socket.bind(self.socket_address)
        self.server_socket.listen(self.backlog)

        while True:
            self.client_socket,self.addr = self.server_socket.accept()
            print('GOT AUDIO_CONNECTION FROM:',self.addr)
            if self.client_socket:

                while(True):
                    self.frame = self.audio.get()
                    
                    self.a = pickle.dumps(self.frame)
                    self.message = struct.pack("Q",len(self.a))+self.a
                    #print(str(len(self.message)))
                    self.client_socket.sendall(self.message)
                    
            else:
                break

        self.client_socket.close()


class video:
    def __init__(self):
        self.vid = cv2.VideoCapture(0)
        self.server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    def video_streamer(self, server):
        self.host_ip, self.port, self.backlog = server  
        self.socket_address = (self.host_ip,self.port)
        
        # bind the socket to the host. 
        #The values passed to bind() depend on the address family of the socket
        self.server_socket.bind(self.socket_address)
        print('STARTING VIDEO_SERVER AT',self.socket_address,'...')
        #listen() enables a server to accept() connections
        #listen() has a backlog parameter. 
        #It specifies the number of unaccepted connections that the system will allow before refusing new connections.
        self.server_socket.listen(0)
        


        while True:
            self.client_socket,self.addr = self.server_socket.accept()
            print('GOT VIDEO_CONNECTION FROM:',self.addr)
            if self.client_socket:
                
                while(self.vid.isOpened()):
                    self.img,self.frame = self.vid.read()
                    self.a = pickle.dumps(self.frame)
                    self.message = struct.pack("Q",len(self.a))+self.a
                    self.client_socket.sendall(self.message)
                    #print(str(len(self.message)))
                    #cv2.imshow('Sending...',self.frame)
                    #self.key = cv2.waitKey(10) 
                    #if self.key ==13:
            else:
                self.client_socket.close()
a = audio()
v = video()
audio_thread = threading.Thread(target=a.audio_streamer, args=(server,))
video_thread = threading.Thread(target=v.video_streamer, args=(server,))
audio_thread.start()
video_thread.start()
audio_thread.join()
video_thread.join()
n"zQ@+0j