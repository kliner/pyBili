#!/usr/bin/env python      
import Tkinter as tk       
import DanMuJi
import bili

DEBUG = 0

class Application(tk.Frame):              
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)   
        self.grid()                       
        self.createWidgets()

    def createWidgets(self):
        self.w = tk.Text(self, height=10)
        self.w.pack(expand=tk.YES, fill=tk.BOTH)
        self.w.grid()

        self.quitButton = tk.Button(self, text='Quit',
            command=self.quit)            
        self.quitButton.grid()            

class GUIDanmakuHandler(bili.SimpleDanmakuHandler):

    def __init__(self, w):
        self.w = w

    def handleDanmaku(self, danmaku):
        super(GUIDanmakuHandler, self).handleDanmaku(danmaku)
        if hasattr(danmaku, 'user') & hasattr(danmaku, 'text'):
            self.w.insert(tk.END, '%s : %s\n' % (danmaku.user, danmaku.text)) 
            self.w.see(tk.END)

def main():
    argv = sys.argv
    roomid = 90012
    if len(argv) == 2: roomid = int(argv[1])

    app = Application()                      
    danmakuHandlers = DanMuJi.initHandlers() + [GUIDanmakuHandler(app.w)]
    bili.BiliHelper(roomid, *danmakuHandlers)
    app.master.title('bilibili danmaku helper')
    app.mainloop()                           
    
if __name__ == '__main__':
    main()
