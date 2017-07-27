#!/usr/bin/python
#coding=utf-8
import requests
import json
import time 
import sys

SEND_URL = 'http://live.bilibili.com/msg/send'
TV_URL = 'http://api.live.bilibili.com/SmallTV/join'
QUERY_NEED_YOU = 'http://api.live.bilibili.com/activity/v1/NeedYou/getLiveInfo'
NEED_YOU_URL = 'http://api.live.bilibili.com/activity/v1/NeedYou/getLiveAward'
QUERY_SUMMER_URL = 'http://api.live.bilibili.com/activity/v1/SummerBattle/check'
SUMMER_URL = 'http://api.live.bilibili.com/activity/v1/SummerBattle/join'

class Sender(object):

    def __init__(self, cookies):
        self.cookies = cookies
        self.lightenIds = set()
        self.raffleIds = set()

    def sendDanmaku(self, roomid, content, color='white'):
        try:
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
            r = requests.post(SEND_URL, data=params, cookies=self.cookies)
            result = r.content
            raw = json.loads(result)
            if raw['code'] != 0: print raw['msg']
            return True
        except:
            return False

    
    def joinSmallTV(self, roomid, tv_id):
        params = {
                'roomid':roomid,
                'id':tv_id,
                '_':int(time.time() * 100)
                }
        r = requests.get(TV_URL, params=params, cookies=self.cookies)
        result = r.content
        raw = json.loads(result)
        if raw['code'] != 0: print raw['msg']

    def _joinNeedYou(self, roomid, lightenId):
        params = {
                'roomid':roomid,
                'lightenId':lightenId
                }
        r = requests.post(NEED_YOU_URL, data=params, cookies=self.cookies)
        result = r.content
        raw = json.loads(result)
        #if raw['code'] != 0: print raw['msg']
        #print raw['msg']

    def joinNeedYou(self, roomid):
        params = {
                'roomid':roomid
                }
        r = requests.get(QUERY_NEED_YOU, params=params, cookies=self.cookies)
        result = r.content
        raw = json.loads(result)
        if raw['code'] == 0 and 'lightenId' in result:
            for d in raw['data']:
                lightenId = d['lightenId']
                if lightenId not in self.lightenIds:
                    self._joinNeedYou(roomid, lightenId)
                    self.lightenIds.add(lightenId)

        #if raw['code'] != 0: print raw['msg']
        #print self.lightenIds

    def _joinSummer(self, roomid, raffleId):
        params = {
                'roomid':roomid,
                'raffleId':raffleId
                }
        r = requests.post(SUMMER_URL, data=params, cookies=self.cookies)
        result = r.content
        raw = json.loads(result)
        if raw['code'] != 0: print raw['msg']
        #print raw['msg']

    def joinSummer(self, roomid, giftId):
        #print 'summer', roomid, giftId
        params = {
                'roomid':roomid
                }
        r = requests.get(QUERY_SUMMER_URL, params=params, cookies=self.cookies)
        result = r.content
        raw = json.loads(result)
        #print raw #{"code":0,"msg":"success","message":"success","data":[{"raffleId":"13878","type":"waterBattle","from":"bchdy","time":59,"status":1}]}
        if raw['code'] == 0:
            for d in raw['data']:
                raffleId = d['raffleId']
                if raffleId not in self.raffleIds:
                    self._joinSummer(roomid, raffleId)
                    self.raffleIds.add(raffleId)

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
