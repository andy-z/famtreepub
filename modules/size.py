'''
Module which defines class for manipulating size values.

Created on Sep 26, 2012

@author: salnikov
'''

from __future__ import absolute_import, division, print_function

import types

MM_PER_INCH = 25.4
PT_PER_INCH = 72.

class Size(object):
    '''
    Class for specifying size values.

    Size can be specified as a number with units, supported units are pt (points),
    in (inches), cm (centimeters), and mm(millimeters). If units are not specified
    then inches are assumed.
    '''

    dpi = 96.  # some random number for converting pixels to inches


    def __init__(self, value=0):
        '''
        Constructor converts input value to a size.

        If input value has numeric type then it is assumed to be size in inches.
        If input value is a string then it should be a floating number followed
        by optional suffix (one of pt, in, mm, cm). Without suffix the number gives
        size in inches.

        If string does not have correct format then ValueError is raised.
        If input value has unsupported type TypeError is raised.
        '''

        if isinstance(value, (types.FloatType, types.IntType, types.LongType)):
            self.value = float(value)
        elif isinstance(value, types.StringTypes):
            # convert units to inches
            if value.endswith('pt'):
                self.value = float(value[:-2]) / PT_PER_INCH
            elif value.endswith('in'):
                self.value = float(value[:-2])
            elif value.endswith('cm'):
                self.value = float(value[:-2]) / (MM_PER_INCH / 10)
            elif value.endswith('mm'):
                self.value = float(value[:-2]) / MM_PER_INCH
            elif value.endswith('px'):
                self.value = float(value[:-2]) / self.dpi
            else:
                # without suffix assume it's inches
                self.value = float(value)
        elif isinstance(value, Size):
            self.value = value.value
        else:
            raise TypeError("incorrect type of the argument: " + str(type(value)))

    @property
    def pt(self):
        ''' return size in points '''
        return self.value * 72.

    @property
    def px(self):
        ''' return size in pixels '''
        return int(round(self.value * self.dpi))

    @property
    def inches(self):
        ''' return size in inches '''
        return self.value

    def __str__(self):
        ''' Returns string representation, e.g. "12in" '''
        return str(self.value) + 'in'

    def __cmp__(self, other):
        ''' Compare two sizes size '''
        return cmp(self.value, Size(other).value)

    def __sub__(self, other):
        ''' Subtract size from other size '''
        return Size(self.value - other.value)

    def __add__(self, other):
        ''' Add two sizes '''
        return Size(self.value + other.value)

    def __mul__(self, other):
        ''' Multiply size by a factor '''
        return Size(self.value * other)

    def __div__(self, other):
        ''' Divide size by a factor '''
        return Size(self.value / other)

    def __truediv__(self, other):
        ''' Divide size by a factor '''
        return Size(self.value / other)

    def __rmul__(self, other):
        ''' Multiply size by a factor '''
        return Size(self.value * other)

    def __xor__(self, units):
        ''' Size(1.)^"mm"  will return "25.4mm" '''
        if units == 'in':
            return "%gin" % (self.value,)
        elif units == 'pt':
            return "%gpt" % (self.value * PT_PER_INCH,)
        elif units == 'cm':
            return "%gcm" % (self.value * MM_PER_INCH / 10,)
        elif units == 'mm':
            return "%gmm" % (self.value * MM_PER_INCH,)
        elif units == 'px':
            return "%gpx" % (int(round(self.value * self.dpi)),)
        else:
            return "%gin" % (self.value,)
