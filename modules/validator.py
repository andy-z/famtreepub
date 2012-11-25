'''
Created on Nov 24, 2012

@author: salnikov
'''

import logging

from drevo_reader import DrevoReader 
from input import FileLocator

logger = logging.getLogger("web2py.app.famtreepub")

def validate(arg):
    '''
    Returns true if given file is acceptable input, false otherwise. Argument
    can be either file name of file-like object.
    
    Acceptable is either an XML file that can be parsed by DrevoReader class
    or a zip file containing such XML file.
    '''
    
    floc = FileLocator(arg)
    if floc is None:
        logger.debug('File %s does not exist', arg)
        return False
    
    try:
        reader = DrevoReader(floc)
    except Exception, ex:
        logger.debug('Error parsing input file: %s', str(ex))
        return False
    return True
