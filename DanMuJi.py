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
    def __init__(self, startGiftResponse = False, showTime = False, showNotification = False):
        self.cnt = 9
        self.notificationTimers = {}
        self.showNotification = showNotification
        self.date_format = '%H:%M:%S'
        self.gifts = []
        self.LOCK = threading.Lock()
        self.giftResponseThreadAlive = False
        self.showTime = showTime
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
                user, content = info[2][1].encode('utf-8'), info[1].encode('utf-8')
                if self.showTime:
                    print '[%s] \033[91m%s\033[0m : \033[94m%s\033[0m' % (tm, user, content)
                else:
                    print '\033[91m%s\033[0m : \033[94m%s\033[0m' % (user, content)
                if self.showNotification:
                    self.showMacNotification(user, content)
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

    def showMacNotification(self, title, content):

        cmd = "terminal-notifier -title '%s' -message '%s' -group '%s' > /dev/null" % (title, content, title)
        # cmd = 'osascript -e \'display notification "%s" with title "%s"\'' % (content, title)
        subprocess.Popen(cmd, shell=True)
        t = threading.Timer(10, self.closeMacNotification, (title, ))
        t.start()
        if title in self.notificationTimers: self.notificationTimers[title].cancel()
        self.notificationTimers[title] = t

    def closeMacNotification(self, group):
        cmd = "terminal-notifier -remove '%s' > /dev/null" % group
        subprocess.Popen(cmd, shell=True)



if __name__ == '__main__':
    argv = sys.argv
    roomid = 90012
    startGiftResponse, showTime, showNotification = False, False, False
    if len(argv) == 2:
        roomid = int(argv[1])
    if len(argv) == 3:
        roomid = int(argv[1])
        startGiftResponse, showTime, showNotification = int(argv[2][0]), int(argv[2][1]), int(argv[2][2]) 

    py = bili.BiliHelper(roomid, DanmakuHandler(startGiftResponse = startGiftResponse, showTime = showTime, showNotification = showNotification))
    while 1:
        cmd = raw_input()
        bili_sender.sendDanmaku(roomid, cmd)
