#!/usr/bin/python
#coding=utf-8
import socket
import struct
import random
import json
import thread
import time
import sys
import threading
import bili_sender

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
    def handleDanmaku(self, danmaku):
        pass

class DefaultDanmakuHandler(DanmakuHandler):
    def __init__(self, startGiftResponse = False):
        self.cnt = 9
        self.date_format = '%H:%M:%S'
        self.gifts = []
        self.LOCK = threading.Lock()
        self.giftResponseThreadAlive = False
        if startGiftResponse: self.startGiftResponseThread()

    def handleDanmaku(self, danmaku):
        body = danmaku.rawData
        if danmaku.action == 3: # online clients
            onlineNum = struct.unpack('>i', body)[0]
            self.cnt += 1
            if self.cnt >= 10: 
                print '在线灵魂数:' + str(onlineNum)
                self.cnt = 0
        elif danmaku.action == 5: # danmaku packet
            raw = json.loads(body)
            if DEBUG: print raw

            tm = time.strftime(self.date_format, danmaku.time)
            if 'info' in raw:
                info = raw['info']
                print '[%s] \033[91m%s\033[0m : \033[94m%s\033[0m' % (tm, info[2][1].encode('utf-8'), info[1].encode('utf-8'))
            elif raw['cmd'] == 'SEND_GIFT':
                data = raw['data']
                uname, num, giftName = data['uname'].encode('utf-8'), data['num'], data['giftName'].encode('utf-8')
                self.LOCK.acquire()
                self.gifts += [(uname, num, giftName)]
                self.LOCK.release()
            elif raw['cmd'] == 'WELCOME': pass 
            elif raw['cmd'] == 'WELCOME_GUARD': pass 
            elif raw['cmd'] in ['SYS_GIFT', 'SYS_MSG']: pass
        else:
            if DEBUG: print 'unknown action,' + repr(packet) 

    def giftResponseThread(self):
        while 1:
            self.LOCK.acquire()
            if self.gifts:
                uname, num, giftName = self.gifts[0]
                for t_uname, t_num, t_giftName in self.gifts[1:]:
                    num = '好多'
                    if t_uname != uname: uname = '大家'
                    if t_giftName != giftName: giftName = '礼物'
                #print '谢谢%s送的%s个%s' % (uname, str(num), giftName)
                bili_sender.sendDanmaku(self.roomid, '谢谢%s送的%s个%s' % (uname, str(num), giftName))
                while self.gifts: self.gifts.pop()
            self.LOCK.release()
            time.sleep(2)

    def startGiftResponseThread(self):
        if not self.giftResponseThreadAlive:
            thread.start_new_thread(self.giftResponseThread, ())
            self.giftResponseThreadAlive = True
            bili_sender.init()
            if DEBUG: print 'giftResponseThreadStarted!'

class BiliHelper(object):

    def __init__(self, roomid = 90012, packetHandler = DefaultDanmakuHandler()):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((HOST, PORT))
        self.cnt = 9
        self.roomid = roomid
        self.heartBeatThreadAlive, self.packetReceiveThreadAlive, self.giftResponseThreadAlive = 0, 0, 0
        self.danmakuHandler = packetHandler
        self.joinChannel(roomid)
        self.startHeartBeatThread()
        self.startPacketReceiveThread()

    def startHeartBeatThread(self):
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

    def heartBeatThread(self):
        while 1:
            self.sendPacket(2, '')
            time.sleep(30)

    def parsePacket(self, packet):
        try:
            while packet:
                #print repr(packet)
                header = struct.unpack('>IHHII', packet[:16])
                packetLength = int(header[0])
                body = packet[16:packetLength]
                action = header[3]
                danmaku = Danmaku(action, body, time.localtime(time.time()))

                self.danmakuHandler.handleDanmaku(danmaku)

                if packetLength > len(packet):
                    print 'packetLengthError!', packetLength, len(packet), repr(packet[:packetLength]), repr(packet[packetLength:])
                    break
                packet = packet[packetLength:]

        except Exception, e:
            print 'decode error!', e

    def recvThread(self):
        while 1:
            packet = self.s.recv(BUFFER_SIZE)
            if packet: self.parsePacket(packet)

if __name__ == '__main__':
    #py = BiliHelper(26057)
    py = BiliHelper(90012, DefaultDanmakuHandler(startGiftResponse = True))
    while 1:
        cmd = raw_input()
