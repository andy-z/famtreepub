'''
Created on Sep 6, 2012

@author: salnikov
'''

import logging

_log = logging.getLogger(__name__)


def resize(size, max_size):
    '''
    Resize a box (size is a tuple (width, height)) so that it fits into 
    max_size and keeps aspect ratio. If size is smaller than max_size then 
    return original size.
    '''
    
    w, h = size  
    if w <= max_size[0] and h <= max_size[1]: return size

    h = max_size[1]
    w = (h*size[0])/size[1]
    if w > max_size[0]:
        w = max_size[0]
        h = (w*size[1])/size[0]
    return w, h

