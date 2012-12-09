# -*- coding: utf-8 -*-
'''
Created on Nov 25, 2012

@author: salnikov
'''
from size import Size





class Config(dict):
    '''
    This is a regular dictionary class with few specialized methods
    '''
    
    def __init__(self):
        
        # set defaults
        self['page_width'] = 6.
        self['page_height'] = 9.
        self['html_page_width'] = 800
        
        self['margin_left'] = 0.5
        self['margin_right'] = 0.5
        self['margin_top'] = 0.5
        self['margin_bottom'] = 0.25
        
        self['image_width'] = 2.5
        self['image_height'] = 2.5
        
        self['first_page'] = 1

        self['date_format'] = 'DMY.'

    def getSize(self, name, default=None):
        
        s = self.get(name, default)
        if s is None: return None
        return Size(s)
    