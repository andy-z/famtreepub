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
    

def _parseOne(str):
    i = str.find('(')
    if i < 0:
        d = int(str)
        return d, d
    else:
        if str.endswith(')'):
            return int(str[:i]), int(str[i+1:-1])
    return None, None

class Date(object):
    
    def __init__(self, datestr):
        self.date = None
        if datestr:
            dd = datestr.split('.')
            if len(dd) == 1:
                # year only
                years = _parseOne(dd[0])
                self.date = (years[0],)
                self.old_date = (years[1],)
            elif len(dd) == 2:
                # year and month
                years = _parseOne(dd[1])
                months = _parseOne(dd[0])
                self.date = (years[0], months[0])
                self.old_date = (years[1], months[1])
            elif len(dd) == 3:
                # year, month, day
                years = _parseOne(dd[2])
                months = _parseOne(dd[1])
                days = _parseOne(dd[0])
                self.date = (years[0], months[0], days[0])
                self.old_date = (years[1], months[1], days[1])

    def __cmp__(self, other):
        return cmp(self.date, other.date)

    def __nonzero__(self):
        return self.date is not None

    def __str__(self):
        def fmt(date):
            res = ""
            if len(date) > 0: res = "%04d" % date[0]
            if len(date) > 1: res = "%02d.%s" % (date[1], res)
            if len(date) > 2: res = "%02d.%s" % (date[2], res)
            return res
        
        res = fmt(self.date)
        if self.old_date != self.date: 
            res += " ({0} JC)".format(fmt(self.old_date))
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