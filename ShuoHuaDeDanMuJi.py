#!/usr/bin/python
#coding=utf-8
import bili
import bili_sender
import thread
import struct
import time
import json
import threading
import sys
import subprocess

DEBUG = 0

class DanmakuHandler(bili.DanmakuHandler):
    def __init__(self, startGiftResponse = False):
        self.cnt = 9
        self.date_format = '%H:%M:%S'
        self.gifts = []
        self.LOCK = threading.Lock()
        self.tts = 0
        self.giftResponseThreadAlive = False
        if startGiftResponse: self.startGiftResponseThread()

    def handleDanmaku(self, danmaku):
        body = danmaku.rawData
        if danmaku.action == 3: # online clients
            onlineNum = struct.unpack('>i', body)[0]
            self.cnt += 1
            if self.cnt >= 10: 
                print '在线 \033[91m♥︎\033[0m :' + str(onlineNum)
                self.cnt = 0
        elif danmaku.action == 5: # danmaku packet
            raw = json.loads(body)
            if DEBUG: print raw

            tm = time.strftime(self.date_format, danmaku.time)
            if 'info' in raw:
                info = raw['info']
                print '[%s] \033[91m%s\033[0m : \033[94m%s\033[0m' % (tm, info[2][1].encode('utf-8'), info[1].encode('utf-8'))

                if info[2][1].encode('utf-8') == 'klikli': return
                #cmd = 'say %s说%s' % (info[2][1].encode('utf-8'), info[1].encode('utf-8'))
                cmd = 'say \'%s\'' % (info[1].encode('utf-8'))
                if DEBUG: print cmd
                if not self.tts:
                    self.tts = subprocess.Popen(cmd, shell=True)
                else:
                    self.tts.kill()
                    self.tts = subprocess.Popen(cmd, shell=True)
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
                reply = '谢谢%s送的%s个%s' % (uname, str(num), giftName)
                bili_sender.sendDanmaku(self.roomid, reply)
                cmd = 'say \'%s\'' % reply
                if DEBUG: print cmd
                if not self.tts:
                    self.tts = subprocess.Popen(cmd, shell=True)
                else:
                    self.tts.kill()
                    self.tts = subprocess.Popen(cmd, shell=True)
                while self.gifts: self.gifts.pop()
            self.LOCK.release()
            time.sleep(5)

    def startGiftResponseThread(self):
        if not self.giftResponseThreadAlive:
            thread.start_new_thread(self.giftResponseThread, ())
            self.giftResponseThreadAlive = True
            bili_sender.init()
            if DEBUG: print 'giftResponseThreadStarted!'

if __name__ == '__main__':
    argv = sys.argv
    roomid = 90012
    if len(argv) == 2:
        roomid = int(argv[1])

    py = bili.BiliHelper(roomid, DanmakuHandler(startGiftResponse = True))
    while 1:
        cmd = raw_input()
        bili_sender.sendDanmaku(roomid, cmd)
