'''
Created on Dec 7, 2012

@author: salnikov

Module for date-related utilities. 
'''

import datetime
import logging

_log = logging.getLogger(__name__)

# definitions for date format
YMD = 'YMD'
DMY = 'DMY'
MDY = 'MDY'

# this are used for formatting only
YbD = 'YbD'   # 2012-Dec-31
YBD = 'YBD'   # 2012-December-31
DbY = 'DbY'   # 31-Dec-2012
DBY = 'DBY'   # 31-December-2012

#
# maps date format string to the tuple if indices, first number in
# a tuple is a year index, second is month index, last is day index
#
_ymd_index = dict(YMD=(0,1,2), DMY=(2,1,0), MDY=(2,0,1), 
                  YbD=(0,1,2), YBD=(0,1,2), DbY=(2,1,0), DBY=(2,1,0))

def separator(dates):
    '''
    Guesses which separator is in use for the list of dates.
    Returns separator character, empty string if separator is not needed 
    (list is empty or dates are years only)l; or throws an exception if
    there is more than one separator character in use.
    
    This method expects that all dates have valid format and does not check it. 
    '''

    sep = ''
    
    for date in dates:
        for ch in date:
            # remove digits and parens from string
            if ch not in '0123456789()':
                if sep == '' :
                    sep = ch
                elif ch != sep:
                    raise ValueError("Conflicting separators in the dates")
    return sep

def guessFormat(dates):
    '''
    Guesses the  format of the date strings. Returns one of the YMD, DMY, or MDY
    constants.
    '''
    
    dates = list(dates)
    
    sep = separator(dates)
    
    formats = []
    for fmt in (DMY, YMD, MDY):

        try:
            res = [parse(date, fmt, sep) for date in dates]
            formats.append(fmt)
        except Exception, ex:
            #_log.error('guessFormat: %s', ex)
            pass
    
    if len(formats) != 1:
        raise ValueError('date: unrecognized date format')
        
    return formats[0]


class Date(object):
    
    def __init__(self, date, jc_date=None):
        '''
        Constructor takes one or two tuples, tuples can have 1 to 3 numbers.
        First element of tuple is year, second (optional) is month, third 
        (optional) is day.
        
        If you pass None as the first argument then "no-date" object is constructed.
        
        If second tuple is passed then it specifies Julian date.
        '''
        self.date = date
        self.jc_date = jc_date
        
        # validate, if these are not good then this will raise exception
        if self.date: Date._validate(self.date)
        if self.jc_date: Date._validate(self.jc_date)

    def __cmp__(self, other):
        return cmp(self.date, other.date)

    def __nonzero__(self):
        return self.date is not None

    def __str__(self):
        def fmt(date):
            res = ""
            if len(date) > 0: res = "%04d" % date[0]
            if len(date) > 1: res = "%02d.%s" % (date[1], res)
            if len(date) > 2: res = "%02d.%s" % (date[2], res)
            return res
        
        res = fmt(self.date)
        if self.jc_date: 
            res += " ({0} JC)".format(fmt(self.jc_date))
        return res

    def fmt(self, fmt, sep):
        
        def _fmt(date, fmt, sep):
            idx = _ymd_index[fmt]
            t = [None, None, None]
            if date: t[idx[0]] = "%04d" % date[0]
            if date and len(date) > 1: t[idx[1]] = "%02d" % date[1]
            if date and len(date) > 2: t[idx[2]] = "%02d" % date[2]
            return sep.join([x for x in t if x is not None])
        
        res = _fmt(self.date, fmt, sep)
        if self.jc_date: 
            res += " ({0} JC)".format(_fmt(self.jc_date, fmt, sep))
        return res

    # Quick validation of tuple contents
    @staticmethod
    def _validate(tup):
        while len(tup) < 3:
            tup += (1,)
        datetime.date(*tup)


def _parseOne(str):
    i = str.find('(')
    if i < 0:
        d = int(str)
        return d, d
    else:
        if str.endswith(')'):
            return int(str[:i]), int(str[i+1:-1])
    return None, None

def parse(datestr, fmt, sep):
    '''
    Parse date string.
    
    General date format is either an empty string (for no-date) or
    one to three components separated by `sep` character. Each component
    is a number optionally followed by another number in parentheses 
    (for Julian dates). Order of the components is defined by fmt string.
    
    Fmt string can be:
        YMD - for year/month/day order, if string has two components then 
              it will be year/month
        DMY - for day/month/year order, if string has two components then 
              it will be month/year
        MDY - for month/day/year order, if string has two components then 
              it will be month/year
    If string has just a single component it is always year.
    
    Ranges for months and days are checked, if they are not in valid range
    then exception is thrown.
    '''
    
    date = None
    jc_date = None
    if datestr:
        dd = datestr.split(sep)
        if len(dd) == 1:
            # year only
            years = _parseOne(dd[0])
            date = (years[0],)
            jc_date = (years[1],)
        elif len(dd) == 2:
            # year and month
            iy , im = 1, 0
            if _ymd_index[fmt][0] == 0: iy, im = 0, 1
            years = _parseOne(dd[iy])
            months = _parseOne(dd[im])
            date = (years[0], months[0])
            jc_date = (years[1], months[1])
        elif len(dd) == 3:
            # year, month, day
            iy, im, id = _ymd_index[fmt]
            years = _parseOne(dd[iy])
            months = _parseOne(dd[im])
            days = _parseOne(dd[id])
            date = (years[0], months[0], days[0])
            jc_date = (years[1], months[1], days[1])

    if jc_date == date: jc_date = None
    
    return Date(date, jc_date)
