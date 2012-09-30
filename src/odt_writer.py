# -*- coding: utf-8 -*-
'''
Created on Sep 8, 2012

@author: salnikov
'''

import os
import Image
import hashlib

from odf.opendocument import OpenDocumentText
from odf import text, style, draw, table

from plotter import Plotter
from size import Size

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


def _tr(str, person):
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


class OdtWriter(object):
    '''
    Format tree as ODF text document
    '''


    def __init__(self, filename, page_width, page_height, margin, imagedir):
        self.filename = filename
        self.page_width = Size(page_width)
        self.page_height = Size(page_height)
        self.margin = Size(margin)
        self.imagedir = imagedir
        
                
    def write(self, model):
        
        doc = OpenDocumentText()

        # set paper dimensions
        pageLayout = style.PageLayout(name=u"pl1")
        doc.automaticstyles.addElement(pageLayout)
        plProp = style.PageLayoutProperties(pageheight=str(self.page_height), pagewidth=str(self.page_width), margin=str(self.margin))
        pageLayout.addElement(plProp)
        
        masterpage = style.MasterPage(name=u"Standard", pagelayoutname=pageLayout)
        doc.masterstyles.addElement(masterpage)
        
        # heading styles 
        h2style = style.Style(name="Heading 2", family="paragraph")
        h2style.addElement(style.ParagraphProperties(textalign='center', breakbefore='page', marginbottom="14pt"))
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
        doc.styles.addElement(imgstyle)

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
        
        
        # sort people according to last name, first name, middle name, missing
        # names or names starting with '?' sort last
        people = model.people[:]
        people.sort(_personCmp)
        
        for person in people:
            
            # page title
            doc.text.addElement(text.H(text=person.name.full, outlinelevel=2, stylename=h2style))


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
                p = text.P()
                p.addText(_tr('Mother', person) + ": " + person.mother.name.full)
                doc.text.addElement(p)
            if person.father:
                p = text.P()
                p.addText(_tr('Father', person) + ": " + person.father.name.full)
                doc.text.addElement(p)


            # spouses and children
            own_kids = []
            if person.spouses:
                hdr = _tr("Spouses and children", person)
                doc.text.addElement(text.H(text=hdr, outlinelevel=3, stylename=h3style))
            for spouse in person.spouses:
                if spouse.person:
                    p = text.P()
                    p.addText(_tr('Spouse', person) + ": " + spouse.person.name.full)
                    kids = [c.name.first for c in spouse.children]
                    if kids: p.addText("; " + _tr('kids', '') + ': ' + ', '.join(kids))
                    doc.text.addElement(p)
                else:
                    own_kids += [c.name.first for c in spouse.children]
            if own_kids: 
                p = text.P()
                p.addText(_tr('Kids', '') + ': ' + ', '.join(own_kids))
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
                p = text.P()
                p.addText(str(evt[0]) + ": " + evt[1])
                doc.text.addElement(p)
            

            # Comments are published as set of paragraphs
            if person.comment:
                doc.text.addElement(text.P())
                for para in person.comment.split('\n'):
                    p = text.P()
                    p.addText(para)
                    doc.text.addElement(p)
                    
                    
            tree_elem = self._getParentTree(person, doc, treetablestyle, treecellstyle, treeparastyle)
            if tree_elem:
                hdr = _tr("Ancestor tree", person)
                doc.text.addElement(text.H(text=hdr, outlinelevel=3, stylename=h3style))
                p = text.P()
                p.addElement(tree_elem)
                doc.text.addElement(p)


        doc.save(self.filename)
        

    def _getMainImage(self, model, person, doc):
        '''
        Returns image for a person, return value is draw.Frame or None
        '''
        photos = model.getPhotos(person)
        if photos: photos = [photo for photo in photos if photo.default]
        if photos and self.imagedir is not None: 
            
            # find image file, get its data
            imgfile = os.path.join(self.imagedir, photos[0].file)
            img = Image.open(imgfile)
            imgdata = file(imgfile, 'rb').read()
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
        