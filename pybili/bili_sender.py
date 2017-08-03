#!/usr/bin/python
#coding=utf-8
import requests
import json
import time 
import sys
import thread
import logging
import logging.handlers

SEND_URL = 'http://live.bilibili.com/msg/send'
TV_URL = 'http://api.live.bilibili.com/SmallTV/join'
QUERY_SUMMER_URL = 'http://api.live.bilibili.com/activity/v1/SummerBattle/check'
SUMMER_URL = 'http://api.live.bilibili.com/activity/v1/SummerBattle/join'

class Sender(object):

    def _initLogger(self, logger):
        logger.setLevel(logging.DEBUG)
        ch = logging.handlers.TimedRotatingFileHandler('bili_sender.log')
        logger.addHandler(ch)
        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # add formatter to ch
        ch.setFormatter(formatter)
        self.logger = logger
        self.logger.info('logger bili_sender init success')

    def __init__(self, cookies):
        logger = logging.getLogger('bili_sender')
        if not logger.handlers:
            self._initLogger(logger)
        
        self.cookies = cookies
        self.lightenIds = set()
        self.raffleIds = set()

    def _get(self, url, params):
        try:
            r = requests.get(url, params=params, cookies=self.cookies)
            result = r.content
            raw = json.loads(result)
            if raw['code'] != 0: 
                self.logger.debug(raw)
                self.logger.warn(raw['msg'])
            else: return raw
        except:
            pass

    def _post(self, url, params):
        try:
            r = requests.post(url, data=params, cookies=self.cookies)
            result = r.content
            raw = json.loads(result)
            if raw['code'] != 0: 
                self.logger.debug(raw)
                self.logger.warn(raw['msg'])
            else: return raw
        except:
            pass

    def sendDanmaku(self, roomid, content, color='white'):
        content = content.strip()
        if not content: return
        if color == 'blue': color = 6737151
        elif color == 'green': color = 8322816
        else: color = 16777215 # white
        params = {
            "color":color, 
            "fontsize":25,
            "mode":1,
            "msg":content,
            "rnd":int(time.time()),
            "roomid":roomid
            }
        return self._post(SEND_URL, params)

    def joinSmallTV(self, roomid, tv_id):
        params = {
                'roomid':roomid,
                'id':tv_id,
                '_':int(time.time() * 100)
                }
        self._get(TV_URL, params)

    def _joinSummer(self, roomid, raffleId):
        params = {
                'roomid':roomid,
                'raffleId':raffleId
                }
        r = self._post(SUMMER_URL, params)
        if r: self.logger.debug('join summer: %s' % r['msg'])

    def joinSummer(self, roomid, giftId):
        params = {
                'roomid':roomid
                }
        r = self._get(QUERY_SUMMER_URL, params)
        if r:
            for d in r['data']:
                raffleId = d['raffleId']
                if raffleId not in self.raffleIds:
                    self._joinSummer(roomid, raffleId)
                    self.raffleIds.add(raffleId)
                    thread.start_new_thread(self.checkSummer, (roomid, raffleId))

    def checkSummer(self, roomid, raffleId):
        time.sleep(65)
        url = 'http://api.live.bilibili.com/activity/v1/SummerBattle/notice'
        params = {
                'roomid':roomid,
                'raffleId':raffleId
                }
        r = self._get(url, params)
        if r:
            if r['data']['gift_id'] == 76: self.logger.info('get!')
            elif r['data']['gift_id'] == -1: self.logger.info('empty!')
            else: self.logger.warn(raw['data'])

def main():
    import bili_config
    argv = sys.argv
    config = bili_config.Config()
    sender = Sender(config.cookies)
    while 1:
        content = raw_input()
        sender.sendDanmaku(int(argv[1]), content)

if __name__ == '__main__':
    main()
