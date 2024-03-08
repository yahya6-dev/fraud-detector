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
        cls.serverAddr = ("",8000)
        cls.MAXBUFF = 1024
        pid = os.fork()
        if pid == 0:
            server = Server1("",8000,0,db="server-users.sql")
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
        print(reply,"After sending screen configuration")
        self.assertTrue(reply == Server1.SUCCESS)
        client.close()