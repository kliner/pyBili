#!/usr/bin/python
#coding=utf-8
import bili
import sys
import thread
import struct
import time
import json

reload(sys)  
sys.setdefaultencoding('utf8')

DEBUG = 1

class DanmakuHandler(bili.DanmakuHandler):
    
    block_lst = ['圆舞曲', '肖邦', '钟']
    to_play_lst = []
    pending_lst = []
    completed = {}

    def __init__(self):
        self.loadConfig()
        self.output_all()

    def loadConfig(self):
        print '初始化...'
        with open('config.json') as f:
            self.block_lst += [s.encode('utf8') for s in json.loads(f.readline())]
            self.to_play_lst += [s.encode('utf8') for s in json.loads(f.readline())]
            self.pending_lst += [s.encode('utf8') for s in json.loads(f.readline())]
        print '初始化完成'

    def saveConfig(self):
        print '保存数据...'
        with open('config.json', 'w') as f:
            self.block_lst = list(set(self.block_lst))
            f.write(json.dumps(self.block_lst) + '\n')
            f.write(json.dumps(self.to_play_lst) + '\n')
            f.write(json.dumps(self.pending_lst) + '\n')
        print '保存数据完成'

    def clear(self): 
        print("\033c")

    def output_help(self):
        print('操作指南: f-收藏,b-屏蔽,c-已弹奏,d-删除,df-删除收藏,s-显示详细列表,q-退出')

    def output_all(self):
        self.clear()
        print '当前待演奏列表：'
        for i, s in enumerate(self.to_play_lst):
            print '%d.\t%s' % (i+1, s)
        print '--------------------------------'
        print '当前收藏列表：'
        for i, s in enumerate(self.pending_lst):
            print '%d.\t%s' % (i+1, s)
        print '--------------------------------'
        print '已弹奏列表：'
        for k in self.completed.keys():
            print k, '\t', self.completed[k], '次'
        print '--------------------------------'
        self.output_help()

    def output(self):
        self.clear()
        print '当前待演奏列表：'
        for i, s in enumerate(self.to_play_lst):
            print '%d.\t%s' % (i+1, s)

    def handleDanmaku(self, danmaku):
        body = danmaku.rawData
        if danmaku.action == 5: # danmaku packet
            raw = json.loads(body)
            if 'info' in raw:
                info = raw['info']
                s = info[1].encode('utf-8').strip()
                if s[:9] in ['点歌机', '点歌姬', '點歌機', '點歌姬']: return
                if s[:6] in ['点歌', '點歌']: content = s[6:].strip()
                else: return
                if any([1 for keyword in self.block_lst if keyword in content]): return
                if content in self.pending_lst or content in self.to_play_lst: return
                self.to_play_lst += [content]
                self.output()

    def getIdx(self, s, offset):
        try:
            idx = s[offset:]
            if not idx: idx = 0
            else: idx = int(idx) - 1
            return idx
        except Exception, e:
            if DEBUG: print 'error!', e
            return 0

    def parseCommand(self, s):
        try:
            s = s.strip()
            if s == 's': 
                pass
            elif s[:2] == 'df':
                idx = self.getIdx(s, 2)
                if idx < len(self.pending_lst):
                    self.pending_lst.pop(idx)
            elif s[0] == 'd': 
                idx = self.getIdx(s, 1)
                if idx < len(self.to_play_lst):
                    self.to_play_lst.pop(idx)
            elif s[0] == 'b': 
                idx = self.getIdx(s, 1)
                if idx < len(self.to_play_lst):
                    content = self.to_play_lst[idx] 
                    self.block_lst += [content]
                    self.to_play_lst.pop(idx)
            elif s[0] == 'f':
                idx = self.getIdx(s, 1)
                if idx < len(self.to_play_lst):
                    content = self.to_play_lst[idx] 
                    self.pending_lst += [content]
                    self.to_play_lst.pop(idx)
            elif s[0] == 'c':
                idx = self.getIdx(s, 1)
                if idx < len(self.to_play_lst):
                    content = self.to_play_lst[idx] 
                    self.completed[content] = self.completed.get(content, 0) + 1
                    self.to_play_lst.pop(idx)
            elif s[0] == 'q':
                self.saveConfig()
                self.output_all()
                sys.exit(0)
                return
            self.output_all()
        except Exception, e:
            if DEBUG: print 'error!', e

if __name__ == '__main__':
    argv = sys.argv
    roomid = 30040
    if len(argv) == 2:
        roomid = int(argv[1])

    danmakuHandler = DanmakuHandler()
    py = bili.BiliHelper(roomid, danmakuHandler)
    while 1:
        cmd = raw_input()
        if cmd == '': danmakuHandler.output_all()
        elif cmd[0] in 'sbdfrcq': danmakuHandler.parseCommand(cmd)
        else: danmakuHandler.handleDanmaku(cmd)
