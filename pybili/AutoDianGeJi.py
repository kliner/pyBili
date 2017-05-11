#!/usr/bin/python
#coding=utf-8
import bili
import bili_sender
import bili_config
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
    state = 'play'
    timer = None
    config = bili_config.Config()
    sender = bili_sender.Sender(config.cookies)
    skip = False

    def __init__(self, roomid):
        self.roomid = roomid
        self.loadMusic()
        thread.start_new_thread(self.musicThread, ())

    def clear(self): 
        print("\033c")
        if self.p.filename: 
            print '正在播放: ', self.p.filename[:-4]

    def printHelp(self):
        print('发 \'点歌\' 进入 点歌模式，在点歌模式下发 \'搜索 关键字\' 搜索列表，在点歌模式下发送 \'点歌 ID\' 完成点歌。发送 \'退出\' 结束点歌。请在五分钟内完成全部操作哦～')

    def printToPlay(self):
        print '当前待播放列表：'
        for u, m in self.to_play_lst: print '%s 点了\t: %s' % (u, m) 

    def loadMusic(self):
        self.all_music = [f[:-4] for f in os.listdir(self.lib_path) if f[-4:] == '.mp3']
        if DEBUG: print self.all_music[0], len(self.all_music)
        
    def playMusic(self, name):
        if DEBUG: 
            print 'player state:', self.p.is_alive()
            print 'self state:', self.state
        while self.state != 'play': time.sleep(1)
        self.p.stop()
        self.p.loadfile(self.lib_path + name + '.mp3')
        time.sleep(0.5)
        if DEBUG: print 'playing ', self.p.filename
        self.clear()
        if self.cur_user: print '当前操作者：', self.cur_user
        self.printToPlay()

        self.p.volume = 8
        length = self.p.length
        self.p.pause()
        if DEBUG: print length
        for i in xrange(int(length)):
            if self.skip:
                if DEBUG: print 'skip play ', name, self.p.filename
                self.p.stop()
                self.skip = False
                break
            time.sleep(1)
        else:
            if DEBUG: print 'finish play ', name, self.p.filename


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
        if self.cur_user == user: 
            self.cur_user = None
            self.clear()
            self.printToPlay()
            print '五分钟到了哦～'

    def match(self, key, music):
        if key in music.lower(): return True
        keys = key.split(' ')
        if len(keys) > 1: 
            if all(k in music.lower() for k in keys): return True
        
    def handleDanmaku(self, danmaku):
        body = danmaku.rawData
        if danmaku.action == 5:
            raw = json.loads(body)
            if DEBUG: print raw
            if 'info' in raw:
                info = raw['info']
                user = info[2][1].encode('utf-8')
                manager = info[2][2]
                content = info[1].encode('utf-8')
                if manager and content in ['切歌']:
                    self.skip = True

                if content in ['点歌', '點歌']: 
                    if not self.cur_user:
                        self.cur_user = user
                        self.printHelp()
                        print '当前操作者：' + user
                        self.timer = threading.Timer(300, self.localTimerThread, (user, ))
                        self.timer.start()
                        self.sender.sendDanmaku(self.roomid, '%s开始点歌～' % self.cur_user)
                    else:
                        self.sender.sendDanmaku(self.roomid, '%s正在点歌, 请等一下哦' % self.cur_user)
                elif not self.cur_user and content[:6] in ['点歌', '點歌']: 
                    self.cur_user = user
                    key = content[6:].strip().lower()
                    self.clear()
                    self.printHelp()
                    print '当前操作者：' + user
                    self.timer = threading.Timer(300, self.localTimerThread, (user, ))
                    self.timer.start()
                    self.sender.sendDanmaku(self.roomid, '%s开始点歌～' % self.cur_user)
                    print '搜索 %s 的结果列表：' % key 
                    for i, t in enumerate(self.all_music):
                        if self.match(key, t): print '%d\t: %s' % (i+1, t) 
                elif user == self.cur_user and content[:6] in ['搜索']:
                    self.clear()
                    key = content[6:].strip().lower()
                    if user != 'klikli': self.sender.sendDanmaku(self.roomid, '搜索 %s 中...' % key)
                    print '搜索 %s 的结果列表：' % key 
                    for i, t in enumerate(self.all_music):
                        if self.match(key, t): print '%d\t: %s' % (i+1, t) 
                    print '切歌时候会导致搜索结果丢失，请注意重新搜索哦'
                elif user == self.cur_user and content[:6] in ['点歌', '點歌']: 
                    try:
                        i = int(content[6:].strip())
                        music = self.all_music[i-1]
                        if DEBUG: print user, i, music
                        self.LOCK.acquire()
                        if len(self.to_play_lst) < 10:
                            if not any([1 for _, name in self.to_play_lst if name == music]):
                                self.to_play_lst += [(user, music)]
                        self.LOCK.release()
                        self.clear()
                        self.printToPlay()
                        self.sender.sendDanmaku(self.roomid, '[%s...]点歌成功' % music[:15])
                    except Exception, e:
                        if DEBUG: print e
                        self.sender.sendDanmaku(self.roomid, '请输入正确的点歌指令哦')
                elif user == self.cur_user and content.lower() in ['退出', 'exit', '结束', 'quit']: 
                    self.sender.sendDanmaku(self.roomid, '欢迎再来点歌哦～')
                    self.cur_user = None
                    if self.timer: self.timer.cancel()
                    self.clear()
                    self.printToPlay()
                elif user == 'klikli' and content == 'reload':
                    self.loadMusic()
                    print '重新加载歌曲库...'

def main():
    argv = sys.argv
    roomid = 90012
    if len(argv) == 2:
        roomid = int(argv[1])

    danmakuHandler = DanmakuHandler(roomid)
    py = bili.BiliHelper(roomid, danmakuHandler)
    while 1:
        cmd = raw_input().strip()
        if cmd == 'p':
            danmakuHandler.p.pause()
            if danmakuHandler.state == 'pause': 
                danmakuHandler.state = 'play'
                print 'play'
            elif danmakuHandler.state == 'play': 
                danmakuHandler.state = 'pause'
                print 'pause'
        elif cmd == 'r':
            danmakuHandler.loadMusic()

                        
if __name__ == '__main__':
    main()
