#!/usr/bin/python
#coding=utf-8
import requests
import time 

SEND_URL = 'http://live.bilibili.com/msg/send'

f = open(r'cookie.txt','r')
cookies = {}
for line in f.read().split(';'):
    name, value = line.strip().split('=', 1)
    cookies[name] = value

def sendDanmuku(roomid, content):
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
    #print r.status_code, r.content

if __name__ == '__main__':
    while 1:
        content = raw_input()
        sendDanmuku(90012, content)
