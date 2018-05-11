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
import subprocess
import traceback
import logging
import logging.handlers

reload(sys)  
sys.setdefaultencoding('utf8')

DIVIDER = '-' * 15

HOME_PATH = os.path.expanduser("~")
LIB_PATH = HOME_PATH + '/Music/lib/'


class Music(object):


    def __init__(self, n, s, e): 
        self.name, self.sname, self.ename = n, s, e

    def __str__(self): 
        return self.searchKey()

    def __repr__(self): 
        return self.__str__()
    
    def searchKey(self): 
        return '%s %s %s' % (self.name, self.sname, self.ename)

    def getPath(self):
        return LIB_PATH + self.name


class MusicPlayer(object):
    
    
    def __init__(self):
        self.p = mplayer.Player()
        self.p.volume = 20
        skip = False

    def play(self, music):
        self.p.stop()
        self.p.loadfile(music.getPath())
        time.sleep(0.5) # wait mplayer to load the file
        print self.p.length # dont know WTF, without will return None
        length = self.p.length
        self.p.pause()
        return length

    def stop(self):
        self.p.stop()

    def pause(self):
        self.p.pause()


class MusicManager(object):


    def __init__(self, path):
        self.all_musics = []
        self.to_play_musics = []
        self.p = MusicPlayer()
        self.LOCK = threading.Lock()
        self.skip = False
        self.lib_path = path
        self.current_music = None
        self._load_lib()


    def _music_thread(self):
        while 1:
            if self.to_play_musics:
                self.LOCK.acquire()
                u, music = self.to_play_musics.pop(0)
                self.LOCK.release()
                self._play_music(music)
            else:
                music = random.choice(self.all_musics)
                self._play_music(music)

    def _play_music(self, music):
        self.current_music = music
        length = self.p.play(music)
        for i in xrange(int(length)):
            if self.skip:
                self.skip = False
                self.p.stop()
                break
            time.sleep(1)

    def _load_lib(self):
        origin_music = [f[:-4] for f in os.listdir(self.lib_path) if f[-4:] == '.mp3'] # load mp3 files in the lib_path
        with open('%s/.pybili.ti' % self.lib_path, 'w') as f:
            f.write('\n'.join(origin_music))
        
        try:
            # tranlate to Traditional Chinese
            subprocess.Popen('opencc -i %s/.pybili.ti -o %s/.pybili.to -c t2s.json' % (self.lib_path, self.lib_path), shell=True)

            with open('%s/.pybili.to' % self.lib_path, 'r') as f:
                lst = f.read().split('\n')
                self.all_musics = [Music(n,s,n) for n, s in zip(origin_music, lst)]
        except:
            print('init cc error')
            self.all_musics = [Music(n,n,n) for n in origin_music]

    def start_playing(self):
        thread.start_new_thread(self._music_thread, ())

    def add_to_play_list(self, new_music):
        self.LOCK.acquire()
        if len(self.to_play_musics) < 10:
            if not any([music.name == new_music.name for _, music in self.to_play_musics]):
                # not exist in the list, add it
                self.to_play_musics += [(self.cur_user, new_music)]
        self.LOCK.release()

    def search_music(self, name):
        result = []
        for i, m in enumerate(self.all_music):
            if self.match(key, m): result += [(i+1, m)]

        if len(result) == 1: self.addToPlayList(result[0])
        return result

    def _match(self, key, music):
        music_search_key = music.searchKey()
        if key in music_search_key.lower(): return True
        keys = key.split(' ')
        if len(keys) > 1: 
            if all(k in music_search_key.lower() for k in keys): return True

    def skip(self):
        self.skip = True

    def get_current_playing(self):
        return self.current_music

class DBHelper(object):

    def __init__(self):
        try:
            import pymongo
            from pymongo import MongoClient
            from bson.objectid import ObjectId
            print 'start db...'
            self.client = MongoClient()
            self.db = self.client.music
        except:
            print 'mongodb service down!\nto install:[brew install mongodb]\nto start:[brew services start mongodb]'
            self.db = None

    def selectFavorite(self, danmaku):
        if self.db:
            cursor = self.db.fav.find({'user': danmaku.user}).sort([('time', pymongo.ASCENDING)])
            return [d['name'] for d in cursor]

    def removeFavorite(self, danmaku, name):
        if self.db:
            cursor = self.db.fav.find({'user': danmaku.user}).sort([('time', pymongo.DESCENDING)])
            i = 0
            for d in cursor:
                i += 1
                if i >= 9:
                    try:
                        self.db.fav.delete_one({'_id': ObjectId(d['_id'])})
                    except:
                        if DEBUG: traceback.print_exc()

    def insertFavorite(self, danmaku, name):
        if self.db:
            favs = self.selectFavorite(danmaku)
            if DEBUG: print favs
            if len(favs) >= 9:
                self.removeFavorite(danmaku, name)

            self.db.fav.insert_one({
                'user':danmaku.user,
                'name':name,
                'time':time.strftime('%y%m%d-%H%M%S', danmaku.time)
                })
            return self.selectFavorite(danmaku)

class DanmakuHandler(bili.SimpleDanmakuHandler):
    home_path = os.path.expanduser("~")
    lib_path = home_path + '/Music/lib/'
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
        self.db = DBHelper()

    def clear(self): 
        print("\033c")
        if self.p.filename: print '正在播放: ', self.p.filename[:-4]

    def printHelp(self): print('发 \'点歌\' 进入 点歌模式，在点歌模式下发 \'搜索 关键字\' 搜索列表，在点歌模式下发送 \'点歌 ID\' 完成点歌。发送 \'退出\' 结束点歌。请在五分钟内完成全部操作哦～')

    def printToPlay(self):
        print '当前待播放列表：'
        for u, m in self.to_play_lst: print '%s 点了\t: %s' % (u, m.name) 

    def loadMusic(self):
        origin_music = [f[:-4] for f in os.listdir(self.lib_path) if f[-4:] == '.mp3']
        with open('%s/.pybili.ti' % self.home_path, 'w') as f:
            f.write('\n'.join(origin_music))
        
        try:
            subprocess.Popen('opencc -i %s/.pybili.ti -o %s/.pybili.to -c t2s.json' % (self.home_path, self.home_path), shell=True)

            with open('%s/.pybili.to' % self.home_path, 'r') as f:
                lst = f.read().split('\n')
                self.all_music = [Music(n,s,n) for n, s in zip(origin_music, lst)]
        except:
            print 'init cc error'
            self.all_music = [Music(n,n,n) for n in origin_music]
           
        if DEBUG: print self.all_music
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

        self.p.volume = 20
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
                u, music = self.to_play_lst.pop(0)
                self.LOCK.release()
                self.playMusic(music.name)
            else:
                music = random.choice(self.all_music)
                self.playMusic(music.name)
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

    def search(self, key):
        result = []
        for i, m in enumerate(self.all_music):
            if self.match(key, m.searchKey()): result += [(i+1, m.name)]
        if len(result) == 0: 
            self.sender.sendDanmaku(self.roomid, 'Sorry...这里没有对应的歌')
        elif len(result) == 1:
            self.addToPlayList(result[0][0])
        else:
            if self.cur_user != 'klikli': self.sender.sendDanmaku(self.roomid, '搜索 %s 中...' % key)
            print '搜索 %s 的结果列表：' % key 
            for i, t in result:
                print '%d\t: %s' % (i, t)
            print '切歌时候会导致搜索结果丢失，请注意重新搜索哦'
        
    def addToPlayListByName(self, name):
        to_add = Music(name, name, name)
        self.LOCK.acquire()
        if len(self.to_play_lst) < 10:
            if not any([1 for _, music in self.to_play_lst if music.name == to_add.name]):
                self.to_play_lst += [(self.cur_user, to_add)]
        self.LOCK.release()
        self.clear()
        self.printToPlay()
        self.sender.sendDanmaku(self.roomid, '[%s...]点歌成功' % to_add.name[:15])

    def addToPlayList(self, i):
        to_add = self.all_music[i-1]
        self.addToPlayListByName(to_add.name)

    def printFav(self, danmaku):
        print DIVIDER
        print '%s的收藏列表: ' % danmaku.user
        favs = self.db.selectFavorite(danmaku)
        for i, name in enumerate(favs):
            print '%d, %s' % (i+1, name)

    def handleDanmaku(self, danmaku):
        super(DanmakuHandler, self).handleDanmaku(danmaku)
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

                if content in ['查看收藏','收藏列表']:
                    if (not self.cur_user) or (self.cur_user == user):
                        self.clear()
                        self.printToPlay()
                        self.printFav(danmaku)
                elif content[:6] in ['收藏']:
                    try:
                        if len(content) == 6: to_add = self.p.filename[:-4]
                        else: 
                            i = int(content[6:].strip())
                            to_add = self.all_music[i-1].name
                        self.db.insertFavorite(danmaku, to_add)
                        self.sender.sendDanmaku(self.roomid, '[%s...]收藏成功' % to_add[:15])
                    except Exception, e:
                        if DEBUG: traceback.print_exc()
                        self.sender.sendDanmaku(self.roomid, '请输入正确的指令哦')
                elif content[:6] in ['点歌', '點歌']: 
                    if not self.cur_user:
                        self.cur_user = user
                        self.printHelp()
                        print '当前操作者：' + user
                        self.timer = threading.Timer(300, self.localTimerThread, (user, ))
                        self.timer.start()
                        self.sender.sendDanmaku(self.roomid, '%s开始点歌～' % self.cur_user)
                    if self.cur_user == user:
                        k = content[6:].strip()
                        if not k: return
                        try:
                            if k[0] == '@': # play from favorite
                                i = int(k[1:])
                                favs = self.db.selectFavorite(danmaku)
                                self.addToPlayListByName(favs[i-1])
                            else:
                                if k.isdigit(): self.addToPlayList(int(k)) # play by id
                                else: self.search(k.lower()) # search
                        except Exception, e:
                            if DEBUG: print e
                            self.sender.sendDanmaku(self.roomid, '请输入正确的点歌指令哦')
                    else:
                        self.sender.sendDanmaku(self.roomid, '%s正在点歌, 请等一下哦' % self.cur_user)
                elif user == self.cur_user and content[:6] in ['搜索']:
                    self.clear()
                    key = content[6:].strip().lower()
                    self.search(key)
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
        else:
            danmakuHandler.search(cmd)

                        
if __name__ == '__main__':
    main()
