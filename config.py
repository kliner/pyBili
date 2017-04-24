#!/usr/bin/python
#coding=utf-8
import json

class Config(object):

    data = {}
    cookies = {}

    def __init__(self, path):
        self.read(path)
    
    def read(self, path):

        with open(r'config.txt','r') as f:
            s = f.read()
            self.data = json.loads(s)
        
        with open(r'cookie.txt','r') as f:
            s = f.read()
            if 'cookie:' == s[:7]: s = s[7:] # do strip 
            try:
                for line in s.split(';'):
                    name, value = line.strip().split('=', 1)
                    self.cookies[name] = value
            except Exception, e:
                print 'warning! please set correct cookies into \'cookie.txt\'', e

if __name__ == '__main__':
    config = Config("config.txt")
    print config.data["90012"]
