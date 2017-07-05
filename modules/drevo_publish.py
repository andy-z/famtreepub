#!/bin/env python
'''
Created on Sep 8, 2012

@author: salnikov
'''

import os
from optparse import OptionParser
import logging

from .drevo_reader import DrevoReader
from .ftp_config import Config
from .odt_writer import OdtWriter
from .html_writer import HtmlWriter
from .input import FileLocator

logging.basicConfig()

def main():

    # setup option parser and parse command line
    parser = OptionParser(usage="usage: %prog [options] file.xml")
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
    parser.add_option("--margin-bottom", default="0.25in",
                      help="bottom page margin of the output document, def: .25n")
    parser.add_option("-i", "--image-dir", default=None,
                      help="directory with image files")
    parser.add_option("-t", "--type", default='odf',
                      help="type of output file, one of odf, html; def: odf")

    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error('One positional argument is required')

    # setup logging
    if options.verbose == 1:
        logging.getLogger().setLevel(logging.INFO)
    elif options.verbose > 1:
        logging.getLogger().setLevel(logging.DEBUG)

    # inctantiate file locator
    fileFactory = FileLocator(args[0], imagedir=options.image_dir)

    reader = DrevoReader(fileFactory)

    if options.type == 'odf':
        if not options.output: options.output = os.path.splitext(os.path.basename(args[0]))[0] + '.odt'
        config = Config()
        config['page_width'] = options.page_width
        config['page_height'] = options.page_height
        config['margin_left'] = options.margin
        config['margin_right'] = options.margin
        config['margin_top'] = options.margin
        config['margin_bottom'] = options.margin_bottom
        writer = OdtWriter(fileFactory, options.output, config)
    elif options.type == 'html':
        if not options.output: options.output = os.path.splitext(os.path.basename(args[0]))[0] + '.html'
        config = Config(page_width=options.page_width)
        writer = HtmlWriter(fileFactory, options.output, config)

    writer.write(reader)

    print "Finished OK"


if __name__ == '__main__':
    main()
