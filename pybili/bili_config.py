#!/usr/bin/python
#coding=utf-8
import os.path 
import sys
import ConfigParser

class Config(object):

    data = {}
    cookies = {}

    def __init__(self, path = os.path.expanduser("~") + '/.pybili.conf'):
        if not os.path.isfile(path):
            print path
            print 'warning! please set the config file!'
            return 
        self.path = path
        self.read(path)

    def get(self, dataid, key, value = None):
        d = self.data[str(dataid)]
        v = d.get(key, None)
        if not v: return value
        return v

    def _get(self, cf, sec, opt):
        if cf.has_option(sec, opt): return cf.get(sec, opt)
        else: return

    def _getboolean(self, cf, sec, opt):
        if cf.has_option(sec, opt): return cf.getboolean(sec, opt)
        else: return
    
    def read(self, path):
        cf = ConfigParser.ConfigParser(allow_no_value=1)
        cf.read(path)
        
        for section in cf.sections():
            if section == 'cookies':
                s = cf.get(section, 'cookies')
                if 'cookie:' == s[:7]: s = s[7:] # do strip 
                try:
                    for line in s.split(';'):
                        name, value = line.strip().split('=', 1)
                        self.cookies[name] = value
                except Exception, e:
                    print 'warning! please set correct cookies into \'cookie.txt\'', e
            else:
                try:
                    d = {}
                    d['GiftResponse'] = self._getboolean(cf, section, 'GiftResponse')
                    d['ShowTime'] = self._getboolean(cf, section, 'ShowTime')
                    d['SmallTVHint'] = self._getboolean(cf, section, 'SmallTVHint')
                    d['MacNotification'] = self._getboolean(cf, section, 'MacNotification')
                    d['MacTTS'] = self._getboolean(cf, section, 'MacTTS')
                    d['DanmakuColor'] = self._get(cf, section, 'DanmakuColor')
                    d['AwardSmallTV'] = self._getboolean(cf, section, 'AwardSmallTV')
                    d['RecordDanmaku'] = self._getboolean(cf, section, 'RecordDanmaku')
                    self.data[section] = d
                except Exception, e:
                    print 'exception when read config, please check the format of config file ', e

    def p(self):
        print 'current configs:'
        for k in self.data.keys():
            print '----------'
            print k
            for kk in self.data[k].keys():
                print kk, self.data[k][kk]

    def inputBoolean(self, msg):
        a = raw_input(msg)
        return a in 'Yy1'

    def setup(self):
        cf = ConfigParser.RawConfigParser()
        cf.read(self.path)

        cookies = raw_input('Please input the cookies: [press enter to skip]')
        if cookies:
            if not cf.has_section('cookies'): cf.add_section('cookies')
            cf.set('cookies', 'cookies', cookies)

        roomid = raw_input('Please input the roomid to setup: [press enter to skip]')
        if roomid:
            if not cf.has_section(roomid): cf.add_section(roomid)

            b = self.inputBoolean('Auto-response the gift? [y/n]')
            cf.set(roomid, 'GiftResponse', b)
            b = self.inputBoolean('Show the time of the danmaku in console? [y/n]')
            cf.set(roomid, 'ShowTime', b)
            b = self.inputBoolean('Auto-response the smallTV? [y/n]')
            cf.set(roomid, 'SmallTVHint', b)
            b = self.inputBoolean('Auto-enter the lottery of the smallTV? [y/n]')
            cf.set(roomid, 'AwardSmallTV', b)
            b = self.inputBoolean('Show notification in the Mac OS? [y/n]')
            cf.set(roomid, 'MacNotification', b)
            b = self.inputBoolean('Speak the danmaku out in the Mac OS? [y/n]')
            cf.set(roomid, 'MacTTS', b)
            b = self.inputBoolean('Record the danmaku into the MongoDB? [y/n]')
            cf.set(roomid, 'RecordDanmaku', b)
            cf.set(roomid, 'DanmakuColor', raw_input('Danmaku color? [white/red/orange/yellow/green/cyan/blue/purple]'))
        cf.write(open(self.path, 'w'))

def main():
    config = Config()
    config.p()
    config.setup()

if __name__ == '__main__':
    main()
