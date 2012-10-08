'''
Created on Sep 6, 2012

@author: salnikov
'''

import logging

import xml.etree.ElementTree as ET
from person import Person, Name, Doc

_log = logging.getLogger(__name__)

class DrevoReader(object):
    '''
    Class which kows how to read an parse XML tree
    '''


    def __init__(self, fileFactory):
        '''
        Constructor takes the name of the input XML file.
        '''
        
        # open XML file
        xml = fileFactory.openXML()
        
        # read and parse whole tree
        tree = ET.parse(xml)
        root = tree.getroot()

        self.docs = []
        self.people = []
        
        for el in root.findall('Pers/r'):
            
            # collect documents in separate list
            self.docs += map(Doc, el.findall('doc'))
            
            # make person
            person = Person(el)
            self.people.append(person)
            _log.debug('Adding person %s', person)
            
    def getPhotos(self, person):
        
        # find docs with this person id and docclass="photo"
        return [d for d in self.docs if (person in d.people) and (d.docclass == 'photo')]
