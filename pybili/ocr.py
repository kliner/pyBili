import sys
import json
import numpy as np
import os.path
from PIL import Image
import training

DEBUG = 0

def recognize(path):
    # read image & convert to grey scale
    pic = Image.open(path).convert('L')
    
    # filter to binary np array, 0 means white, 1 means black
    pix = np.array(pic)
    pix /= 128
    pix = 1 - pix

    if DEBUG: consolePrint(pix)
    
    # load trained data
    global trained_data
    p = 'trained_data.json'
    if os.path.exists(p): 
        with open(p, 'r') as f:
            trained_data = json.load(f)
    else: trained_data = training.train()
    
    # do recognize
    s = ''
    for area in _selectImageArea(pix): s += _recognize(pix, area)
    if DEBUG: print s
    return eval(s)

def consolePrint(pix):
    h, w = pix.shape
    pix2 = [[0] * w for _ in xrange(h)]
    for i in xrange(h):
        for j in xrange(w):
            if pix[i][j]: pix2[i][j] = '*'
            else: pix2[i][j] = ' '
    for i in xrange(h):
        print ''.join(pix2[i])

def _selectImageArea(pix):
    h, w = pix.shape
    image_lines = [i for i in xrange(w) if any([pix[j][i] for j in xrange(h)])]
    
    i = 0
    image_area = []
    while i < len(image_lines):
        j = i+1
        while j < len(image_lines) and image_lines[j] == image_lines[j-1]+1: j+=1
        image_area += [image_lines[i], image_lines[j-1]]
        i = j
    image_area = zip(image_area[::2], image_area[1::2])
    #print image_area
    return image_area

def _match(pix):
    global trained_data
    arr = pix.ravel()
    key = ''.join(map(str, arr.tolist()))
    #print key
    for k, v in trained_data:
        sim = sum([1 for i in xrange(len(v)) if v[i] == key[i]])
        if sim > 620: return k
    return '?'

def _recognize(pix, area):
    a, b = area
    w = b-a+1
    d = { 7:'1', 9:'-', 16:_recognize_16(pix, area), 17:_recognize_17(pix, area) }
    return d[w]

def _recognize_16(pix, area):
    if area[1] - area[0] + 1 == 16:
        return _match(pix[:,area[0]:area[1]+1])

def _recognize_17(pix, area):
    if area[1] - area[0] + 1 == 17:
        a, b = area
        if pix[6][a+8]: return '4'
        else: return '+'

if __name__ == '__main__':
    f = sys.argv[1]
    #f = 'img.jpg'
    print recognize(f)
