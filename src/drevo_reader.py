'''
Created on Sep 6, 2012

@author: salnikov
'''

import xml.etree.ElementTree as ET
from person import Person, Name, Doc



class DrevoReader(object):
    '''
    Class which kows how to read an parse XML tree
    '''


    def __init__(self, filename):
        '''
        Constructor takes the name of the input XML file.
        '''
        
        tree = ET.parse(filename)
        root = tree.getroot()

        self.docs = []
        self.people = []
        
        for el in root.findall('Pers/r'):
            
            # collect documents in separate list
            self.docs += [Doc(d) for d in el.findall('doc')]
            
            # make person
            self.people.append(Person(el))
            
        # map IDs to people
        ids = dict()
        for p in self.people:
            ids[p.id] = p
            
        # replace ID references with real objects
        for p in self.people:
            
            if p.mother: p.mother = ids.get(p.mother)
            if p.father: p.father = ids.get(p.father)
            
            for s in p.spouses:
                s.person = ids.get(s.id)
                s.children = [ids.get(cid) for cid in s.children]

        for d in self.docs:
            d.people = [ids.get(pid) for pid in d.people]

    def getPhotos(self, person):
        
        # find docs with this person id and docclass="photo"
        return [d for d in self.docs if (person in d.people) and (d.docclass == 'photo')]
