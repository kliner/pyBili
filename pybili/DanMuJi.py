#!/usr/bin/python
#coding=utf-8
import bili
import bili_sender
import bili_config
import thread
import struct
import time
import json
import threading
import sys
import subprocess

DEBUG = 0

class DanmakuHandler(bili.DanmakuHandler):
    tts_s = None

    def __init__(self, roomid, cookies, config):
        self.sender = bili_sender.Sender(cookies)
        self.cnt = 9
        self.notificationTimers = {}
        self.startGiftResponse = config.get(roomid, "GiftResponse", False)
        self.showTime = config.get(roomid, "ShowTime", False)
        self.showNotification = config.get(roomid, "MacNotification", False)
        self.showSysGift = config.get(roomid, "SmallTVHint", False) 
        self.tts = config.get(roomid, "MacTTS", False)
        self.color = config.get(roomid, "DanmakuColor", "white")
        self.awardSmallTV = config.get(roomid, "AwardSmallTV", False)
        self.awardNeedYou = config.get(roomid, "AwardNeedYou", False)
    
        print '----------------------------'
        print '| bili danmaku helper v0.1 |' 
        print '----------------------------'
        print 'showTime...', self.showTime 
        print 'giftResponse...', self.startGiftResponse 
        print 'showSystemGift...', self.showSysGift
        print 'macNotification...', self.showNotification
        print 'macTTS...', self.tts
        print 'danmakuColor...', self.color
        print 'awardSmallTV...', self.awardSmallTV
        print 'awardNeedYou...', self.awardNeedYou
        print '----------------------------'
        self.date_format = '%H:%M:%S'
        self.gifts = []
        self.LOCK = threading.Lock()
        self.giftResponseThreadAlive = False
        self.sayLOCK = threading.Lock()
        self.saySentences = []
        if self.startGiftResponse: self.startGiftResponseThread()
        if self.tts: self.startTTSThread()

    def startTTSThread(self):
        thread.start_new_thread(self.sayThread, ())

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
                if self.tts:
                    self.toSay(content)

            elif raw['cmd'] == 'SEND_GIFT':
                data = raw['data']
                uname, num, giftName = data['uname'].encode('utf-8'), data['num'], data['giftName'].encode('utf-8')
                self.LOCK.acquire()
                self.gifts += [(uname, num, giftName)]
                self.LOCK.release()
            elif raw['cmd'] == 'WELCOME': pass 
            elif raw['cmd'] == 'WELCOME_GUARD': pass 
            elif raw['cmd'] in ['SYS_GIFT']: pass
            elif raw['cmd'] in ['SYS_MSG']: 
                if u'应援棒' in raw['msg']:
                    roomid = raw['url'].split('/')[-1]
                    tm = time.strftime(self.date_format, time.localtime(time.time() + 18000))
                    #self.sender.sendDanmaku(self.roomid, '%s房间领应援棒啦，当前时间%s' % (roomid, tm), self.color)
                    #if self.showSysGift: self.sender.sendDanmaku(self.roomid, '%s房间领应援棒啦，当前时间%s' % (roomid, tm), self.color)
                    if self.awardNeedYou: self.sender.joinNeedYou(roomid)

                if 'roomid' in raw:
                    roomid = str(raw['roomid'])
                    tm = time.strftime(self.date_format, time.localtime(time.time() + 180 + 18000))
                    #print '%s房间小电视啦，有效期至%s(｡･ω･｡)ﾉ' % (roomid, tm)
                    if self.showSysGift: self.sender.sendDanmaku(self.roomid, '%s房间小电视啦，有效期至%s' % (roomid, tm), self.color)
                    tvid = raw['tv_id']
                    if self.awardSmallTV: self.sender.joinSmallTV(roomid, tvid)

            else: 
                if DEBUG: print raw
        else:
            if DEBUG: print 'unknown action,' + repr(danmaku) 

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
                self.sender.sendDanmaku(self.roomid, '谢谢%s送的%s个%s' % (uname, str(num), giftName), self.color)
                while self.gifts: self.gifts.pop()
            self.LOCK.release()
            time.sleep(2)

    def startGiftResponseThread(self):
        if not self.giftResponseThreadAlive:
            thread.start_new_thread(self.giftResponseThread, ())
            self.giftResponseThreadAlive = True
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

    def say(self, s):
        cmd = 'say \'%s\'' % (s)
        if DEBUG: print cmd
        if not self.tts_s:
            self.tts_s = subprocess.Popen(cmd, shell=True)
            self.tts_s.wait()
        else:
            self.tts_s = subprocess.Popen(cmd, shell=True)
            self.tts_s.wait()

    def toSay(self, s):
        self.sayLOCK.acquire()
        self.saySentences = [s] + self.saySentences
        self.sayLOCK.release()
    
    def sayThread(self):
        while 1:
            while self.saySentences:
                self.sayLOCK.acquire()
                s = self.saySentences.pop()
                self.sayLOCK.release()
                self.say(s)
            time.sleep(1)


def main():
    argv = sys.argv
    roomid = 90012
    if len(argv) == 2:
        roomid = int(argv[1])
    config = bili_config.Config()
    cookies = config.cookies

    handler = DanmakuHandler(roomid, cookies, config = config)

    color = config.get(roomid, "DanmakuColor", "white")

    py = bili.BiliHelper(roomid, handler)
    while 1:
        cmd = raw_input()
        handler.sender.sendDanmaku(roomid, cmd, color)

if __name__ == '__main__':
    main()
