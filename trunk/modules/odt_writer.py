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
import gtext
import utils

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


_ = gtext.gtext

# indices of margins
MARGIN_LEFT = 0
MARGIN_RIGHT = 1
MARGIN_TOP = 2
MARGIN_BOTTOM = 3
MARGIN_KW = ['margin_left', 'margin_right', 'margin_top', 'margin_bottom']

class OdtWriter(object):
    '''
    Format tree as ODF text document
    '''


    def __init__(self, fileFactory, output, config):

        self.fileFactory = fileFactory
        self.output = output         # output file name or file object
        
        # page dimensions
        self.page_width = config.getSize("page_width")
        self.page_height = config.getSize("page_height")

        # set margins, use defaults if none given
        self.margins = [config.getSize(MARGIN_KW[i]) for i in range(4)]
        
        # starting page number
        self.firstpage = config.get('first_page')
                
    def write(self, model):
        
        doc = OpenDocumentText()

        # set paper dimensions
        pageLayout = style.PageLayout(name=u"pl1")
        doc.automaticstyles.addElement(pageLayout)
        plProp = style.PageLayoutProperties(pageheight=str(self.page_height), pagewidth=str(self.page_width), 
                        marginleft=str(self.margins[MARGIN_LEFT]), marginright=str(self.margins[MARGIN_RIGHT]), 
                        margintop=str(self.margins[MARGIN_TOP]), marginbottom=str(self.margins[MARGIN_BOTTOM]))
        pageLayout.addElement(plProp)

        # add page numbers to the footers
        footer = style.Footer()
        foostyle = style.Style(name="Footer", family="paragraph")
        foostyle.addElement(style.ParagraphProperties(textalign='center'))
        foostyle.addElement(style.TextProperties(fontsize='10pt'))
        doc.automaticstyles.addElement(foostyle)
        p = text.P(stylename = foostyle)
        p.addElement(text.PageNumber(selectpage="current", pageadjust=str(self.firstpage-1)))
        footer.addElement(p)
        
        masterpage = style.MasterPage(name=u"Standard", pagelayoutname=pageLayout)
        masterpage.addElement(footer)
        doc.masterstyles.addElement(masterpage)
        
        # heading styles
        h1topmrg = (self.page_height - self.margins[MARGIN_TOP] - self.margins[MARGIN_BOTTOM]) * 0.5  - Size('22pt')
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

        # centered paragraph
        centered = style.Style(name="centered", family="paragraph")
        centered.addElement(style.ParagraphProperties(textalign='center'))
        doc.styles.addElement(centered)

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
        
        
        # Title page
        hdr = _("Person List", None)
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
            p.addText(_('Born', person) + ": ")
            if person.birth.date: 
                p.addText(str(person.birth.date))
            else:
                p.addText(_('Unknown', person))
            if person.birth.place: 
                p.addText(", " + person.birth.place)
            doc.text.addElement(p)

            # Parents
            if person.mother:
                p = text.P(text = _('Mother', person) + ": " + person.mother.name.full)
                doc.text.addElement(p)
            if person.father:
                p = text.P(text = _('Father', person) + ": " + person.father.name.full)
                doc.text.addElement(p)


            # spouses and children
            own_kids = []
            if person.spouses:
                hdr = _("Spouses and children", person)
                doc.text.addElement(text.H(text=hdr, outlinelevel=3, stylename=h3style))
            for spouse in person.spouses:
                _log.debug('spouse = %s; children ids = %s; children = %s', spouse, spouse._children, spouse.children)
                if spouse.person:
                    p = text.P(text = _('Spouse', person) + ": " + spouse.person.name.full)
                    kids = [c.name.first for c in spouse.children]
                    if kids: p.addText("; " + _('kids', '') + ': ' + ', '.join(kids))
                    doc.text.addElement(p)
                else:
                    own_kids += [c.name.first for c in spouse.children]
            if own_kids: 
                p = text.P(text = _('Kids', '') + ': ' + ', '.join(own_kids))
                doc.text.addElement(p)

            # All relevant dates
            events = []
            for spouse in person.spouses:
                
                # marriage date if known
                if spouse.marriage.date: 
                    descr = _('Marriage', person) 
                    if spouse.person:
                        descr += ", " + _('Spouse', person) + ": "  + spouse.person.name.maiden_full
                    events.append((spouse.marriage.date, descr))

                # kids birth dates
                for kid in spouse.children:
                    if kid.birth.date:
                        descr = _('Born', kid) + " " + _('kid', kid) + " " + kid.name.first
                        events.append((kid.birth.date, descr))

            if person.death.date:
                descr = _('Died', person)
                if person.death.place: descr += ", " + person.death.place
                events.append((person.death.date, descr))
                    
            events.sort()
            if events:
                hdr = _("Events and dates", person)
                doc.text.addElement(text.H(text=hdr, outlinelevel=3, stylename=h3style))
            for evt in events:
                p = text.P(text = str(evt[0]) + ": " + evt[1])
                doc.text.addElement(p)
            

            # Comments are published as set of paragraphs
            if person.comment:
                hdr = _("Comments", person)
                doc.text.addElement(text.H(text=hdr, outlinelevel=3, stylename=h3style))

                doc.text.addElement(text.P())
                for para in person.comment.split('\n'):
                    doc.text.addElement(text.P(text = para))
                    
            # plot ancestors tree
            tree_elem = self._getParentTree(person, doc)
            if tree_elem:
                hdr = _("Ancestor tree", person)
                doc.text.addElement(text.H(text=hdr, outlinelevel=3, stylename=h3style))
                p = text.P(stylename=centered)
                p.addElement(tree_elem)
                doc.text.addElement(p)


        # generate some stats
        hdr = _("Statistics", None)
        doc.text.addElement(text.H(text=hdr, outlinelevel=1, stylename=h1style))
        doc.text.addElement(text.P(text='', stylename=brstyle))

        hdr = _("Total Statistics", None)
        doc.text.addElement(text.H(text=hdr, outlinelevel=2, stylename=h2style))
        nmales = len([person for person in people if person.sex == 'M'])
        nfemales = len([person for person in people if person.sex == 'F'])
        p = text.P(text = '%s: %d' % (_('Person count'), len(people)))
        doc.text.addElement(p)
        p = text.P(text = '%s: %d' % (_('Female count'), nfemales))
        doc.text.addElement(p)
        p = text.P(text = '%s: %d' % (_('Male count'), nmales))
        doc.text.addElement(p)


        hdr = _("Name Statistics", None)
        doc.text.addElement(text.H(text=hdr, outlinelevel=2, stylename=h2style))

        hdr = _("Female Name Frequency", None)
        doc.text.addElement(text.H(text=hdr, outlinelevel=3, stylename=h3style))
        elem = self._namestat(person for person in people if person.sex == 'F')
        doc.text.addElement(elem)
        
        hdr = _("Male Name Frequency", None)
        doc.text.addElement(text.H(text=hdr, outlinelevel=3, stylename=h3style))
        elem = self._namestat(person for person in people if person.sex == 'M')
        doc.text.addElement(elem)
        
        # TOC
        doc.text.addElement(text.P(text='', stylename=brstyle))
        toc = text.TableOfContent(name='TOC')
        tocsrc = text.TableOfContentSource(outlinelevel=2)
        toctitle = text.IndexTitleTemplate(text = _('Table Of Contents'))
        tocsrc.addElement(toctitle)
        toc.addElement(tocsrc)
        doc.text.addElement(toc)

        # save the result
        if hasattr(self.output, 'write'):
            doc.write(self.output)
        else:
            doc.save(self.output)
        

    def _getMainImage(self, model, person, doc):
        '''
        Returns image for a person, return value is draw.Frame or None
        '''
        photos = model.getPhotos(person)
        if photos: photos = [photo for photo in photos if photo.default]
        if photos: 
            
            # find image file, get its data
            imgfile = self.fileFactory.openImage(photos[0].file)
            if imgfile:
                imgdata = imgfile.read()
                imgfile = StringIO(imgdata)
                img = Image.open(imgfile)
                filename = "Pictures/" + hashlib.sha1(imgdata).hexdigest() + '.' +img.format
    
                # calculate size of the frame
                w, h = utils.resize(img.size, (2.5, 2.5))
                frame = draw.Frame(width="%.3fin"%w, height="%.3fin"%h)
                imgref = doc.addPicture(filename, "image/"+img.format, imgdata)
                frame.addElement(draw.Image(href=imgref))
                return frame
        
        
    def _getParentTree(self, person, doc):
        '''
        Returns element containg parent tree or None
        '''

        width = self.page_width - self.margins[MARGIN_LEFT] - self.margins[MARGIN_RIGHT]

        plotter = Plotter(width=width, gen_dist="12pt", font_size="9pt")
        img = plotter.parent_tree(person)
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
                n1, c1 = namefreq[2*i]
                n2, c2 = None, None
                if 2*i+1 < len(namefreq):
                    n2, c2 = namefreq[2*i+1]
                yield n1, c1, n2, c2
        
        namefreq = {}
        for person in people:
            counter = namefreq.setdefault(person.name.first, 0)
            namefreq[person.name.first] += 1
        namefreq = [(key, val) for key, val in namefreq.items()]
        # sort accending in name
        namefreq.sort()
        total = float(sum(count for name, count in namefreq))

        tbl = table.Table()
        tbl.addElement(table.TableColumn())
        tbl.addElement(table.TableColumn())
        tbl.addElement(table.TableColumn())
        tbl.addElement(table.TableColumn())

        for name1, count1, name2, count2 in _gencouples(namefreq):

            row = table.TableRow()
            
            cell = table.TableCell()
            cell.addElement(text.P(text = name1 or '-'))
            row.addElement(cell)
            
            cell = table.TableCell()
            cell.addElement(text.P(text = '%d (%.1f%%)' % (count1, count1/total*100)))
            row.addElement(cell)

            if count2 is not None:

                cell = table.TableCell()
                cell.addElement(text.P(text = name2 or '-'))
                row.addElement(cell)
                
                cell = table.TableCell()
                cell.addElement(text.P(text = '%d (%.1f%%)' % (count2, count2/total*100)))
                row.addElement(cell)

            tbl.addElement(row)

        return tbl
