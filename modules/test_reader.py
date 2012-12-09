#!/bin/env python
'''
Created on Sep 6, 2012

@author: salnikov
'''

from optparse import OptionParser
from drevo_reader import DrevoReader 

def main():

    parser = OptionParser(usage = "usage: %prog [options] file.xml")
    
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error('One positional argument is required')

    reader = DrevoReader(args[0])


    for p in reader.people:
        
        print "%s %s" % (p.id, p.name.full)

if __name__ == '__main__':
    main()
    