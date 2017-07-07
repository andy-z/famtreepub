'''
Created on Sep 6, 2012

@author: salnikov
'''

from __future__ import absolute_import, division, print_function

import logging

_log = logging.getLogger(__name__)

def _tagtext(elem, tag):
    child = elem.find(tag)
    if child is not None:
        return child.text.strip()

def _tagid(elem, tag):
    child = elem.find(tag)
    if child is not None:
        return child.get('id')

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

    def __init__(self, elem, dateParser):
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

class Event(object):

    def __init__(self, date, place):
        self.date = date
        self.place = place

    def __cmp__(self, other):
        return cmp((self.date, self.place), (other.date, other.place))


class Spouse(object):

    def __init__(self, elem, dateParser):
        self.id = elem.get('id')
        self.marriage = Event(dateParser(_tagtext(elem, 'marriage/date')), _tagtext(elem, "marriage/pl_full"))
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
    def __init__(self, elem, dateParser):
        '''
        Constructor
        '''

        self.id = elem.get('id')
        self.name = Name(elem)
        self.sex = _tagtext(elem, 'sex')
        self.birth = Event(dateParser(_tagtext(elem, 'bfdate')), _tagtext(elem, 'bplace'))
        self.death = Event(dateParser(_tagtext(elem, 'dfdate')), _tagtext(elem, 'dplace'))
        self._mother = _tagid(elem, 'mother')
        self._father = _tagid(elem, 'father')
        self.occupation = _tagtext(elem, 'occu')
        self.comment = _tagtext(elem, 'comment')
        self.spouses = [Spouse(el, dateParser) for el in elem.findall('spouse')]

        # add this person to global id map
        _id2pers[self.id] = self

    @property
    def mother(self):
        return _id2pers.get(self._mother)

    @property
    def father(self):
        return _id2pers.get(self._father)

    def __str__(self):
        return "Person(id = %s, name = %s)" % (self.id, self.name)
