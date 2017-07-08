'''
Created on Dec 7, 2012

@author: salnikov

Module for date-related utilities.
'''

from __future__ import absolute_import, division, print_function

__all__ = ['Date', 'DateString', 'parse', 'guessFormat', 'YMD', 'DMY', 'MDY']

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

class Date(object):
    """Date representation.

    Date is a (year, month, day) triplet, each of them is optional.
    Additionally DAte contains optional representation of the same date
    in Julian calendar.

    Dates can be compared to each other and can be formatted
    using one of 'YMD', 'MDY', or 'DMY' formats.
    """

    # maps date format string to the tuple if indices, first number in
    # a tuple is a year index, second is month index, last is day index
    _ymd_index = dict(YMD=(0, 1, 2), DMY=(2, 1, 0), MDY=(2, 0, 1),
                      YbD=(0, 1, 2), YBD=(0, 1, 2), DbY=(2, 1, 0), DBY=(2, 1, 0))

    def __init__(self, year=None, month=None, day=None,
                 year_jc=None, month_jc=None, day_jc=None):
        self._validate(year, month, day)
        self._validate(year_jc, month_jc, day_jc)

        self.year = year
        self.month = month
        self.day = day
        self.year_jc = year_jc
        self.month_jc = month_jc
        self.day_jc = day_jc

    @staticmethod
    def _validate(year, month, day):
        """Check date triplet for validity.
        """
        if day is not None and month is None:
            raise ValueError("Day without month")
        if day is None:
            day = 1
        if month is None:
            month = 1
        if year is None:
            year = 2000
        # actual validation happens here
        datetime.date(year, month, day)

    @classmethod
    def _fmtDate(cls, date, fmt, sep):
        idx = cls._ymd_index[fmt]
        t = [None, None, None]
        t[idx[0]] = "%04d" % date[0]
        if date[1]:
            t[idx[1]] = "%02d" % date[1]
        if date[2]:
            t[idx[2]] = "%02d" % date[2]
        return sep.join([x for x in t if x is not None])

    def fmt(self, fmt, sep):
        """Make string representation.

        Parameters
        ----------
        fmt : str
            One of 'YMD', 'MDY', or 'DMY'.
        sep : str
            Separator character, can be anything.
        """
        date = (self.year, self.month, self.day)
        res = self._fmtDate(date, fmt, sep)
        if self.year_jc or self.month_jc or self.day_jc:
            date = (self.year_jc, self.month_jc, self.day_jc)
            res += " ({0} JC)".format(self._fmtDate(date, fmt, sep))
        return res

    def __str__(self):
        """Default date formatting in DD.MM.YYYY format.
        """
        return self.fmt('DMY', '.')

    def __cmp__(self, other):
        """Compare two dates
        """
        tup1 = (self.year, self.month, self.day)
        tup2 = (other.year, other.month, other.day)
        return cmp(tup1, tup2)


class DateString(object):
    """Class representing a date or few dates together with formatting
    information.

    Note: do not instantiate DateString objects directly, use `parse()` method instead.

    This class is an internal representation of the date strings which can
    contain one or more dates plus some textual info. As an example the input
    may have date strings like "Around 05.12.1961" or "From 1991 to 2002".
    `parse()` method below will parse these strings and extract dates from them
    and replace input string with format string which may look like
    "From {0} to {1}" and will construct DateString instance from all of that info.

    Data instances can be compared, the first date in the input string used for
    comparisons. They can also be formatted using `fmt()` method, the original
    string is recreated, but the date format may be changed.

    Parameters
    ----------
    dates : list of `Date` or None
        If `tuples` is None then "no-date" object is constructed.
        List can contain one or two tuples, each tuple can have 3 or 6
        numbers. First element of tuple is year, second is month, third is day.
        If tuple contains six elements then elements 4-6 specify Julian date.
    dstr : str
        Format string, e.g. "from {0} to {1}", number of substitution must
        be equal to number of tuples in the list.
    """

    def __init__(self, dates, dstr):
        self.dates = dates
        self.dstr = dstr

    def __cmp__(self, other):
        d1 = self.dates[0] if self.dates else Date()
        d2 = other.dates[0] if other.dates else Date()
        return cmp(d1, d2)

    def __nonzero__(self):
        return self.dates is not None

    def __str__(self):
        """Default date formatting in DD.MM.YYYY format.
        """
        return self.fmt('DMY', '.')

    def fmt(self, fmt, sep):
        if self.dates is None:
            return ""
        return self.dstr.format(*[dt.fmt(fmt, sep) for dt in self.dates])


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



def parse(datestr, fmt):
    '''Parse date string.

    Date string can contain arbitrary text with one or few dates
    (like "From 01.01.1967 to 01.01.1968").

    General date format is either an empty string (for no-date) or
    one to three components separated by separators (one of .-/). Each
    component is a number optionally followed by another number in
    parentheses (for Julian dates). Order of the components is defined by
    `fmt` string.

    Parameters
    ----------
    datestr : `str`
        String with dates and text
    fmt : `str`
        One of:
        'YMD' - for year/month/day order, if string has two components then
                it will be year/month
        'DMY' - for day/month/year order, if string has two components then
                it will be month/year
        'MDY' - for month/day/year order, if string has two components then
                it will be month/year
        If date string has just a single component it is always year.

    Raises
    ------
    Ranges for months and days are checked, if they are not in valid range
    then exception is thrown.

    Returns
    -------
    DateString object
    '''

    # _log.debug("date.parse: datestr=%s fmt=%s", datestr, fmt)

    if not datestr:
        return DateString(None, None)

    fstr = datestr

    tuples = []


    count = 0
    while True:

        # find next date
        day = True
        match = _date_re_ymd.search(fstr)
        if match and fmt[0] != 'Y':
            raise ValueError('Date string in incorrect order, fstr="{0}" fmt={1}'.format(fstr, fmt))
        if not match:
            match = _date_re_dmy.search(fstr)
            if match and fmt[0] == 'Y':
                raise ValueError('Date string in incorrect order, fstr="{0}" fmt={1}'.format(fstr, fmt))
        if not match:
            day = False
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
        gd = match.groupdict()

        items = [gd.get(k) for k in ('year', 'mon', 'day', 'year_jc', 'mon_jc', 'day_jc')]
        y, m, d, yjc, mjc, djc = [int(item) if item is not None else None for item in items]

        # MDY is DMY with swapped MD (only if day was present in match)
        if fmt == 'MDY' and day:
            m, d = d, m
            mjc, djc = djc, mjc

        if yjc or mjc or djc:
            if yjc is None:
                yjc = y
            if mjc is None:
                mjc = m
            if djc is None:
                djc = d
            dt = Date(y, m, d, yjc, mjc, djc)
        else:
            dt = Date(y, m, d)

        tuples.append(dt)
        fstr = fstr[:match.start()] + "{" + str(count) + "}" + fstr[match.end():]
        count += 1

    d = DateString(tuples, fstr)
    # _log.debug("date.parse: date=%s", d)
    return d


def guessFormat(dates):
    '''Guesses format of the date strings.

    Parameters
    ----------
    dates : list of strings

    Returns
    -------
    One of the YMD, DMY, or MDY constants.
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
