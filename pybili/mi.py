#!/usr/bin/python
#coding=utf-8
import requests
import json
import time 
import sys
import random

SEND_URL = 'http://live.bilibili.com/msg/send'

class Sender(object):

    def __init__(self, cookies):
        self.cookies = cookies

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
        except:
            print 'send danmaku error:', sys.exc_info()[0]
    

lst = '''
        塞纳河畔 左岸的咖啡
我手一杯 品尝你的美
留下唇印的嘴
花店玫瑰 名字写错谁
告白气球 风吹到对街
微笑在天上飞
你说你有点难追 想让我知难而退
礼物不需挑最贵 只要香榭的落叶
喔 营造浪漫的约会 不害怕搞砸一切
拥有你就拥有 全世界
亲爱的 爱上你 从那天起
甜蜜的很轻易
亲爱的 别任性 你的眼睛
在说我愿意
塞纳河畔 左岸的咖啡
我手一杯 品尝你的美
留下唇印的嘴
花店玫瑰 名字写错谁
告白气球 风吹到对街
微笑在天上飞
你说你有点难追 想让我知难而退
礼物不需挑最贵 只要香榭的落叶
喔 营造浪漫的约会 不害怕搞砸一切
拥有你就拥有 全世界
亲爱的 爱上你 从那天起
甜蜜的很轻易
亲爱的 别任性 你的眼睛
在说我愿意
亲爱的 爱上你 恋爱日记
飘香水的回忆
一整瓶 的梦境 全都有你
搅拌在一起
亲爱的 别任性 你的眼睛
在说我愿意
5片式镜头 ƒ/2.0 光圈
双色温闪光灯
支持 PDAF 相位对焦
暗光画质增强技术
HDR高动态范围调节技术
全景模式
连拍模式
面部识别功能
实时滤镜拍照
第二代36级智能美颜 自拍实时美颜
ƒ/2.0 大光圈 85°大广角
视频通话实时美颜
倒计时自拍
面部识别功能
支持魔镜功能 实时评测颜值
支持阳光屏 强烈阳光下清晰可见屏幕内容
支持夜光屏
支持护眼模式
支持色温调节
        '''.split()

cks = ["sid=cohdat21; fts=1497021168; LIVE_BUVID=146ada79a17e6839cbe254b809986f8e; LIVE_BUVID__ckMd5=deef7b5e401f1ac0; buvid3=3C5D4495-EA05-4335-80FB-8406E4F99B9A15603infoc; DedeUserID=28919882; DedeUserID__ckMd5=6025d570808b12d6; SESSDATA=7d7aee87%2C1499613190%2Cc44752f8; bili_jct=5664bee6709796edbf715b751a6c2061; LIVE_LOGIN_DATA=c27d7350e7c33b0afd725b7230ebdaa5afe00ae6; LIVE_LOGIN_DATA__ckMd5=cd66751c50b04b60; _dfcaptcha=bc59ef133c7755f6d60e9cb24a65768a; attentionData=%7B%22code%22%3A0%2C%22msg%22%3A%22success%22%2C%22message%22%3A%22success%22%2C%22data%22%3A%7B%22count%22%3A0%2C%22open%22%3A1%2C%22has_new%22%3A0%7D%7D; Hm_lvt_8a6e55dbd2870f0f5bc9194cddf32a02=1497021168; Hm_lpvt_8a6e55dbd2870f0f5bc9194cddf32a02=1497021198; F_S_T_28919882=1; user_face=http%3A%2F%2Fi1.hdslb.com%2Fbfs%2Fface%2Fb11d5c14c1445c1b5093e2dcad51d58221282bc7.jpg",
        "sid=j44742hb; fts=1497021328; LIVE_BUVID=067930dfaf06c68c46ddc766599a7198; LIVE_BUVID__ckMd5=dfe68c58efb81910; buvid3=FC19C6FE-314D-4982-AFE2-096CD689581032373infoc; DedeUserID=15653302; DedeUserID__ckMd5=2740846aa032723c; SESSDATA=641a6b54%2C1499613344%2C1eaef350; bili_jct=1e23321cfdfaebc7f0c9b40324cede1d; LIVE_LOGIN_DATA=40db80532a9f5fda6e558afbefae27900f3866e1; LIVE_LOGIN_DATA__ckMd5=2ae63537cd546605; _dfcaptcha=5e52181bcfb3bf52961c3e28fc079a90; attentionData=%7B%22code%22%3A0%2C%22msg%22%3A%22success%22%2C%22message%22%3A%22success%22%2C%22data%22%3A%7B%22count%22%3A0%2C%22open%22%3A1%2C%22has_new%22%3A0%7D%7D; user_face=http%3A%2F%2Fi2.hdslb.com%2Fbfs%2Fface%2F426eca544511d6416f2c7f6c7c3e78bdd6e50579.jpg; F_S_T_15653302=1; Hm_lvt_8a6e55dbd2870f0f5bc9194cddf32a02=1497021329; Hm_lpvt_8a6e55dbd2870f0f5bc9194cddf32a02=1497021352", 
        "sid=la5zn8lk; fts=1497023179; LIVE_BUVID=e77111075c93a9d3c94622dacdcc0505; LIVE_BUVID__ckMd5=51343520b0568123; buvid3=A5F3E262-3402-4605-92E5-255DDF59F4C732358infoc; DedeUserID=35076534; DedeUserID__ckMd5=2864d5fe0301aff3; SESSDATA=9a737022%2C1499615330%2C84b2a1d4; bili_jct=a5f038c4f44d83593ff8f013b9186fba; LIVE_LOGIN_DATA=f537448b1a8480a667edce29e95896d76a95a461; LIVE_LOGIN_DATA__ckMd5=ba6f130d402af57f; _dfcaptcha=c802f04dc6380cc5b660414d50d54ebc; attentionData=%7B%22code%22%3A0%2C%22msg%22%3A%22success%22%2C%22message%22%3A%22success%22%2C%22data%22%3A%7B%22count%22%3A0%2C%22open%22%3A1%2C%22has_new%22%3A0%7D%7D; Hm_lvt_8a6e55dbd2870f0f5bc9194cddf32a02=1497023180; Hm_lpvt_8a6e55dbd2870f0f5bc9194cddf32a02=1497023338; F_S_T_35076534=1; user_face=http%3A%2F%2Fi1.hdslb.com%2Fbfs%2Fface%2Fbdd22abffb6847ca6398365c52eeecf7ac171674.jpg"]

def parseCookie(s):
    c = {}
    s = s.strip()
    if 'cookie:' == s[:7]: s = s[7:] # do strip 
    try:
        for line in s.split(';'):
            name, value = line.strip().split('=', 1)
            c[name] = value
    except:
        pass
    return c

def main():
    import bili_config
    date_format = '%m%d-%H%M%S'
    config = bili_config.Config()
    senders = [Sender(config.cookies)]
    for c in map(parseCookie, cks):
        print c
        senders += [Sender(c)]

    #for s in lst: print s
    print "danmakus count:", len(lst)
    while 1:
        tm = time.localtime(time.time() + 18000)
        mins = int(time.strftime('%M', tm))
        hours = int(time.strftime('%H', tm))
        if 11 <= hours <= 23:
            if 50 <= mins < 60:
                content = random.choice(lst)
                for sender in senders:
                    sender.sendDanmaku(545342, content)
                    #sender.sendDanmaku(90012, "笔芯")
                    print time.strftime(date_format, tm), content
                    time.sleep(30)
            elif mins == 49:
                print time.strftime(date_format, tm)
                time.sleep(10)
            else:
                print time.strftime(date_format, tm)
                time.sleep(60)
        else:
            time.sleep(1800)

if __name__ == '__main__':
    main()
