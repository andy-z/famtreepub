# -*- coding: utf-8 -*-
'''
Created on Sep 8, 2012

@author: salnikov
'''

import os
import Image
import hashlib
import logging
from cStringIO import StringIO

from odf.opendocument import OpenDocumentText
from odf import text, style, draw, table

from plotter import Plotter
from size import Size

_log = logging.getLogger(__name__)

def _unknownName(name):
    return name is None or name.startswith(('?', '.'))

def _nameCmp(lhs, rhs):
    if _unknownName(lhs):
        if _unknownName(rhs): return 0
        return 1
    else:
        if _unknownName(rhs): return -1
        return cmp(lhs, rhs)

def _personCmp(lhs, rhs):
    lhs, rhs = lhs.name, rhs.name
    d = _nameCmp(lhs.last, rhs.last)
    if d != 0: return d
    d = _nameCmp(lhs.first, rhs.first)
    if d != 0: return d
    return _nameCmp(lhs.middle, rhs.middle)


def _tr(str, person = None):
    if str == 'Unknown': return u'Неизвестно'
    if str == 'Born' and person.sex == 'M': return u'Родился'
    if str == 'Born' and person.sex == 'F': return u'Родилась'
    if str == 'Died' and person.sex == 'M': return u'Умер'
    if str == 'Died' and person.sex == 'F': return u'Умерла'
    if str == 'Mother': return u'Мать'
    if str == 'Father': return u'Отец'
    if str == 'Spouse' and person.sex == 'M': return u'Супруга'
    if str == 'Spouse' and person.sex == 'F': return u'Супруг'
    if str == 'kid' and person.sex == 'M': return u'сын'
    if str == 'kid' and person.sex == 'F': return u'дочь'
    if str == 'kids': return u'дети'
    if str == 'Kids': return u'Дети'
    if str == 'Marriage': return u'Свадьба'
    if str == 'Spouses and children': return u'Супруги и дети'
    if str == 'Events and dates': return u'События и даты'
    if str == 'Ancestor tree': return u'Предки'
    if str == 'Comments': return u'Комментарии'
    if str == 'Person List': return u'Персоналии'
    if str == 'Statistics': return u'Статистика'
    if str == 'Total Statistics': return u'Общая статистика'
    if str == 'Name Statistics': return u'Статистика имен'
    if str == 'Female Name Frequency': return u'Частота женских имен'
    if str == 'Male Name Frequency': return u'Частота мужских имен'
    return str

class OdtWriter(object):
    '''
    Format tree as ODF text document
    '''


    def __init__(self, fileFactory, filename, page_width, page_height, margin, firstpage=1):
        self.fileFactory = fileFactory
        self.filename = filename
        self.page_width = Size(page_width)
        self.page_height = Size(page_height)
        self.margin = Size(margin)
        self.firstpage = firstpage
                
    def write(self, model):
        
        doc = OpenDocumentText()

        # set paper dimensions
        pageLayout = style.PageLayout(name=u"pl1")
        doc.automaticstyles.addElement(pageLayout)
        plProp = style.PageLayoutProperties(pageheight=str(self.page_height), pagewidth=str(self.page_width), margin=str(self.margin))
        pageLayout.addElement(plProp)
        
        footer = style.Footer()
        foostyle = style.Style(name="Footer", family="paragraph")
        foostyle.addElement(style.ParagraphProperties(textalign='center'))
        doc.automaticstyles.addElement(foostyle)
        p = text.P(stylename = foostyle)
        p.addElement(text.PageNumber(selectpage="current", pageadjust=str(self.firstpage-1)))
        footer.addElement(p)
        
        masterpage = style.MasterPage(name=u"Standard", pagelayoutname=pageLayout)
        masterpage.addElement(footer)
        doc.masterstyles.addElement(masterpage)
        
        # heading styles
        h1topmrg = self.page_height * 0.5 - self.margin - Size('22pt')
        h1style = style.Style(name="Heading 1", family="paragraph")
        h1style.addElement(style.ParagraphProperties(textalign='center', breakbefore='page', margintop=str(h1topmrg)))
        h1style.addElement(style.TextProperties(fontsize='22pt', fontweight='bold'))
        doc.styles.addElement(h1style)

        brstyle = style.Style(name="Break", family="paragraph")
        brstyle.addElement(style.ParagraphProperties(textalign='center', breakafter='page'))
        doc.automaticstyles.addElement(brstyle)

        h2namestyle = style.Style(name="Heading 2 (Name)", family="paragraph")
        h2namestyle.addElement(style.ParagraphProperties(textalign='center', breakbefore='page', marginbottom="14pt"))
        h2namestyle.addElement(style.TextProperties(fontsize='14pt', fontweight='bold'))
        doc.styles.addElement(h2namestyle)

        h2style = style.Style(name="Heading 2", family="paragraph")
        h2style.addElement(style.ParagraphProperties(textalign='center', margintop="12pt"))
        h2style.addElement(style.TextProperties(fontsize='14pt', fontweight='bold'))
        doc.styles.addElement(h2style)

        h3style = style.Style(name="Heading 3", family="paragraph")
        #h3style.addElement(style.ParagraphProperties(textalign='center', margintop="12pt", borderbottom="0.06pt solid #000000"))
        h3style.addElement(style.ParagraphProperties(textalign='center', margintop="12pt"))
        h3style.addElement(style.TextProperties(fontweight='bold'))
        doc.styles.addElement(h3style)
        
        # style for image
        imgstyle = style.Style(name="ImgStyle", family="graphic", parentstylename="Graphics")
        imgstyle.addElement(style.GraphicProperties(verticalpos='top', verticalrel='paragraph-content',
                                                    horizontalpos='right', horizontalrel='page-content',
                                                    marginleft="0.1in", marginbottom="0.1in"))
        doc.automaticstyles.addElement(imgstyle)

        # style for tree table
        treetablestyle = style.Style(name="TreeTableStyle", family="table")
        treetablestyle.addElement(style.TableProperties(align='center'))
        doc.automaticstyles.addElement(treetablestyle)

        treecellstyle = style.Style(name="TreeTableCellStyle", family="table-cell")
        treecellstyle.addElement(style.TableCellProperties(verticalalign='middle', padding='0.03in'))
        doc.automaticstyles.addElement(treecellstyle)
        
        treeparastyle = style.Style(name="TreeTableParaStyle", family="paragraph")
        treeparastyle.addElement(style.ParagraphProperties(textalign='center', verticalalign='middle', 
                                                           border="0.06pt solid #000000", padding='0.01in'))
        treeparastyle.addElement(style.TextProperties(fontsize='10pt'))
        doc.automaticstyles.addElement(treeparastyle)
        
        
        # generate some stats
        hdr = _tr("Person List", None)
        doc.text.addElement(text.H(text=hdr, outlinelevel=1, stylename=h1style))
        doc.text.addElement(text.P(text='', stylename=brstyle))

        # sort people according to last name, first name, middle name, missing
        # names or names starting with '?' sort last
        people = model.people[:]
        people.sort(_personCmp)
        
        for person in people:
            
            _log.debug('Processing %s', person)            
            
            # page title
            doc.text.addElement(text.H(text=person.name.full, outlinelevel=2, stylename=h2namestyle))


            p = text.P()
            imgframe = self._getMainImage(model, person, doc)
            if imgframe: 
                imgframe.setAttribute('stylename', imgstyle)
                imgframe.setAttribute('anchortype', 'paragraph')
                p.addElement(imgframe)
            
            # birth date and place
            p.addText(_tr('Born', person) + ": ")
            if person.birth.date: 
                p.addText(str(person.birth.date))
            else:
                p.addText(_tr('Unknown', person))
            if person.birth.place: 
                p.addText(", " + person.birth.place)
            doc.text.addElement(p)

            # Parents
            if person.mother:
                p = text.P(text = _tr('Mother', person) + ": " + person.mother.name.full)
                doc.text.addElement(p)
            if person.father:
                p = text.P(text = _tr('Father', person) + ": " + person.father.name.full)
                doc.text.addElement(p)


            # spouses and children
            own_kids = []
            if person.spouses:
                hdr = _tr("Spouses and children", person)
                doc.text.addElement(text.H(text=hdr, outlinelevel=3, stylename=h3style))
            for spouse in person.spouses:
                _log.debug('spouse = %s; children ids = %s; children = %s', spouse, spouse._children, spouse.children)
                if spouse.person:
                    p = text.P(text = _tr('Spouse', person) + ": " + spouse.person.name.full)
                    kids = [c.name.first for c in spouse.children]
                    if kids: p.addText("; " + _tr('kids', '') + ': ' + ', '.join(kids))
                    doc.text.addElement(p)
                else:
                    own_kids += [c.name.first for c in spouse.children]
            if own_kids: 
                p = text.P(text = _tr('Kids', '') + ': ' + ', '.join(own_kids))
                doc.text.addElement(p)

            # All relevant dates
            events = []
            for spouse in person.spouses:
                
                # marriage date if known
                if spouse.marriage.date: 
                    descr = _tr('Marriage', person) 
                    if spouse.person:
                        descr += ", " + _tr('Spouse', person) + ": "  + spouse.person.name.maiden_full
                    events.append((spouse.marriage.date, descr))

                # kids birth dates
                for kid in spouse.children:
                    if kid.birth.date:
                        descr = _tr('Born', kid) + " " + _tr('kid', kid) + " " + kid.name.first
                        events.append((kid.birth.date, descr))

            if person.death.date:
                descr = _tr('Died', person)
                if person.death.place: p.addText(", " + person.death.place)
                events.append((person.death.date, descr))
                    
            events.sort()
            if events:
                hdr = _tr("Events and dates", person)
                doc.text.addElement(text.H(text=hdr, outlinelevel=3, stylename=h3style))
            for evt in events:
                p = text.P(text = str(evt[0]) + ": " + evt[1])
                doc.text.addElement(p)
            

            # Comments are published as set of paragraphs
            if person.comment:
                hdr = _tr("Comments", person)
                doc.text.addElement(text.H(text=hdr, outlinelevel=3, stylename=h3style))

                doc.text.addElement(text.P())
                for para in person.comment.split('\n'):
                    doc.text.addElement(text.P(text = para))
                    
            # plot ancestors tree
            tree_elem = self._getParentTree(person, doc, treetablestyle, treecellstyle, treeparastyle)
            if tree_elem:
                hdr = _tr("Ancestor tree", person)
                doc.text.addElement(text.H(text=hdr, outlinelevel=3, stylename=h3style))
                p = text.P()
                p.addElement(tree_elem)
                doc.text.addElement(p)


        # generate some stats
        hdr = _tr("Statistics", None)
        doc.text.addElement(text.H(text=hdr, outlinelevel=1, stylename=h1style))
        doc.text.addElement(text.P(text='', stylename=brstyle))

        hdr = _tr("Total Statistics", None)
        doc.text.addElement(text.H(text=hdr, outlinelevel=2, stylename=h2style))
        nmales = len([person for person in people if person.sex == 'M'])
        nfemales = len([person for person in people if person.sex == 'F'])
        p = text.P(text = '%s: %d' % (_tr('Всего персон'), len(people)))
        doc.text.addElement(p)
        p = text.P(text = '%s: %d' % (_tr('Женского пола'), nfemales))
        doc.text.addElement(p)
        p = text.P(text = '%s: %d' % (_tr('Мужского пола'), nmales))
        doc.text.addElement(p)


        hdr = _tr("Name Statistics", None)
        doc.text.addElement(text.H(text=hdr, outlinelevel=2, stylename=h2style))

        hdr = _tr("Female Name Frequency", None)
        doc.text.addElement(text.H(text=hdr, outlinelevel=3, stylename=h3style))
        elem = self._namestat(person for person in people if person.sex == 'F')
        doc.text.addElement(elem)
        
        hdr = _tr("Male Name Frequency", None)
        doc.text.addElement(text.H(text=hdr, outlinelevel=3, stylename=h3style))
        elem = self._namestat(person for person in people if person.sex == 'M')
        doc.text.addElement(elem)
        

        # save the result
        doc.save(self.filename)
        

    def _getMainImage(self, model, person, doc):
        '''
        Returns image for a person, return value is draw.Frame or None
        '''
        photos = model.getPhotos(person)
        if photos: photos = [photo for photo in photos if photo.default]
        if photos: 
            
            # find image file, get its data
            imgfile = self.fileFactory.openImage(photos[0].file)
            imgdata = imgfile.read()
            imgfile = StringIO(imgdata)
            img = Image.open(imgfile)
            filename = "Pictures/" + hashlib.sha1(imgdata).hexdigest() + '.' +img.format

            # calculate size of the frame
            h = 2.
            w = h / img.size[1] * img.size[0]
            if w > 2.5:
                w = 2.5
                h = w / img.size[0] * img.size[1]
            frame = draw.Frame(width="%.3fin"%w, height="%.3fin"%h)
            imgref = doc.addPicture(filename, "image/"+img.format, imgdata)
            frame.addElement(draw.Image(href=imgref))
            return frame
        
        
    def _getParentTree(self, person, doc, tablestyle, treecellstyle, treeparastyle):
        '''
        Returns element containg parent tree or None
        '''

        width = self.page_width - 2*self.margin

        plotter = Plotter()
        img = plotter.parent_tree(person, width=width, gen_dist="12pt", font_size="9pt")
        if img is None: return

        # if not None then 4-tuple
        imgdata, imgtype, width, height = img
        
        # store image
        filename = "Pictures/" + hashlib.sha1(imgdata).hexdigest() + '.svg'
        imgref = doc.addPicture(filename, imgtype, imgdata)
        
        frame = draw.Frame(width=str(width), height=str(height))
        frame.addElement(draw.Image(href=imgref))
        
        return frame
        
    def _namestat(self, people):
        
        def _gencouples(namefreq):
            halflen = (len(namefreq)+1)/2
            for i in range(halflen):
                c1, n1 = namefreq[2*i]
                c2, n2 = None, None
                if 2*i+1 < len(namefreq):
                    c2, n2 = namefreq[2*i+1]
                yield c1, n1, c2, n2
        
        namefreq = {}
        for person in people:
            counter = namefreq.setdefault(person.name.first, 0)
            namefreq[person.name.first] += 1
        namefreq = [(val, key) for key, val in namefreq.items()]
        # sort descending in frequency, accending in name
        namefreq.sort(key = lambda x: (-x[0], x[1]))
        total = float(sum(count for count, name in namefreq))

        tbl = table.Table()
        tbl.addElement(table.TableColumn())
        tbl.addElement(table.TableColumn())
        tbl.addElement(table.TableColumn())
        tbl.addElement(table.TableColumn())

        for count1, name1, count2, name2 in _gencouples(namefreq):

            row = table.TableRow()
            
            cell = table.TableCell()
            cell.addElement(text.P(text = name1))
            row.addElement(cell)
            
            cell = table.TableCell()
            cell.addElement(text.P(text = '%d (%.1f%%)' % (count1, count1/total*100)))
            row.addElement(cell)

            if count2 is not None:

                cell = table.TableCell()
                cell.addElement(text.P(text = name2))
                row.addElement(cell)
                
                cell = table.TableCell()
                cell.addElement(text.P(text = '%d (%.1f%%)' % (count2, count2/total*100)))
                row.addElement(cell)

            tbl.addElement(row)

        return tbl
