import pybili.bili_config
import requests
import time

CAPTCHA_URL = 'http://api.live.bilibili.com/freeSilver/getCaptcha?ts=%i'

def load(path = 'img.jpg'):
    config = pybili.bili_config.Config()
    t = int(time.time()*1000)
    r = requests.get(CAPTCHA_URL % t, cookies=config.cookies)
    with open(path, 'w') as f:
        for chunk in r: f.write(chunk)
    return 'ok'

if __name__=='__main__':
    print load()
