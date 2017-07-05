"""Module for validation of the uploaded input files.
"""

import logging

from .drevo_reader import DrevoReader
from .input import FileLocator

_log = logging.getLogger(__name__)

def validate(fname):
    '''Checks that input file is an acceptable file.

    Acceptable is either an XML file that can be parsed by DrevoReader class
    or a zip file containing such XML file.

    Parameters
    ----------
    fname : str
        Uploaded file location.

    Raises
    ------
    An exception is raised if file(s) cannot be validated.
    '''

    floc = FileLocator(fname)
    if floc is None:
        raise ValueError('File %s does not exist' % fname)

    reader = DrevoReader(floc)
    if not reader.people:
        raise ValueError('File has no persons')
