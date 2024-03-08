import unittest
import os,socket,time
import sys,pickle
from multiprocessing import Process 
# include server directory to its path
sys.path.append("../server1")
from server1 import Server1
import numpy as np 
import cv2,zlib

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
        client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        client.connect(self.serverAddr)

        # received data from our server response
        data = client.recv(self.MAXBUFF)
        print("client received on first connection =>", data.decode("ascii"))

        self.assertEqual(Server1.AUTH_CMD,data)
        # client credntials
        creds = pickle.dumps(["admin","admin"])
        bytesSent = client.send(creds)
        print("Client waiting for response => byte sent",bytesSent)
        # server response after login
        reply = client.recv(bytesSent)
        # send server status of beeing authenticated
        client.send(Server1.SUCCESS)
        print(reply)
        self.assertTrue(reply == Server1.AUTH_SUCCESS)
        print("server reply after login => %s" % reply.decode("ascii"))
        reply = client.recv(self.MAXBUFF)
        print("reply after authentication",reply.decode("ascii"))
        # screen size
        size = [1000,1000]
        client.send(pickle.dumps(size))
        reply = client.recv(self.MAXBUFF)
        # sending response after sending screen size
        client.send(Server1.SUCCESS)
        print(reply,"After sending screen configuration")
        self.assertTrue(reply == Server1.SUCCESS)

        # receive streaming server info
        reply = client.recv(self.MAXBUFF)
        fps,streamServerAddress = pickle.loads(reply)
        self.assertTrue(fps != None)
        print("streaming server fps and address",fps,streamServerAddress)
        client.send(Server1.SUCCESS)

        reply = client.recv(self.MAXBUFF)
        print("server reply for cmd")
        client.send(Server1.GET_CAMERA_1)
        reply = client.recv(self.MAXBUFF)

        # send a new request to shutdown
        client.send(Server1.SERVER_SHUTDOWN)
        clientStreamSock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        clientStreamSock.connect(streamServerAddress)
        print(clientStreamSock.getpeername(),"client connect to udp streaming server")
        clientStreamSock.close()
        client.close()


    def recvFrame(self,clientStreamSock):
        pass