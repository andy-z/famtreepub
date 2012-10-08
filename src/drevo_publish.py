#!/bin/env python
'''
Created on Sep 8, 2012

@author: salnikov
'''

import os
from optparse import OptionParser
import logging

logging.basicConfig()

from drevo_reader import DrevoReader 
from odt_writer import OdtWriter
from size import Size
from input import FileLocator

def main():

    # setup option parser and parse command line
    parser = OptionParser(usage = "usage: %prog [options] file.xml")
    parser.add_option("-v", "--verbose",
                  action="count", dest="verbose", default=0,
                  help="more verbose output")
    parser.add_option("-o", "--output",
                  action="store", dest="output", default=None,
                  help="set name of the output file")
    parser.add_option("-H", "--page-height", default="9in",
                  help="page height of the output document, def: 9in")
    parser.add_option("-W", "--page-width", default="6in",
                  help="page width of the output document, def: 6in")
    parser.add_option("-M", "--margin", default="0.5in",
                  help="page margins of the output document, def: .5n")
    parser.add_option("-i", "--image-dir", default=None,
                  help="directory with image files")

    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error('One positional argument is required')

    # setup logging
    if options.verbose == 1:
        logging.getLogger().setLevel(logging.INFO)
    elif options.verbose > 1:
        logging.getLogger().setLevel(logging.DEBUG)

    # make output file name
    if not options.output:
        options.output = os.path.basename(args[0]) + '.odt'

    # inctantiate file locator
    fileFactory = FileLocator(args[0], imagedir=options.image_dir)

    reader = DrevoReader(fileFactory)

    writer = OdtWriter(fileFactory,
                       options.output, 
                       page_width=Size(options.page_width), 
                       page_height=Size(options.page_height),
                       margin=Size(options.margin))
    writer.write(reader)
    
    print "Finished OK"


if __name__ == '__main__':
    main()
