'''
Created on Sep 22, 2012

@author: salnikov
'''

import os
import logging
from pysvg import shape, builders, structure

from size import Size
from textbox import TextBox

_rect_style = "fill:none;stroke-width:1pt;stroke:black"
_rect_unknown_style = "fill:none;stroke-width:1pt;stroke:grey"
_pline_style = "fill:none;stroke-width:0.5pt;stroke:black"
_pline_unknown_style = "fill:none;stroke-width:0.5pt;stroke:grey"

_log = logging.getLogger(__name__)



class _PersonBox(object):
    
    _margin = Size('1pt')
    
    def __init__(self, person, gen, motherBox, fatherBox, box_width, max_box_width, font_size, gen_dist):
        self.mother = motherBox
        self.father = fatherBox
        self.generation = gen
        
        # displayed persons name
        if person is None:
            self.name = '?'
        elif gen == 0:
            self.name = (person.name.first or '') + ' ' + (person.name.maiden or person.name.last or '')
        else:
            self.name = (person.name.first or '') + ' ' + (person.name.last or '')
        style = _rect_unknown_style if person is None else _rect_style
        href = None if person is None else ('#person.' + person.id)
        x0 = gen*(gen_dist + box_width) + Size('1pt')
        self.box = TextBox(text=self.name, x0=x0, width=box_width, maxwidth=max_box_width, font_size=font_size, rect_style=style, href=href)
        
        self.setY0(Size())

    def height(self):

        h = Size()
        if self.mother:
            h = self.mother.height() + self.father.height() + 2*self._margin
        h = max(h, self.box.height + 2*self._margin)
        _log.debug('_PersonBox.name = %s; height = %s', self.name, h)
        return h
    
    def setY0(self, y0):
        
        _log.debug('_PersonBox.name = %s; setY0 = %s', self.name, y0)
        if self.mother:
            self.mother.setY0(y0 + self._margin)
            mheight = self.mother.height()
            self.father.setY0(y0 + mheight + self._margin)
            self.box.y0 = (self.mother.box.midy + self.father.box.midy - self.box.height) / 2
        else:
            self.box.y0 = y0 + self._margin
            
    def svg(self):

        textclass = None if self.name == '?' else 'svglink'
        elements = self.box.svg(textclass)
    
        if self.mother:
            x0 = self.box.x1
            y0 = self.box.midy
            pbox1 = self.mother
            x1 = pbox1.box.x0
            y1 = pbox1.box.midy
            midx = (x0 + x1) / 2
            style = _pline_unknown_style if pbox1.name == '?' else _pline_style
            elements.append(shape.line(X1=str(x0), Y1=str(y0), X2=str(midx), Y2=str(y0), style=_pline_style))
            elements.append(shape.line(X1=str(midx), Y1=str(y0), X2=str(midx), Y2=str(y1), style=style))
            elements.append(shape.line(X1=str(midx), Y1=str(y1), X2=str(x1), Y2=str(y1), style=style))
            pbox2 = self.father
            y1 = pbox2.box.midy
            style = _pline_unknown_style if pbox2.name == '?' else _pline_style
            elements.append(shape.line(X1=str(midx), Y1=str(y0), X2=str(midx), Y2=str(y1), style=style))
            elements.append(shape.line(X1=str(midx), Y1=str(y1), X2=str(x1), Y2=str(y1), style=style))
            
        return elements

class Plotter(object):


    def __init__(self, max_gen=4, width="5in", gen_dist="12pt", font_size="10pt", fullxml=True, refs=False):
        '''
        Constructor
        '''
        
        self.max_gen = max_gen
        self.width = Size(width)
        self.gen_dist = Size(gen_dist)
        self.font_size = Size(font_size)
        self.fullxml = fullxml
        self.refs = refs
        self.vmargin = Size("4pt")
        self.vmargin2 = Size("6pt")
    
    def parent_tree(self, person):
        """
        Plot parent tree of a person, max_gen gives the max total number of generations plotted.
        
        Returns 4-tuple: image data, mime-type, image width, image height.
        If tree cannot be plotted (e.g. when person has no parents) then None is returned
        """
        
        
        # returns number known generations for a person
        def _genDepth(person):
            if not person: return 0
            return max(_genDepth(person.father), _genDepth(person.mother)) + 1
        
        # generator for person parents, returns None for unknown parent
        def _boxes(box):
            yield box
            if box.mother:
                for p in _boxes(box.mother): yield p
                for p in _boxes(box.father): yield p

        # get the number of generations, limit to 4
        ngen = min(_genDepth(person), self.max_gen)
        _log.debug('parent_tree: person = %s', person.name)
        _log.debug('parent_tree: ngen = %d', ngen)

        # if no parents then do not plot anything
        if ngen < 2: return
                
        # calculate horizontal size of each box
        box_width = (self.width - (ngen-1)*self.gen_dist - Size('2pt')) / self.max_gen
        max_box_width = (self.width - (ngen-1)*self.gen_dist - Size('2pt')) / ngen
        
        # build tree of boxes
        boxtree = self._makeTree(person, 0, ngen, box_width, max_box_width)

        # get full height
        height = boxtree.height()
        
        # update box width for every generation and calculate total width
        width = Size('1pt')
        for gen in range(ngen):
            gen_width = max(pbox.box.width for pbox in _boxes(boxtree) if pbox.generation == gen)
            for pbox in _boxes(boxtree):
                if pbox.generation == gen:
                    pbox.box.width = gen_width
                    pbox.box.x0 = width
            width += gen_width + self.gen_dist
        width -= self.gen_dist
        width += Size('1pt')

        # produce complete XML
        svg = structure.svg(width=str(width), height=str(height))
        for pbox in _boxes(boxtree):
            for element in pbox.svg():
                svg.addElement(element)

        # generate full XML
        xml = svg.getXML()
        if self.fullxml:
            xml = svg.wrap_xml(xml, encoding='UTF-8')
        
        return xml, 'image/svg', width, height


    def _makeTree(self, person, gen, max_gen, box_width, max_box_width):
        
        if gen < max_gen:

            motherTree = None            
            fatherTree = None
            if person and (person.mother or person.father):
                motherTree = self._makeTree(person.mother, gen+1, max_gen, box_width, max_box_width)
                fatherTree = self._makeTree(person.father, gen+1, max_gen, box_width, max_box_width)
            box = _PersonBox(person, gen, motherTree, fatherTree, box_width, max_box_width, self.font_size, self.gen_dist)
            return box
        