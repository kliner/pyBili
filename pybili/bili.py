#!/usr/bin/python
#coding=utf-8
import socket
import struct
import random
import json
import thread
import time
import sys

reload(sys)  
sys.setdefaultencoding('utf-8')

HOST = 'livecmt-2.bilibili.com'
PORT = 788
BUFFER_SIZE = 128 * 1024

DEBUG = 0

class Danmaku(object):
    def __init__(self, action, rawData, time):
        self.action = action
        self.rawData = rawData
        self.time = time

class DanmakuHandler(object):

    def setRoomId(self, roomid):
        self.roomid = roomid

    def handleDanmaku(self, danmaku):
        pass

class BiliHelper(object):

    def __init__(self, roomid, packetHandler):
        self.lastPacket = 0
        self.cnt = 9
        self.roomid = roomid
        self.heartBeatThreadAlive, self.packetReceiveThreadAlive, self.giftResponseThreadAlive = 0, 0, 0
        self.danmakuHandler = packetHandler
        packetHandler.setRoomId(roomid)
        self.startHeartBeatThread()
        self.startPacketReceiveThread()
        time.sleep(5) # sleep 5s for thread start
        thread.start_new_thread(self.localCheckThread, ())

    def startHeartBeatThread(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((HOST, PORT))
        self.joinChannel(self.roomid)
        if not self.heartBeatThreadAlive:
            thread.start_new_thread(self.heartBeatThread, ())
            self.heartBeatThreadAlive = True
            if DEBUG: print 'heartBeatThreadStarted!'

    def startPacketReceiveThread(self):
        if not self.packetReceiveThreadAlive:
            thread.start_new_thread(self.recvThread, ())
            self.packetReceiveThreadAlive = True
            if DEBUG: print 'packetReceiveThreadStarted!'

    def sendPacket(self, action, body):
        playload = body.encode('utf-8')
        packetLength = len(playload) + 16
        head = struct.pack('>IHHII', packetLength, 16, 1, action, 1)
        self.s.send(head + playload)

    def joinChannel(self, channelId, uid = int(1e14 + 2e14 * random.random())):
        body = json.dumps({'roomid':channelId, 'uid': uid}, separators=(',',':'))
        self.sendPacket(7, body)
        return 1

    def localCheckThread(self):
        while 1:
            try:
                if not self.heartBeatThreadAlive:
                    if DEBUG: print 'detect heartBeatThread down, restarting...'
                    self.startHeartBeatThread()
                if not self.packetReceiveThreadAlive:
                    if DEBUG: print 'detect packetReceiveThread down, restarting...'
                    self.startPacketReceiveThread()
            except Exception, e:
                pass
            time.sleep(10)

    def heartBeatThread(self):
        try:
            while 1:
                self.sendPacket(2, '')
                time.sleep(30)
        except Exception, e:
            if DEBUG: print 'heartBeatThread down!'
            self.heartBeatThreadAlive = False

    def handleUnfinishedPacket(self, packet):
        if self.lastPacket: 
            if DEBUG: 
                print '--------------------------'
                print 'last unfinished packet, ', repr(packet)
                print '--------------------------'
            if len(packet) < 16: return packet
            header = struct.unpack('>IHHII', packet[:16])
            if header[0] > 0xffff:
                packet = self.lastPacket + packet
                if DEBUG: print 'contact last packet, ', repr(packet)
            self.lastPacket = 0
        return packet

    def parsePacket(self, packet):
        packet = self.handleUnfinishedPacket(packet)
        try:
            while packet:
                #print repr(packet)
                if len(packet) < 16: return
                header = struct.unpack('>IHHII', packet[:16])
                packetLength = int(header[0])
                body = packet[16:packetLength]
                action = header[3]
                danmaku = Danmaku(action, body, time.localtime(time.time()))

                if packetLength > len(packet):
                    if DEBUG:
                        print 'packetLengthError!', header, len(packet), repr(packet[:packetLength]), repr(packet[packetLength:])
                    self.lastPacket = packet
                    break
                self.danmakuHandler.handleDanmaku(danmaku)
                packet = packet[packetLength:]
        except SystemExit:  
            return  
        except Exception, e:
            print 'decode error!', e

    def recvThread(self):
        try:
            while 1:
                packet = self.s.recv(BUFFER_SIZE)
                if packet: self.parsePacket(packet)
        except Exception, e:
            if DEBUG: print 'recvThread down!', e
            self.packetReceiveThreadAlive = False

if __name__ == '__main__':
    while 1:
        cmd = raw_input()
