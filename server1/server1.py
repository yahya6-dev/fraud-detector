# this is the main server that normally clients
# connect to, by itself it main an internally for
# conversing with an internal server (TCP Based server for analysing fraud)

# load socket module and open cv module
import socket
import cv2, pickle, time,sys
import _thread as thread
import numpy as np
import os,sqlite3,datetime,gzip,pickle
from threading import Timer
from multiprocessing import Process


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
    SERVER_TARGET_REQUEST = b"SERVER_TARGET_REQUEST"
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
        # error response
        self.noUpperbody = cv2.imread("../Components/assets/no-upperbody.png")
        self.noFullbody = cv2.imread("../Components/assets/no-fullbody.png")
        self.noFace = cv2.imread("../Components/assets/no-face.png")
        # detectors
        self.faceDetector = cv2.CascadeClassifier("../Components/assets/models/haarcascade_frontalface_default.xml")
        self.upperBodyDetector = cv2.CascadeClassifier("../Components/assets/models/haarcascade_upperbody.xml")
        self.fullBodyDetector = cv2.CascadeClassifier("../Components/assets/models/haarcascade_fullbody.xml")
        # main socket that normally clients connect to
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.sock.bind((host,port))
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
        response = reply
        # reference frame for computing histogram
        referenceFrame = None
        TRACKING_FACE = "Face"
        TRACKING_FULLBODY = "Full Body"
        TRACKING_TOPBODY = "Top Body"
        while True:
            self.success0, self.frame0 = self.cam0.read()
            print(response)
            reply,rectSize,x,y,selectTarget,trackingType = pickle.loads(response)
            rectX,rectY = rectSize
            print(reply,rectSize,x,y,selectTarget,trackingType)
            # special flags
            flags = cv2.CASCADE_SCALE_IMAGE
            # special case for a target request 
            if reply == Server1.SERVER_TARGET_REQUEST:
                self.lock.acquire()
                # check tracking and do the appropriate thing  
                targetFrame = self.frame0[y:rectY+y,x:rectX+x]

                gray = cv2.cvtColor(targetFrame,cv2.COLOR_BGR2GRAY)
                if trackingType == TRACKING_FACE:
                    result = self.faceDetector.detectMultiScale(gray,minNeighbors=5,scaleFactor=1.1,minSize=(30,30),flags=flags)
                    if len(result) > 0:
                        self.sendFrame(addr,targetFrame)
                    else:
                        self.sendFrame(addr,self.noFace)

                elif trackingType == TRACKING_FULLBODY:
                    result = self.fullBodyDetector.detectMultiScale(gray,minNeighbors=5,scaleFactor=1.1,minSize=(30,30),flags=flags)
                    if len(result) > 0:
                        self.sendFrame(addr,targetFrame)
                    else:
                        self.sendFrame(addr,self.noFullbody)
                elif trackingType == TRACKING_TOPBODY:
                    result = self.upperBodyDetector.detectMultiScale(gray,minNeighbors=5,scaleFactor=1.1,minSize=(30,30),flags=flags)
                    if len(result) > 0:
                        self.sendFrame(addr,targetFrame)
                    else:
                        print("NO UPPER WORK")
                        self.sendFrame(addr,self.noUpperbody)
                self.lock.release()

                break

            if selectTarget:
                if type(referenceFrame) != np.ndarray:
                    referenceFrame = self.frame0.copy()
                    #continue
                hsv_roi = cv2.cvtColor(referenceFrame[y:rectY+y,x:rectX+x],cv2.COLOR_BGR2HSV)
                x1,y1,w1,h1 = x,y,rectX+x,rectY+y
                track_window = (x1,y1,w1,h1)
                mask = None
                hist_roi = cv2.calcHist([hsv_roi],[0],mask,[180],[0,180])
                cv2.normalize(hist_roi,hist_roi,0,255,cv2.NORM_MINMAX)
                # criteria for stopping 
                criteria = (cv2.TERM_CRITERIA_COUNT | cv2.TERM_CRITERIA_EPS,10,1)
                hsv = cv2.cvtColor(self.frame0,cv2.COLOR_BGR2HSV)
                # back propagation
                back_proj = cv2.calcBackProject([hsv],[0],hist_roi,[0,180],1)
                iters,rect = cv2.meanShift(back_proj,track_window,criteria)
                x,y,w,h = rect 
                cv2.rectangle(self.frame0,(x,y),(rectX+x,rectY+y),(237,30,12),2)
            
            else:
                cv2.rectangle(self.frame0,(x,y),(rectX+x,rectY+y),(38,124,254),1)
                referenceFrame = None

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
                print(reply,"to the server" )
                
            elif reply == Server1.SERVER_SHUTDOWN:
                break

            response,addr = self.sock.recvfrom(1024*3)
                 

    def sendFrame(self,addr,frame):
        # buffer length
        maxbuffer = 1024 * 6 
        frame = pickle.dumps(frame)
        # compressed frame
        compressedFrame = gzip.compress(frame) 

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
        maxbuffer = 1024 * 6
        # list of connected
        connected  = ()
        while True:
            print("server listening at",self.sock.getsockname())
            try:
                data,addr = self.sock.recvfrom(maxbuffer)
                print("receive connection from =>",addr)
                #if not connected:
                #connected = addr
                    # handle client in a new thread
                #thread.start_new_thread(self.handleClient,(addr,data))
                #else:
                Process(target=self.handleClient,args=(addr,data)).start()

            except KeyboardInterrupt:
                self.cam0.release()
                sys.exit(0)

if __name__ == "__main__":
    server = Server1("",8000,0,db="server-users.sql")
    server.run()