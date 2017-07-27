#!/usr/bin/env python      
import sys
import Tkinter as tk       
import DanMuJi
import bili
import re
import emoji_list
import bili_config

DEBUG = 0

class Application(tk.Frame):
    def __init__(self, master=None, w=40, h=32):
        tk.Frame.__init__(self, master)   
        
        self.mWIDTH, self.mHEIGHT = w, h
        self.grid()
        self.createWidgets()

    def createWidgets(self):
        self.w = tk.Text(self, height=self.mHEIGHT, width=self.mWIDTH, font=("simhei", 20))
        #self.w.pack(expand=tk.YES, fill=tk.BOTH)
        self.w.grid(row=0, column=0, sticky='nsew')

        self.quitButton = tk.Button(self, text='Quit', command=self.quit)            
        self.quitButton.grid(row=1, column=0)

class GUIDanmakuHandler(bili.SimpleDanmakuHandler):

    def __init__(self, w):
        self.w = w
        self.cnt = 0
        self.all_emoji = emoji_list.all_emoji

    def stripEmoji(self, s):
        for e in self.all_emoji:
            if e not in '0123456789#*': s = s.replace(e, '')
        return s

    def handleDanmaku(self, danmaku):
        super(GUIDanmakuHandler, self).handleDanmaku(danmaku)
        if hasattr(danmaku, 'user') & hasattr(danmaku, 'text'):
            if self.cnt > 100: self.w.delete(1.0, 2.0)
            else: self.cnt += 1
            user = self.stripEmoji(danmaku.user)
            text = self.stripEmoji(danmaku.text)
            if text and user: self.w.insert(tk.END, '%s : %s\n' % (user, text)) 
            self.w.see(tk.END)

def main():
    argv = sys.argv
    roomid = 90012
    if len(argv) == 2: roomid = int(argv[1])
    c = bili_config.Config()
    print 'width:', c.w, 'height', c.h
    
    app = Application(w=c.w, h=c.h)
    danmakuHandlers = DanMuJi.initHandlers(roomid) + [GUIDanmakuHandler(app.w)]
    bili.BiliHelper(roomid, *danmakuHandlers)
    app.master.title('bilibili danmaku helper')
    app.mainloop()                           
    
if __name__ == '__main__':
    main()
