# this is the main server that normally clients
# connect to, by itself it main an internally for
# conversing with an internal server (TCP Based server for analysing fraud)

# load socket module and open cv module
import socket
import cv2, pickle, time,sys
import _thread as thread
import numpy as np
import os,sqlite3,datetime,zlib
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
    SERVER_FRAME_TYPE = b"FRAME_TYPE"
    SERVER_QUERY_CMD = b"QUERY_CMD"

    def __init__(self,host,port,camera1,camera2=None,db=None):
        # main socket that normally clients connect to
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.sock.bind((host,port))
        # socket for streaming frame
        self.streamingServer = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.streamingServer.bind((host,7000))
        # internal server sock for connecting to the second server TCP
        self.serverSock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        # list of camera that normally the server serve
        self.camera1 = camera1
        self.camera2 = camera2
        # maximum buffer
        self.MAXBUFF = 1024
        # init cv2 module
        # video frame size according to the client screen area
        self.HEIGHT = 0
        self.WIDTH = 0
        self.fps = 0
        # init database 
        self.initDB(db)
        self.init()
        # run test of a frame per second
        self.estimateFPS()

        # max duration before saving a video
        self.DURATION = 60*60
        self.frame = None
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

    # initialized our database
    def initDB(self,db):
        print("db =>",db)
        TABLE_CRT_CMD = """
          create table server_users (
            id int primary key, username char(64),
            password char(64)
          )
        """
        if db:
            if db in os.listdir("."):
                # database already exists
                print("database already")
                self.db = sqlite3.connect(db)
                self.cursor = self.db.cursor()
            else:
                self.db = sqlite3.connect(db)
                self.cursor = self.db.cursor()
                self.cursor.execute(TABLE_CRT_CMD)
                # create a new user for accessing the server
                self.cursor.execute("insert into server_users(username,password) values('admin','admin')")
                self.db.commit()


    def verifyUser(self,username,password):
        """ query the database for verifying users exists """
        QUERY_STM = """select username,password from server_users where username = ?
         and password = ?"""
        self.cursor.execute(QUERY_STM,[username,password])
        result = self.cursor.fetchone()
        print(result,"from server database",username,password)
        if result:
            return True
        return False
        
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

    def internalCMDHandler(self,sock,cmds):
        SHUTDOWN = cmds[Server1.SERVER_SHUTDOWN]

        while True and not SHUTDOWN:
            sock.send(Server1.SERVER_QUERY_CMD)
            reply = sock.recv(self.MAXBUFF)
            print("User Request ",reply,"COMMAND")
            # decode reply
            if reply != b"":
                current_query = cmds[reply]
                for key in cmds:
                    cmds[key] = 0

                cmds[reply] = 1

            SHUTDOWN = cmds[Server1.SERVER_SHUTDOWN]

        sock.close()
    


    def handleClient(self,sock):
        """ target client screen size """
        def streamClient(address):
            # current user query
            current_cmd = 
        width,height = self.getClientConfiguration(sock)
        authorized_client = sock.getpeername()
        # receive request which camera to serve
        CAMERA_CMDS = {Server1.GET_CAMERA_1:0,Server1.GET_CAMERA_3:0,Server1.GET_CAMERA_2:0,
                        Server1.SERVER_SHUTDOWN:0,Server1.SERVER_STOP:0,
                        }
        print("client screen size",width,height)

        reply = sock.recv(self.MAXBUFF)
        print(sock.getpeername(),"Status after sending screen size")
        # information on the udp server for streaming the video
        streamServerInfo = [self.fps,("",7000)]
        # send server information
        sock.send(pickle.dumps(streamServerInfo))
        # server reply
        reply = sock.recv(self.MAXBUFF)
        print("reply after sending to a client streaming server info",reply)
        # starting new thread
        self.internalCMDHandler(sock,CAMERA_CMDS)
        sock.close()
        os._exit(0)

    def auth(self,sock):
        """ verify user """
        sock.sendall(Server1.AUTH_CMD)
        # client response
        response = sock.recv(self.MAXBUFF)
        print("client response",response)
        # verify user here
        username,password = pickle.loads(response)
        print("client creds",username,password)
        if self.verifyUser(username,password):
            print("user authenticated")
            sock.send(Server1.AUTH_SUCCESS)
            return True

        return False

    def unauthorized(self,address):
        pass
    
    def saveFrames(self,frame):
        pass

    def sendData(self,sock,data):
        MAXBUFF = 1024 * 6

        rest = None
        while data:
            data,rest = data[MAXBUFF:],data[:MAXBUFF]
            sock.send(rest)
        sock.send(Server1.END_OF_FRAME)

    def clientResponse(self,sock):
        timeout = 0.1
        data = b''
        while not data:
            sock.settimeout(timeout)
            data = sock.recv(self.MAXBUFF)
        return data

    def getClientConfiguration(self,sock):
        """ get client target screen size """
        status = sock.recv(self.MAXBUFF)
        print("client verified status =>",status)
        sock.send(Server1.GET_CLIENT_CONFIG)
        # get client  response
        data = self.clientResponse(sock)
        width,height = pickle.loads(data)
        # send ok response
        sock.send(Server1.SUCCESS)
        return width,height

    def run(self):
        self.sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        self.sock.listen(5)
        print("server listening for connection","video frames per second",self.fps)
        while True:
            try:
                sock,address = self.sock.accept()
                print(type(sock),address)
                if self.auth(sock):
                    if os.fork() == 0:
                        self.handleClient(sock,)
                else:
                    sock.send(Server1.AUTH_NEEDED)
                    sock.close()

            except KeyboardInterrupt:
                self.cam0.release()
                sys.exit(0)

if __name__ == "__main__":
    server = Server1("",8000,0,db="server-users.sql")
    server.run()