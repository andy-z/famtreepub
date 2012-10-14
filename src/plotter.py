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

class Plotter(object):


    def __init__(self):
        '''
        Constructor
        '''
        pass
    

    
    def parent_tree(self, person, max_gen=4, width="5in", gen_dist="12pt", font_size="10pt"):
        """
        Plot parent tree of a person, max_gen gives the max total number of generations plotted.
        
        Returns 4-tuple: image data, mime-type, image width, image height.
        If tree cannot be plotted (e.g. when person has no parents) then None is returned
        """
        
        
        # returns number known generations for a person
        def _genDepth(person):
            if not person: return 0
            return max(_genDepth(person.father), _genDepth(person.mother)) + 1
        
        # generator for persont parents, returns None for unknown parent
        def _parents(people):
            for p in people:
                if p:
                    yield p.father
                    yield p.mother
                else:
                    yield None
                    yield None

        # get the number of generations, limit to 4
        ngen = min(_genDepth(person), 4)
        _log.debug('parent_tree: ngen = %d', ngen)

        # if no parents then do not plot anything
        if ngen < 2: return
                
        # calculate box sizes
        plot_width = Size(width)
        gen_dist = Size(gen_dist)
        box_width = (plot_width - (ngen-1)*gen_dist) / ngen
        vmargin = Size("4pt")
        vmargin2 = Size("6pt")
        
        # make the list of people in each generation
        generations = [[person]]
        while len(generations) < ngen:
            generations.append(list(_parents(generations[-1])))

        # make list of boxes, here older generation comes first
        boxes = []
        for gen, gen_people in enumerate(generations):
            boxes.insert(0, [])
            
            x0 = gen*(gen_dist + box_width) + Size('0.5pt')
            
            for pers in gen_people:
                # displayed persons name
                style = _rect_style
                if pers is None:
                    name = '?'
                    style = _rect_unknown_style
                elif gen == 0:
                    name = (pers.name.first or '') + ' ' + (pers.name.maiden or pers.name.last or '') 
                else:
                    name = (pers.name.first or '') + ' ' + (pers.name.last or '')
                _log.debug('parent_tree: gen = %d; name = %s', gen, name)
                box = TextBox(text=name, x0=x0, width=box_width, font_size=font_size, rect_style=style)
                boxes[0].append(box)

        # layout all boxes
        for gen, gen_boxes in enumerate(boxes):
            if gen == 0:
                
                # re-calculate vertical positions in last generation
                y = Size(0)
                for v, box in enumerate(gen_boxes):
                    box.y0 = y
                    y += box.height
                    if v % 2: 
                        y +=  vmargin2
                    else: 
                        y +=  vmargin
            else:
                
                # in all other generations place child between its parents
                for v, box in enumerate(gen_boxes):
                    # boxes for parents
                    parents = boxes[gen-1][2*v:2*v+2]
                    y0 = parents[0].y0 
                    y1 = parents[1].y1
                    box.y0 = (y0+y1)/2 - box.height/2

            # get full height
            height = boxes[0][-1].y1

        # produce complete XML
        svg = structure.svg()
        for gen_boxes in boxes:
            for box in gen_boxes:
                for element in box.svg():
                    svg.addElement(element)

        # lines connecting boxes
        for gen, gen_boxes in enumerate(boxes):
            if gen == 0: continue
            for v, box in enumerate(gen_boxes):
                x0 = box.x1
                y0 = box.midy
                box1 = boxes[gen-1][v*2]
                x1 = box1.x0
                y1 = box1.midy
                midx = (x0 + x1) / 2
                style = _pline_unknown_style if box1.text == '?' else _pline_style
                svg.addElement(shape.line(X1=str(x0), Y1=str(y0), X2=str(midx), Y2=str(y0), style=style))
                svg.addElement(shape.line(X1=str(midx), Y1=str(y0), X2=str(midx), Y2=str(y1), style=style))
                svg.addElement(shape.line(X1=str(midx), Y1=str(y1), X2=str(x1), Y2=str(y1), style=style))
                box2 = boxes[gen-1][v*2+1]
                y1 = box2.midy
                style = _pline_unknown_style if box2.text == '?' else _pline_style
                svg.addElement(shape.line(X1=str(midx), Y1=str(y0), X2=str(midx), Y2=str(y1), style=style))
                svg.addElement(shape.line(X1=str(midx), Y1=str(y1), X2=str(x1), Y2=str(y1), style=style))


        # generate full XML
        xml = svg.wrap_xml(svg.getXML(), encoding='UTF-8')
        
        return xml, 'image/svg', width, height
