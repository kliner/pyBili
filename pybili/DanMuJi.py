#!/usr/bin/python
#coding=utf-8
import bili
import bili_sender
import bili_config
import struct
import time
import json
import sys
import signal

from handlers import *

DEBUG = 0

class DanmakuHandler(bili.DanmakuHandler):
    #log = open('/Users/kliner/blog/' + time.strftime('%d-%H%M%S', time.localtime(time.time() + 18000)) + '.log', 'w')

    def __init__(self, roomid, config):
        self.cnt = 9
        self.showTime = config.get(roomid, "ShowTime", False)
        #self.color = config.get(roomid, "DanmakuColor", "white")
    
        print '----------------------------'
        print 'showTime...', self.showTime 
        #print 'danmakuColor...', self.color
        self.date_format = '%H:%M:%S'
            
        signal.signal(signal.SIGINT, self.signal_handler)

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

            elif raw['cmd'] == 'SEND_GIFT': pass
            elif raw['cmd'] == 'WELCOME': pass 
            elif raw['cmd'] == 'WELCOME_GUARD': pass 
            elif raw['cmd'] in ['SYS_GIFT']: pass
            elif raw['cmd'] in ['SYS_MSG']: pass
            else: 
                if DEBUG: print raw
        else:
            if DEBUG: print 'unknown action,' + repr(danmaku) 
    
    def signal_handler(self, signal, frame):
        print('exit... saving info...')
        #self.log.close()
        sys.exit(0)

def initHandlers(roomid):
    config = bili_config.Config()
    cookies = config.cookies

    handler = DanmakuHandler(roomid, config = config)
    sender = bili_sender.Sender(cookies)

    danmakuHandlers = [handler]
    if config.get(roomid, "RecordDanmaku", False): danmakuHandlers += [MongoHandler()]
    if config.get(roomid, "MacTTS", False): danmakuHandlers += [TTSHandler()]
    if config.get(roomid, "MacNotification", False): danmakuHandlers += [NotifcationHandler()]
    if config.get(roomid, "GiftResponse", False): danmakuHandlers += [GiftResponseHandler(sender)]
    if config.get(roomid, "AwardSmallTV", False): danmakuHandlers += [AutoRewardHandler(sender)]
    if config.get(roomid, "SmallTVHint", False): danmakuHandlers += [RewardResponseHandler(sender)]
    if config.get(roomid, "AwardSummer", False): danmakuHandlers += [AutoSummerRewardHandler(sender)]
    return danmakuHandlers

def main():
    argv = sys.argv
    roomid = 90012
    if len(argv) == 2: roomid = int(argv[1])

    py = bili.BiliHelper(roomid, *initHandlers(roomid))
    
    config = bili_config.Config()
    cookies = config.cookies
    sender = bili_sender.Sender(cookies)
    while 1:
        cmd = raw_input()
        sender.sendDanmaku(roomid, cmd)

if __name__ == '__main__':
    main()
