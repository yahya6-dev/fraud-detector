import unittest
import os,socket,time
import sys,pickle
from multiprocessing import Process 

# include server directory to its path
sys.path.append("../server1")

from server1 import Server1
import numpy as np 
import cv2,zlib,_thread as thread,time

class TestServerAuthentication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.serverAddr = ("",9000)
        cls.MAXBUFF = 1024
        pid = os.fork()
        if pid == 0:
            server = Server1("",9000,0,db="server-users.sql")
            server.run()
        else:
            cls.pid = pid
            time.sleep(4)
            print("to start sending message now")

    @classmethod
    def tearDownClass(cls):
        os.kill(cls.pid,9)

    def test_client_connection(self):
        time.sleep(2)
        client = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        client.connect(self.serverAddr)

        client.sendto(Server1.GET_CAMERA_1,self.serverAddr)
        
        reply,addr = client.recvfrom(self.MAXBUFF)
        # send server camera query
        frame = b""
        while True:
            client.sendto(Server1.GET_CAMERA_1,self.serverAddr)
            data,addr = client.recvfrom(1024*6)
            if data == Server1.START_OF_FRAME:
                frame = b""

            elif data == Server1.END_OF_FRAME:
                try:
                    frame = zlib.decompress(frame)
                    frame = pickle.loads(frame)
                    cv2.imwrite("out.jpg",frame)
                    break
                    print(frame)
                    frame = b""
                except:
                    frame = b""
            else:
                frame += data
            
             

        