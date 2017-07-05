'''
Created on Dec 7, 2012

@author: salnikov

Module for date-related utilities.
'''

import re
import datetime
import logging

_log = logging.getLogger(__name__)

# definitions for date format
YMD = 'YMD'
DMY = 'DMY'
MDY = 'MDY'

# this are used for formatting only
YbD = 'YbD'  # 2012-Dec-31
YBD = 'YBD'  # 2012-December-31
DbY = 'DbY'  # 31-Dec-2012
DBY = 'DBY'  # 31-December-2012

#
# maps date format string to the tuple if indices, first number in
# a tuple is a year index, second is month index, last is day index
#
_ymd_index = dict(YMD=(0, 1, 2), DMY=(2, 1, 0), MDY=(2, 0, 1),
                  YbD=(0, 1, 2), YBD=(0, 1, 2), DbY=(2, 1, 0), DBY=(2, 1, 0))


_date_re_ymd = re.compile(r'''\b
        (?P<year>\d{4})                       # 4 digits
        (?:\((?P<year_jc>\d{2,4})\))?         # optional 4 digits in parens fo JC
        ([-./])                           # separator character
        (?P<mon>\d{2})                    # 2 digits
        (?:\((?P<mon_jc>\d{2})\))?        # optional 2 digits in parens fo JC
        \3                                # separator character
        (?P<day>\d{2})                # 2 digits
        (?:\((?P<day_jc>\d{2})\))?    # optional 2 digits in parens fo JC
\b
''', re.X)

_date_re_dmy = re.compile(r'''\b
        (?P<day>\d{2})                # 2 digits
        (?:\((?P<day_jc>\d{2})\))?    # optional 2 digits in parens fo JC
        ([-./])                       # separator character
        (?P<mon>\d{2})                    # 2 digits
        (?:\((?P<mon_jc>\d{2})\))?        # optional 2 digits in parens fo JC
        \3                                # separator character
        (?P<year>\d{4})                       # 4 digits
        (?:\((?P<year_jc>\d{2,4})\))?         # optional 4 digits in parens fo JC
\b
''', re.X)

_date_re_my = re.compile(r'''\b
        (?P<mon>\d{2})                    # 2 digits
        (?:\((?P<mon_jc>\d{2})\))?        # optional 2 digits in parens fo JC
        ([-./])                           # separator character
        (?P<year>\d{4})                       # 4 digits
        (?:\((?P<year_jc>\d{2,4})\))?         # optional 4 digits in parens fo JC
\b
''', re.X)

_date_re_ym = re.compile(r'''\b
        (?P<year>\d{4})                       # 4 digits
        (?:\((?P<year_jc>\d{2,4})\))?         # optional 4 digits in parens fo JC
        ([-./])                           # separator character
        (?P<mon>\d{2})                    # 2 digits
        (?:\((?P<mon_jc>\d{2})\))?        # optional 2 digits in parens fo JC
\b
''', re.X)

_date_re_y = re.compile(r'''\b
        (?P<year>\d{4})                       # 4 digits
        (?:\((?P<year_jc>\d{2,4})\))?         # optional 4 digits in parens fo JC
\b
''', re.X)


def guessFormat(dates):
    '''
    Guesses the  format of the date strings. Returns one of the YMD, DMY, or MDY
    constants.
    '''

    dates = list(dates)
    _log.info("guessFormat: dates: %s", dates)
    if not dates:
        # any format will do
        return YMD

    formats = []
    for fmt in (DMY, YMD, MDY):

        try:
            res = [parse(date, fmt) for date in dates]
            formats.append(fmt)
        except Exception as ex:
            # _log.debug("guessFormat: failed: %s", ex)
            # print "guessFormat: failed: %s" % ex
            pass

    if len(formats) != 1:
        _log.debug("guessFormat: formats: %s", formats)
        raise ValueError('date: unrecognized date format')
    else:
        _log.info("guessFormat: found format: %s", formats[0])

    return formats[0]


class Date(object):

    def __init__(self, tuples, dstr):
        '''
        Constructor takes one or two tuples, tuples can have 1 to 3 numbers.
        First element of tuple is year, second (optional) is month, third
        (optional) is day.

        If you pass None as the first argument then "no-date" object is constructed.

        If second tuple is passed then it specifies Julian date.
        '''
        self.tuples = tuples
        self.dstr = dstr

    def __cmp__(self, other):
        tup1 = self.tuples[0] if self.tuples else ()
        tup2 = other.tuples[0] if other.tuples else ()
        return cmp(tup1[:3], tup2[:3])

    def __nonzero__(self):
        return self.tuples is not None

    def __str__(self):
        return self.fmt('DMY', '.')

    def fmt(self, fmt, sep):

        def _fmtThree(date, fmt, sep):
            idx = _ymd_index[fmt]
            t = [None, None, None]
            t[idx[0]] = "%04d" % date[0]
            if date[1]:
                t[idx[1]] = "%02d" % date[1]
            if date[2]:
                t[idx[2]] = "%02d" % date[2]
            return sep.join([x for x in t if x is not None])

        def _fmtSix(date, fmt, sep):
            res = _fmtThree(date[:3], fmt, sep)
            if len(date) == 6:
                res += " ({0} JC)".format(_fmtThree(date[3:], fmt, sep))
            return res

        if self.tuples is None:
            return ""
        return self.dstr.format(*[_fmtSix(dt, fmt, sep) for dt in self.tuples])


# Quick validation of tuple contents
def _validate(tup):
    # replace zeros with ones
    fix = [max(1, x) for x in tup]
    datetime.date(*fix)

def _parseOne(pstr):
    i = pstr.find('(')
    if i < 0:
        d = int(pstr)
        return d, d
    else:
        if pstr.endswith(')'):
            return int(pstr[:i]), int(pstr[i + 1:-1])
    return None, None

def parse(datestr, fmt):
    '''
    Parse date string. date string can contain arbitrary text with one or
    few dates (like "From 01.01.1967 to 01.01.1968"). Returns Date object

    General date format is either an empty string (for no-date) or
    one to three components separated by separators (one of .-/). Each
    component is a number optionally followed by another number in
    parentheses (for Julian dates). Order of the components is defined by
    fmt string.

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

    # _log.debug("date.parse: datestr=%s fmt=%s", datestr, fmt)

    if not datestr:
        return Date(None, None)

    fstr = datestr

    tuples = []


    count = 0
    while True:

        # find next date
        match = _date_re_ymd.search(fstr)
        if match and fmt[0] != 'Y':
            raise ValueError('Date string in incorrect order, fstr="{0}" fmt={1}'.format(fstr, fmt))
        if not match:
            match = _date_re_dmy.search(fstr)
            if match and fmt[0] == 'Y':
                raise ValueError('Date string in incorrect order, fstr="{0}" fmt={1}'.format(fstr, fmt))
        if not match:
            match = _date_re_my.search(fstr)
            if match and fmt[0] == 'Y':
                raise ValueError('Date string in incorrect order, fstr="{0}" fmt={1}'.format(fstr, fmt))
        if not match:
            match = _date_re_ym.search(fstr)
            if match and fmt[0] != 'Y':
                raise ValueError('Date string in incorrect order, fstr="{0}" fmt={1}'.format(fstr, fmt))
        if not match:
            match = _date_re_y.search(fstr)
        if not match:
            break


        # _log.debug('date.parse: match=%s', match.group(0))
        gd = match.groupdict(0)

        y, m, d, yjc, mjc, djc = [int(gd.get(k, 0))
                                  for k in ('year', 'mon', 'day', 'year_jc', 'mon_jc', 'day_jc')]
        if fmt == 'MDY':
            # MDY is DMY with swapped MD
            m, d = d, m
            mjc, djc = djc, mjc

        if (yjc, mjc, djc) == (0, 0, 0):
            dt = (y, m, d)
            try:
                _validate(dt)
            except Exception as ex:
                # _log.error("validation error: ex={0} fstr={1} dt={2}".format(str(ex), fstr, dt))
                raise
        else:
            if yjc == 0:
                yjc = y
            if mjc == 0:
                mjc = m
            if djc == 0:
                djc = d
            dt = (y, m, d, yjc, mjc, djc)
            try:
                _validate(dt[:3])
                _validate(dt[3:])
            except Exception as ex:
                # _log.error("validation error: ex={0} fstr={1} dt={2}".format(str(ex), fstr, dt))
                raise

        tuples.append(dt)
        fstr = fstr[:match.start()] + "{" + str(count) + "}" + fstr[match.end():]
        count += 1

    d = Date(tuples, fstr)
    # _log.debug("date.parse: date=%s", d)
    return d
