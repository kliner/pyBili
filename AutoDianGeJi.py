#!/usr/bin/python
#coding=utf-8
import bili
import bili_sender
import sys
import thread
import struct
import time
import json
import os
import mplayer
import random
import threading

reload(sys)  
sys.setdefaultencoding('utf8')

DEBUG = 0

class DanmakuHandler(bili.DanmakuHandler):
    
    lib_path = '/Users/kliner/Music/lib/'
    all_music = []
    to_play_lst = []
    p = mplayer.Player()
    LOCK = threading.Lock()
    cur_user = None

    def __init__(self):
        self.loadMusic()
        thread.start_new_thread(self.musicThread, ())

    def clear(self): 
        print("\033c")
        if self.p.filename: 
            print '正在播放: ', self.p.filename[:-4]

    def printHelp(self):
        print('发 \'点歌\' 进入 点歌模式，在点歌模式下发 \'搜索 关键字\' 搜索列表，在点歌模式下发送 \'点歌 ID\' 完成点歌。请在五分钟内完成全部操作哦～')

    def printToPlay(self):
        print '当前待播放列表：'
        for u, m in self.to_play_lst: print '%s 点了\t: %s' % (u, m) 

    def loadMusic(self):
        self.all_music += [f[:-4] for f in os.listdir(self.lib_path) if f[-4:] == '.mp3']
        if DEBUG: print self.all_music[0], len(self.all_music)
        
    def playMusic(self, name):
        self.p.loadfile(self.lib_path + name + '.mp3')
        if DEBUG: print 'playing ', self.p.filename
        if not self.cur_user: 
            self.clear()
            self.printToPlay()

        self.p.volume = 5
        length = self.p.length
        self.p.pause()
        time.sleep(length)

    def musicThread(self):
        while 1:
            if self.to_play_lst:
                self.LOCK.acquire()
                u, name = self.to_play_lst.pop(0)
                self.LOCK.release()
                self.playMusic(name)
            else:
                name = random.choice(self.all_music)
                self.playMusic(name)
            if not self.cur_user:
                self.printToPlay()

    def localTimerThread(self, user):
        time.sleep(300)
        if self.cur_user == user: 
            self.cur_user = None
            self.printToPlay()

    def handleDanmaku(self, danmaku):
        body = danmaku.rawData
        if danmaku.action == 5:
            raw = json.loads(body)
            if 'info' in raw:
                info = raw['info']
                user = info[2][1].encode('utf-8')
                content = info[1].encode('utf-8')
                if content in ['点歌', '點歌']: 
                    if not self.cur_user:
                        self.cur_user = user
                        self.printHelp()
                        print '当前操作者：' + user
                        thread.start_new_thread(self.localTimerThread, (user, ))

                    else:
                        bili_sender.sendDanmaku(roomid, '%s正在点歌, 请等一下哦' % self.cur_user)
                elif user == self.cur_user and content[:6] in ['搜索']:
                    self.clear()
                    key = content[6:].strip()
                    print '搜索 %s 的结果列表：' % key 
                    for i, t in enumerate(self.all_music):
                        if key in t: print '%d\t: %s' % (i+1, t) 
                elif user == self.cur_user and content[:6] in ['点歌', '點歌']: 
                    try:
                        i = int(content[6:].strip())
                        m = self.all_music[i-1]
                        self.LOCK.acquire()
                        self.to_play_lst += [(user, m)]
                        self.cur_user = None
                        self.LOCK.release()
                        self.clear()
                        self.printToPlay()
                    except Exception, e:
                        bili_sender.sendDanmaku(roomid, '请输入正确的点歌指令哦')
                    
                        
if __name__ == '__main__':
    argv = sys.argv
    roomid = 90012
    if len(argv) == 2:
        roomid = int(argv[1])

    danmakuHandler = DanmakuHandler()
    py = bili.BiliHelper(roomid, danmakuHandler)
    while 1:
        cmd = raw_input()
