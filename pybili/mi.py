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

def main():
    import bili_config
    date_format = '%m%d-%H%M%S'
    config = bili_config.Config()
    sender = Sender(config.cookies)
    #for s in lst: print s
    print "danmakus count:", len(lst)
    while 1:
        tm = time.localtime(time.time() + 18000)
        mins = int(time.strftime('%M', tm))
        hours = int(time.strftime('%H', tm))
        if 11 <= hours <= 23:
            if 50 <= mins < 60:
                content = random.choice(lst)
                sender.sendDanmaku(545342, content)
                print time.strftime(date_format, tm), content
                time.sleep(1)
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
