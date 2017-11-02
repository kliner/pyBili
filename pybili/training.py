import json
import numpy as np
from PIL import Image

def train():
    h, w = 40, 16
    nums = '02356789'
    data = []
    for f in nums:
        pic = Image.open('training_data/%s.png' % f).convert('L')
        pix = np.array(pic)
        pix = pix / 128
        pix = 1 - pix
        arr = pix.ravel()
        key = ''.join(map(str, arr.tolist()))
        data += [(f, key)]
    with open('trained_data.json', 'w') as outfile:
        json.dump(data, outfile)
    return data
    
if __name__ == '__main__':
    print train()
