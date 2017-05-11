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
                    d['AwardNeedYou'] = self._getboolean(cf, section, 'AwardNeedYou')
                    self.data[section] = d
                except Exception, e:
                    print 'exception when read config, please check the format of config file ', e

if __name__ == '__main__':
    config = Config()
    print config.data["90012"]
    print config.data["30040"]
    print config.get(90012, "MacTTS", False)

