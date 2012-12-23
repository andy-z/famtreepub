'''
Created on Sep 6, 2012

@author: salnikov
'''

import logging
import traceback

import xml.etree.ElementTree as ET
from person import Person, Doc
import date

_log = logging.getLogger(__name__)


class _DateParser(object):
    '''Class defines callable instances to parse dates'''
    def __init__(self, fmt):
        self.fmt = fmt
        
    def __call__(self, datestr):
        return date.parse(datestr, self.fmt)

class DrevoReader(object):
    '''
    Class which knows how to read an parse XML tree
    '''


    def __init__(self, fileFactory):
        '''
        Constructor takes the name of the input XML file.
        '''
        
        # open XML file
        xml = fileFactory.openXML()
        
        # read and parse whole tree
        try:
            tree = ET.parse(xml)
        except:
            _log.error("%s", traceback.format_exc())
            raise ValueError("Not well-formed XML file")
        root = tree.getroot()
        
        if root.tag != 'agelongtree':
            raise ValueError("Unexpected XML tag")
        if not list(root):
            raise ValueError("File is empty")

        # first step is to guess date formats, collect all dates and 
        # feed them to the date parser, it will raise exception if 
        # cannot reliably determine date format 
        datefmt = date.guessFormat(self._getDates(root))
        dateParser = _DateParser(datefmt)

        self.docs = []
        self.people = []
        
        for el in root.findall('Pers/r'):
            
            # collect documents in separate list
            for docel in el.findall('doc'):
                self.docs.append(Doc(docel, dateParser))
            
            # make person
            person = Person(el, dateParser)
            self.people.append(person)
            _log.debug('Adding person %s', person)
            
    def getPhotos(self, person):
        
        # find docs with this person id and docclass="photo"
        return [d for d in self.docs if (person in d.people) and (d.docclass == 'photo')]

    @staticmethod
    def _getDates(root):
        '''Generator for all strings containing dates'''
        for elem in root.iter():
            if elem.tag in ('bfdate', 'dfdate', 'di', 'de'):
                d = elem.text.strip()
                if d: yield d
