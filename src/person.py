'''
Created on Sep 6, 2012

@author: salnikov
'''

import logging

_log = logging.getLogger(__name__)

def _tagtext(elem, tag):
    child = elem.find(tag)
    if child is not None: return child.text.strip()

def _tagid(elem, tag):
    child = elem.find(tag)
    if child is not None: return child.get('id')

# global mapping for person id -> person
_id2pers = {}


class Name(object):
    
    def __init__(self, elem):
        self.full = _tagtext(elem, 'fullname')
        self.last = _tagtext(elem, 'sn')
        self.first = _tagtext(elem, 'fn')
        self.middle = _tagtext(elem, 'mn')
        self.maiden = _tagtext(elem, 'msn')
        self.maiden_full = " ".join([(self.maiden or self.last) or "", self.first or "", self.middle or ""])
        
    def __str__(self):
        return self.full

class Doc(object):

    def __init__(self, elem):
        self.id = elem.get('id')
        self.docclass = elem.get('class')
        self.default = (elem.get('default') == 'T')
        self.file = _tagtext(elem, 'file')
        self.date = _tagtext(elem, 'date')
        self.comment = _tagtext(elem, 'comment')
        self._people = [el.get('id') for el in elem.findall('persons/p')]

    @property
    def people(self):
        return map(_id2pers.get, self._people)
    


class Date(object):
    
    def __init__(self, datestr):
        self.date = None
        if datestr:
            dd = datestr.split('.')
            if len(dd) == 1:
                self.date = (int(dd[0]), )
            elif len(dd) == 2:
                self.date = (int(dd[1]), int(dd[0]))
            elif len(dd) == 3:
                self.date = (int(dd[2]), int(dd[1]), int(dd[0]))

    def __cmp__(self, other):
        return cmp(self.date, other.date)

    def __nonzero__(self):
        return self.date is not None

    def __str__(self):
        res = ""
        if len(self.date) > 0: res = "%04d" % self.date[0]
        if len(self.date) > 1: res = "%02d.%s" % (self.date[1], res)
        if len(self.date) > 2: res = "%02d.%s" % (self.date[2], res)
        return res

class Event(object):

    def __init__(self, date, place):
        self.date = Date(date)
        self.place = place
        
    def __cmp__(self, other):
        return cmp((self.date, self.place), (other.date, other.place))


class Spouse(object):
    
    def __init__(self, elem):
        self.id = elem.get('id')
        self.marriage = Event(_tagtext(elem, 'marriage/date'), _tagtext(elem, "marriage/pl_full"))
        self._children = [el.get('id') for el in elem.findall('child')]
        self.divorced = elem.find('divorce') is not None

    @property
    def person(self):
        return _id2pers.get(self.id)
    
    @property
    def children(self):
        return map(_id2pers.get, self._children)
    
    def __str__(self):
        return 'Spouse(id = %s, person = %s)' % (self.id, self.person)
    

class Person(object):
    '''
    Person description
    '''
    def __init__(self, elem):
        '''
        Constructor
        '''
        
        self.id = elem.get('id')
        self.name = Name(elem)
        self.sex = _tagtext(elem, 'sex')
        self.birth = Event(_tagtext(elem, 'bfdate'), _tagtext(elem, 'bplace'))
        self.death = Event(_tagtext(elem, 'dfdate'), _tagtext(elem, 'dplace'))
        self._mother = _tagid(elem, 'mother')
        self._father = _tagid(elem, 'father')
        self.occupation = _tagtext(elem, 'occu')
        self.comment = _tagtext(elem, 'comment')
        self.spouses = [Spouse(el) for el in elem.findall('spouse')]

        # add this person to global id map
        global _id2pers
        _id2pers[self.id] = self

    @property
    def mother(self):
        return _id2pers.get(self._mother)
    
    @property
    def father(self):
        return _id2pers.get(self._father)
    
    def __str__(self):
        return "Person(id = %s, name = %s)" % (self.id, self.name)