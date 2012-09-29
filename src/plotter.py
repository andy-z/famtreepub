'''
Created on Sep 22, 2012

@author: salnikov
'''

import os
from pydot import Dot, Node, Edge
import Image

nodeid = 1

class Plotter(object):


    def __init__(self):
        '''
        Constructor
        '''
        pass
    

    
    def parent_tree(self, person, max_gen=3):
        """
        """
        
        
        def _addPerson(person, g, gen):
            
            global nodeid
            
            label = person.name.full.replace(' ', '\n')
            node = Node(nodeid, label=label, shape='box')
            nodeid += 1
            g.add_node(node)
            
            if gen > 0 and person.father and person.mother:
                if person.father:
                    fnode = _addPerson(person.father, g, gen-1)
                else:
                    fnode = Node(nodeid, label='?', shape='box')
                    nodeid += 1
                g.add_edge(Edge(node, fnode, dir='none'))
                if person.mother:
                    mnode = _addPerson(person.mother, g, gen-1)
                else:
                    mnode = Node(nodeid, label='?', shape='box')
                    nodeid += 1
                g.add_edge(Edge(node, mnode, dir='none'))
                
            return node
        
        
        # make new graph
        g = Dot(rankdir="LR", ranksep="0.1")
        
        # add all people
        _addPerson(person, g, max_gen)
        
        # plot
        tmpfname = "/tmp/drevo_plotter.png"
        g.write(tmpfname, format='png')
        img = Image.open(tmpfname)
        imgdata = file(tmpfname).read()
        os.remove(tmpfname)
                    
        return imgdata, img.size[0], img.size[1]
    