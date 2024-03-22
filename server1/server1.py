# this is the main server that normally clients
# connect to, by itself it main an internally for
# conversing with an internal server (TCP Based server for analysing fraud)

# load socket module and open cv module
import socket
import cv2, pickle, time,sys
import _thread as thread
import numpy as np
import os,sqlite3,datetime,zlib,pickle
from threading import Timer



class Server1:
    """ list of server command """
    CAMERA_QUERY = b"WHICH CAMERA?"
    AUTH_CMD = b"WHO ARE YOU?"
    GET_CLIENT_CONFIG = b"GET CNF"
    GET_CAMERA_1 = b"GET CAMERA 1"
    GET_CAMERA_2 = b"GET CAMERA 2"
    GET_CAMERA_3 = b"GET ALL CAMERA"
    SERVER_PAUSED = b"PAUSED MOMENTARILY"
    SUCCESS = b"OK"
    SERVER_SHUTDOWN = b"SHUTDOWN SERVER ONE"
    END_OF_FRAME = b"END_OF_FRAME"
    SERVER_STOP = b"STOP"
    AUTH_NEEDED = b"ERROR_AUTH_NEEDED"
    AUTH_SUCCESS = b"AUTH_SUCCESS"
    SERVER_FRAME_TYPE_COLOR_CAM_1 = b"FRAME_TYPE_COLOR_CAM_1"
    SERVER_FRAME_TYPE_GRAY_CAM_1  = b"FRAME_TYPE_GRAY_CAM_1"
    SERVER_FRAME_TYPE_COLOR_CAM_2 = b"FRAME_TYPE_COLOR_CAM_2"
    SERVER_FRAME_TYPE_GRAY_CAM_2  = b"FRAME_TYPE_GRAY_CAM_2"
    SERVER_FRAME_TYPE_GRAY_CAM_3 = b"FRAME_TYPE_GRAY_CAM_3"
    SERVER_FRAME_TYPE_COLOR_CAM_3 = b"FRAME_TYPE_COLOR_CAM_3"
    SERVER_QUERY_CMD = b"QUERY_CMD"
    SERVER_CONTINUE = b"CONTINUE"
    START_OF_FRAME = b"START_OF_FRAME"

    def __init__(self,host,port,camera1,camera2=None,db=None):
        # main socket that normally clients connect to
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.sock.bind((host,port))
        # socket for streaming frame
        self.streamingServer = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        #self.streamingServer.bind((host,7000))
        # internal server sock for connecting to the second server TCP
        self.serverSock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        # list of camera that normally the server serve
        self.camera1 = camera1
        self.camera2 = camera2
        # thread lock
        self.lock = thread.allocate_lock()
        # maximum buffer
        self.MAXBUFF = 1024
        # init cv2 module
        # video frame size according to the client screen area
        self.HEIGHT = 0
        self.WIDTH = 0
        self.fps = 0
        # init database 
        self.init()
        # run test of a frame per second
        self.estimateFPS()

        # max duration before saving a video
        self.DURATION = 60*60
        self.frame0 = None
        self.frame1 = None
        self.success0 = self.success1 = None
        # saving timer
        self.timer = Timer(self.DURATION,self.updateVideoWriter)
        self.timer.start()

    def updateVideoWriter(self):
        # compress previous videos
        prevVideo1,prevVideo2 = self.filename1,self.filename2
        self._compress(prevVideo1,prevVideo2)
        # delete the two uncompressed video
        self.timer = Timer(self.DURATION,self.updateVideoWriter)
        self.timer.start()

    
    def init(self):
        # files
        self.filename1 = "{!r}-cam1".format(datetime.datetime.utcnow())
        self.filename2 = "{!r}-cam2".format(datetime.datetime.utcnow())

        # initialized the cameras
        self.cam0 = cv2.VideoCapture(self.camera1)
        if self.camera2:
            self.cam1 = cv2.VideoCapture(self.camera2)
        # target encoding
        self.encoding = cv2.VideoWriter_fourcc("X","2","6","4")
        # video writer 
        # self.videoWriter = cv2.VideoWriter(self.filename1,self.encoding)
        # self.videoWriter1 = cv2.VideoWriter(self.filename2,self.encoding)

    def estimateFPS(self):
        """ estimate frame per second """
        startTime = time.time()
        success,self.frame = self.cam0.read()
        while time.time() - startTime < 1 and  success:
            success,self.frame = self.cam0.read()
            self.fps += 1
        # compensate for the slow moving
        self.fps += 2

    

    def handleClient(self,addr,reply):
        """ target client screen size """
        # receive request which camera to serve
        CAMERA_CMDS = {Server1.GET_CAMERA_1:0,Server1.GET_CAMERA_3:0,Server1.GET_CAMERA_2:0,
                        Server1.SERVER_SHUTDOWN:0,Server1.SERVER_STOP:0,
                }
        # client reply for cmd
        reply = reply
        
        while True:
            self.success0, self.frame0 = self.cam0.read()
            cv2.rectangle(self.frame0,(10,10),(200,200),(38,124,254),2)
            print(reply)
            if reply == Server1.GET_CAMERA_1:
                if self.success0:
                    self.sendFrame(addr,self.frame0)
                    print("serving client another frame")
    

            elif reply == Server1.GET_CAMERA_2:            
                if self.success1:
                    self.sendFrame(addr,self.frame1)
                    
            
            elif reply == Server1.GET_CAMERA_3:
                if self.success0:
                    self.sendFrame(addr,self.frame0)
                

            elif reply == Server1.SERVER_FRAME_TYPE_GRAY_CAM_1:
                if self.success0:
                    frame = cv2.cvtColor(self.frame0,cv2.COLOR_BGR2GRAY)
                    print("server frame",frame)
                    self.sendFrame(addr,frame)

            elif reply == Server1.SERVER_FRAME_TYPE_GRAY_CAM_2:
                if self.success0:
                    frame = cv2.cvtColor(self.frame1,cv2.COLOR_BGR2GRAY)
                    self.sendFrame(addr,frame)

            elif reply == Server1.SERVER_FRAME_TYPE_GRAY_CAM_3:
                if self.success0:
                    frame = cv2.cvtColor(self.frame0,cv2.COLOR_BGR2GRAY)
                    self.sendFrame(addr,frame)

            elif reply == Server1.SERVER_STOP:
                self.sock.sendto(Server1.SUCCESS,addr)

            elif reply == Server1.SERVER_SHUTDOWN:
                break

            reply,addr = self.sock.recvfrom(1024*3)
                 

    def sendFrame(self,addr,frame):
        # buffer length
        maxbuffer = (1024 * 3) + 1000
        frame = pickle.dumps(frame)
        # compressed frame
        compressedFrame = zlib.compress(frame,9) 

        self.sock.sendto(Server1.START_OF_FRAME,addr)

        while compressedFrame: 
            compressedFrame,rest = compressedFrame[maxbuffer:], compressedFrame[:maxbuffer]
            self.sock.sendto(rest,addr)
            time.sleep(0.0001)
        self.sock.sendto(Server1.END_OF_FRAME,addr)


    def saveFrames(self,frame):
        pass

    def run(self):
        self.sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        print("server listening for connection","video frames per second",self.fps)
        maxbuffer = 1024 * 3

        while True:
            print("server listening at",self.sock.getsockname())
            try:
                data,addr = self.sock.recvfrom(maxbuffer)
                print("receive connection from =>",addr)
        
                # handle client in a new thread
                thread.start_new_thread(self.handleClient(addr,data))
            
            except KeyboardInterrupt:
                self.cam0.release()
                sys.exit(0)

if __name__ == "__main__":
    server = Server1("",8000,0,db="server-users.sql")
    server.run()