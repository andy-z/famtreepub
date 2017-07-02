'''
Created on Nov 24, 2012

@author: salnikov
'''

import logging

from .drevo_reader import DrevoReader
from .input import FileLocator

_log = logging.getLogger(__name__)

def validate(arg):
    '''
    Throws an exception if files cannot be validated.

    Acceptable is either an XML file that can be parsed by DrevoReader class
    or a zip file containing such XML file.
    '''

    floc = FileLocator(arg)
    if floc is None:
        raise ValueError('File %s does not exist' % arg)

    reader = DrevoReader(floc)
    if not reader.people:
        raise ValueError('File has no persons')
