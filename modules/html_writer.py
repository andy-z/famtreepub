# -*- coding: utf-8 -*-
'''
Created on Sep 8, 2012

@author: salnikov
'''

from __future__ import absolute_import, division, print_function

import logging
from cStringIO import StringIO
import base64

from PIL import Image
from .plotter import Plotter
from . import gtext
from . import utils

_log = logging.getLogger(__name__)

_ = gtext.gtext

def _unknownName(name):
    return name is None or name.startswith(('?', '.'))

def _nameCmp(lhs, rhs):
    if _unknownName(lhs):
        if _unknownName(rhs):
            return 0
        return 1
    else:
        if _unknownName(rhs):
            return -1
        return cmp(lhs, rhs)

def _personCmp(lhs, rhs):
    lhs, rhs = lhs.name, rhs.name
    d = _nameCmp(lhs.last, rhs.last)
    if d != 0:
        return d
    d = _nameCmp(lhs.first, rhs.first)
    if d != 0:
        return d
    return _nameCmp(lhs.middle, rhs.middle)

def _personRef(person, name=None):
    if name is None:
        name = person.name.full
    return u'<a href="#person.{0}">{1}</a>'.format(person.id, name)


_style = '''
<style type="text/css" media="screen" >
body {
  background-color: #bbbbbb;
}
#contents_div {
  background-color: white;
  padding: 1em;
  width: %(page_width)s;
  margin:auto;
}
a { text-decoration:   none; }
a:visited { color: black; }
a:link { color: black; }
a:hover { color: red; }
h1 {
  background-color: #bbbbbb;
  color: white;
  text-align: center;
  width: 100%%;
  padding: 4px 0px 4px 0px;
  border-radius: 0.2em;
  box-shadow: 4px 4px 4px #555;
  clear:both;
}
h2 {
  background-color: #e0e0e0;
  color: black;
  text-align: center;
  width: 100%%;
  padding: 4px 0px 4px 0px;
  border-radius: 0.2em;
  box-shadow: 4px 4px 4px #555;
  clear:both;
}
h3 {
  text-align: center;
  font-weight: normal;
  font-style: italic;
}
.svglink:hover {
  fill:red;
}
</style>

<style type="text/css" media="print" >
body {
  background-color: white;
}
#contents_div {
  padding: 1em;
  width: 90%%;
  margin:auto;
}
a { text-decoration:   none; }
a:visited { color: black; }
a:link { color: black; }
a:hover { color: red; }
h1 {
  text-align: center;
  width: 100%%;
  padding: 4px 0px 4px 0px;
  page-break-before: always;
  border: solid black 1pt;
  clear:both;
}
h2 {
  text-align: center;
  width: 100%%;
  padding: 4px 0px 4px 0px;
  clear:both;
}
h3 {
  text-align: center;
  font-weight: normal;
  font-style: italic;
}
</style>

<style type="text/css" media="all" >
img.personImage {
  border-radius: 6px;
  box-shadow: 2px 2px 10px #555;
  float: right;
  margin: 0px 0px 10px 10px;
  padding: 6px 6px 6px 6px;
}
table.statTable {
  margin:auto;
  width: 80%%;
}
.centered {
  margin:auto;
  width: -moz-max-content;
  width: max-content;
}
</style>
'''


class HtmlWriter(object):
    '''
    Format tree as HTML document
    '''


    def __init__(self, fileFactory, output, config):

        self.fileFactory = fileFactory
        self.output = output  # output file name or file object

        # parameters
        self.config = config

    def write(self, model):

        toc = []

        doc = ['<!DOCTYPE html>']
        doc += ['<html>', '<head>']
        doc += ['<meta http-equiv="Content-Type" content="text/html; charset=utf-8">\n']
        doc += ['<title>', 'Family Tree', '</title>\n']
        d = dict(page_width=self.config.getSize('page_width') ^ 'px')
        doc += [_style % d]
        doc += ['</head>\n', '<body>\n']
        doc += ['<div id="contents_div"/>\n']

        doc += [u'<h1 id="personList">{0}</h1>\n'.format(_("Person List"))]
        toc += [(1, 'personList', _("Person List"))]

        # sort people according to last name, first name, middle name, missing
        # names or names starting with '?' sort last
        people = model.people[:]
        people.sort(_personCmp)

        for person in people:

            _log.debug('Processing %s', person)

            # page title
            doc += [u'<h2 id="person.{0}">{1}</h2>\n'.format(person.id, person.name.full)]
            toc += [(2, 'person.' + person.id, person.name.full)]

            img = self._getMainImage(model, person)
            if img:
                doc += [img]

            # birth date and place
            doc += ['<p>' + _('Born', person) + ": "]
            if person.birth.date:
                doc += [self._datefmt(person.birth.date)]
            else:
                doc += [_('Unknown', person)]
            if person.birth.place:
                doc += [", " + person.birth.place]
            doc += ['</p>\n']

            # Parents
            if person.mother:
                doc += ['<p>' + _('Mother', person) + ": " + _personRef(person.mother) + '</p>\n']
            if person.father:
                doc += ['<p>' + _('Father', person) + ": " + _personRef(person.father) + '</p>\n']

            # spouses and children
            own_kids = []
            if person.spouses:
                hdr = _("Spouses and children", person)
                doc += ['<h3>' + hdr + '</h3>\n']
            for spouse in person.spouses:
                _log.debug('spouse = %s; children ids = %s; children = %s', spouse, spouse._children, spouse.children)
                if spouse.person:
                    doc += ['<p>' + _('Spouse', person) + ": " + _personRef(spouse.person)]
                    kids = [_personRef(c, c.name.first) for c in spouse.children]
                    if kids:
                        doc += ["; " + _('kids', '') + ': ' + ', '.join(kids)]
                    doc += ['</p>\n']
                else:
                    own_kids += [_personRef(c, c.name.first) for c in spouse.children]
            if own_kids:
                doc += ['<p>' + _('Kids', '') + ': ' + ', '.join(own_kids) + '</p>\n']

            # All relevant dates
            events = []
            for spouse in person.spouses:

                # marriage date if known
                if spouse.marriage.date:
                    descr = _('Marriage', person)
                    if spouse.person:
                        descr += ", " + _('Spouse', person) + ": " + _personRef(spouse.person, spouse.person.name.maiden_full)
                    events.append((spouse.marriage.date, descr))

                # kids birth dates
                for kid in spouse.children:
                    if kid.birth.date:
                        descr = _('Born', kid) + " " + _('kid', kid) + " " + _personRef(kid, kid.name.first)
                        events.append((kid.birth.date, descr))

            if person.death.date:
                descr = _('Died', person)
                if person.death.place:
                    descr += ", " + person.death.place
                events.append((person.death.date, descr))

            events.sort()
            if events:
                doc += ['<h3>' + _("Events and dates") + '</h3>\n']
            for evt in events:
                doc += ['<p>' + self._datefmt(evt[0]) + ": " + evt[1] + '</p>\n']

            # Comments are published as set of paragraphs
            if person.comment:
                doc += ['<h3>' + _("Comments", person) + '</h3>\n']
                for para in person.comment.split('\n'):
                    doc += ['<p>' + para + '</p>\n']

            # plot ancestors tree
            tree_elem = self._getParentTree(person)
            if tree_elem:
                doc += ['<h3>' + _("Ancestor tree", person) + '</h3>\n']
                doc += ['<div class="centered">\n']
                doc += [tree_elem]
                doc += ['</div>\n']
            else:
                doc += ['<svg width="100%" height="1pt"/>\n']


        # generate some stats
        doc += [u'<h1 id="statistics">{0}</h1>\n'.format(_("Statistics"))]
        toc += [(1, 'statistics', _("Statistics"))]

        doc += [u'<h2 id="total_statistics">{0}</h2>\n'.format(_("Total Statistics"))]
        toc += [(2, 'total_statistics', _("Total Statistics"))]

        nmales = len([person for person in people if person.sex == 'M'])
        nfemales = len([person for person in people if person.sex == 'F'])
        doc += ['<p>%s: %d</p>' % (_('Person count'), len(people))]
        doc += ['<p>%s: %d</p>' % (_('Female count'), nfemales)]
        doc += ['<p>%s: %d</p>' % (_('Male count'), nmales)]


        doc += [u'<h2 id="name_statistics">{0}</h2>\n'.format(_("Name Statistics"))]
        toc += [(2, 'name_statistics', _("Name Statistics"))]

        doc += [u'<h3 id="female_name_freq">{0}</h3>\n'.format(_("Female Name Frequency"))]
        doc += self._namestat(person for person in people if person.sex == 'F')

        doc += [u'<h3 id="male_name_freq">{0}</h3>\n'.format(_("Male Name Frequency"))]
        doc += self._namestat(person for person in people if person.sex == 'M')

        # add table of contents
        doc += [u'<h1>{0}</h1>\n'.format(_("Table Of Contents"))]
        lvl = 0
        for toclvl, tocid, text in toc:
            while lvl < toclvl:
                doc += ['<ul>']
                lvl += 1
            while lvl > toclvl:
                doc += ['</ul>']
                lvl -= 1
            doc += [u'<li><a href="#{0}">{1}</a></li>\n'.format(tocid, text)]
        while lvl > 0:
            doc += ['</ul>']
            lvl -= 1

        # closing
        doc += ['</body>']
        doc += ['</html>']

        if hasattr(self.output, 'write'):
            for line in doc:
                self.output.write(unicode(line).encode('utf-8'))
        else:
            out = file(self.output, 'w')
            for line in doc:
                out.write(unicode(line).encode('utf-8'))
            out.close()


    def _getMainImage(self, model, person):
        '''
        Returns image for a person, return value is an <img> element
        '''
        photos = model.getPhotos(person)
        if photos:
            photos = [photo for photo in photos if photo.default]
        if photos:

            # find image file, get its data
            imgfile = self.fileFactory.openImage(photos[0].file)
            if imgfile:
                imgdata = imgfile.read()
                imgfile = StringIO(imgdata)
                img = Image.open(imgfile)

                # resize it if larger than needed
                maxsize = (self.config.getSize('image_width').px, self.config.getSize('image_height').px)
                size = utils.resize(img.size, maxsize)
                if size != img.size:
                    # means size was reduced
                    _log.debug('Resize image to %s', size)
                    img = img.resize(size, Image.ANTIALIAS)
                    imgsize = ""
                else:
                    # means size was not changed and image is smaller than box,
                    # we may want to extend it
                    extend = utils.resize(img.size, maxsize, False)
                    imgsize = ' width="{}" height="{}"'.format(*extend)

                # save to a buffer
                imgfile = StringIO()
                img.save(imgfile, 'JPEG')
                imgfile.seek(0)

                return '<img class="personImage"' + imgsize + ' src="data:image/jpg;base64,' + base64.b64encode(imgfile.read()) + '">'


    def _getParentTree(self, person):
        '''
        Returns element containg parent tree or None
        '''

        width = self.config.getSize('page_width')

        plotter = Plotter(width=width, gen_dist="12pt", font_size="9pt", fullxml=False, refs=True)
        img = plotter.parent_tree(person, 'px')
        if img is None:
            return

        # if not None then 4-tuple
        imgdata, imgtype, width, height = img

        # return unicode string
        return imgdata.decode('utf-8')


    def _namestat(self, people):

        def _gencouples(namefreq):
            halflen = (len(namefreq) + 1) / 2
            for i in range(halflen):
                n1, c1 = namefreq[2 * i]
                n2, c2 = None, None
                if 2 * i + 1 < len(namefreq):
                    n2, c2 = namefreq[2 * i + 1]
                yield n1, c1, n2, c2

        namefreq = {}
        for person in people:
            counter = namefreq.setdefault(person.name.first, 0)
            namefreq[person.name.first] += 1
        namefreq = [(key, val) for key, val in namefreq.items()]
        # sort accending in name
        namefreq.sort()
        total = float(sum(count for name, count in namefreq))


        tbl = ['<table class="statTable">\n']

        for name1, count1, name2, count2 in _gencouples(namefreq):

            tbl += ['<tr>\n']

            tbl += [u'<td width="25%">{0}</td>'.format(name1 or '-')]
            tbl += ['<td width="20%">{0} ({1:.1%})</td>'.format(count1, count1 / total)]

            if count2 is not None:

                tbl += [u'<td width="25%">{0}</td>'.format(name2 or '-')]
                tbl += ['<td width="20%">{0} ({1:.1%})</td>'.format(count2, count2 / total)]

            tbl += ['</tr>\n']

        tbl += ['</table>\n']
        return tbl


    def _datefmt(self, date):

        fmt = self.config['date_format']
        return date.fmt(fmt[:3], fmt[-1])
