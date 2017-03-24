#!/usr/bin/python
#coding=utf-8
import requests
import json
import time 

SEND_URL = 'http://live.bilibili.com/msg/send'
TV_URL = 'http://api.live.bilibili.com/SmallTV/join'

cookies = {}

def init():
    with open(r'cookie.txt','r') as f:
        try:
            for line in f.read().split(';'):
                name, value = line.strip().split('=', 1)
                cookies[name] = value
        except Exception, e:
            print 'warning! please set correct cookies into \'cookie.txt\''

def sendDanmaku(roomid, content):
    content = content.strip()
    if not content: return
    params = {
        "color":16777215,
        "fontsize":25,
        "mode":1,
        "msg":content,
        "rnd":int(time.time()),
        "roomid":roomid
        }
    r = requests.post(SEND_URL, data=params, cookies=cookies)
    result = r.content
    raw = json.loads(result)
    if raw['code'] != 0: print raw['msg']

def joinSmallTV(roomid, tv_id):
    params = {
            'roomid':roomid,
            'id':tv_id,
            '_':int(time.time() * 100)
            }
    r = requests.get(TV_URL, params=params, cookies=cookies)
    result = r.content
    raw = json.loads(result)
    if raw['code'] != 0: print raw['msg']

if __name__ == '__main__':
    init()
    while 1:
        content = raw_input()
        sendDanmaku(90012, content)
