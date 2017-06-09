#!/usr/bin/python
#coding=utf-8
import time
import json
import thread
import threading
import subprocess
import re

from bili import DanmakuHandler
from bili import SimpleDanmakuHandler
from pymongo import MongoClient

DEBUG = 0

class MongoHandler(DanmakuHandler):

    def __init__(self):
        try:
            print 'start db logger...'
            self.client = MongoClient()
            self.db = self.client.danmaku
        except:
            print 'mongodb service down!\nto install:[brew install mongodb]\nto start:[brew services start mongodb]'

    def handleDanmaku(self, danmaku):
        try:
            self.insert(danmaku)
        except:
            pass

    def insert(self, danmaku):
        danmaku.roomid = self.roomid
        self.db.raw.insert_one({
            'roomid':danmaku.roomid,
            'action':danmaku.action,
            'raw':danmaku.rawData,
            'time':time.strftime('%y%m%d-%H%M%S', danmaku.time)
            })

        if hasattr(danmaku, 'user') and hasattr(danmaku, 'text'):
            self.db.plain.insert_one({
                'roomid':danmaku.roomid,
                'user':danmaku.user,
                'text':danmaku.text,
                'time':time.strftime('%y%m%d-%H%M%S', danmaku.time)
                })

class TTSHandler(SimpleDanmakuHandler):

    def __init__(self):
        print 'start macTTS...'
        self.sayLOCK = threading.Lock()
        self.saySentences = []
        self.startTTSThread()
    
    def startTTSThread(self):
        thread.start_new_thread(self.sayThread, ())

    def handleDanmaku(self, danmaku):
        super(TTSHandler, self).handleDanmaku(danmaku)
        if hasattr(danmaku, 'text'):
           self.toSay(danmaku.text)

    def say(self, s):
        t = re.sub(r'23[3]+', ' 2 3 3 ', s)
        t = re.sub(r'66[6]+', ' 6 6 6 ', t)
        cmd = 'say \'%s\'' % (t)
        if DEBUG: print cmd
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

class NotifcationHandler(SimpleDanmakuHandler):

    def __init__(self):
        print 'start macNotification...'
        self.notificationTimers = {}

    def handleDanmaku(self, danmaku):
        super(NotifcationHandler, self).handleDanmaku(danmaku)
        if hasattr(danmaku, 'user') & hasattr(danmaku, 'text'):
           self.showMacNotification(danmaku.user, danmaku.text)

    def showMacNotification(self, title, content):
        title = title.replace('\'', ' ')
        content = content.replace('\'', ' ')
        cmd = "terminal-notifier -title '%s' -message '%s' -group '%s' > /dev/null" % (title, content, title)
        subprocess.Popen(cmd, shell=True)
        t = threading.Timer(10, self.closeMacNotification, (title, ))
        t.start()
        if title in self.notificationTimers: self.notificationTimers[title].cancel()
        self.notificationTimers[title] = t

    def closeMacNotification(self, group):
        cmd = "terminal-notifier -remove '%s' > /dev/null" % group
        subprocess.Popen(cmd, shell=True)

class GiftResponseHandler(SimpleDanmakuHandler):

    def __init__(self, sender):
        print 'start gift response...'
        self.startGiftResponseThread()
        self.gifts = []
        self.sender = sender
        self.LOCK = threading.Lock()

    def handleDanmaku(self, danmaku):
        super(GiftResponseHandler, self).handleDanmaku(danmaku)
        if hasattr(danmaku, 'json'):
            raw = danmaku.json
            if raw['cmd'] == 'SEND_GIFT':
                data = raw['data']
                uname, num, giftName = data['uname'].encode('utf-8'), data['num'], data['giftName'].encode('utf-8')
                self.LOCK.acquire()
                self.gifts += [(uname, num, giftName)]
                self.LOCK.release()
        
    def giftResponseThread(self):
        while 1:
            self.LOCK.acquire()
            if self.gifts:
                uname, num, giftName = self.gifts[0]
                for t_uname, t_num, t_giftName in self.gifts[1:]:
                    num = '好多'
                    if t_uname != uname: uname = '大家'
                    if t_giftName != giftName: giftName = '礼物'
                self.sender.sendDanmaku(self.roomid, '谢谢%s送的%s个%s' % (uname, str(num), giftName))
                while self.gifts: self.gifts.pop()
            self.LOCK.release()
            time.sleep(2)

    def startGiftResponseThread(self):
        thread.start_new_thread(self.giftResponseThread, ())

class RewardResponseHandler(SimpleDanmakuHandler):

    def __init__(self, sender):
        print 'start smallTV response...'
        self.sender = sender
        self.date_format = '%H:%M:%S'

    def handleDanmaku(self, danmaku):
        super(RewardResponseHandler, self).handleDanmaku(danmaku)
        if hasattr(danmaku, 'json'):
            raw = danmaku.json
            if raw['cmd'] in ['SYS_MSG']: 
                if 'roomid' in raw:
                    roomid = str(raw['roomid'])
                    tm = time.strftime(self.date_format, time.localtime(time.time() + 180 + 18000))
                    self.sender.sendDanmaku(self.roomid, '%s房间小电视啦，有效期至%s' % (roomid, tm))

class AutoRewardHandler(SimpleDanmakuHandler):

    def __init__(self, sender):
        print 'start auto reward smallTV...'
        self.sender = sender

    def handleDanmaku(self, danmaku):
        super(AutoRewardHandler, self).handleDanmaku(danmaku)
        if hasattr(danmaku, 'json'):
            raw = danmaku.json
            if raw['cmd'] in ['SYS_MSG']: 
                if 'roomid' in raw:
                    roomid = str(raw['roomid'])
                    self.sender.joinSmallTV(roomid, raw['tv_id'])

def main():
    pass

if __name__ == '__main__':
    main()
