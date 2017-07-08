"""Unit test for date module
"""

from __future__ import absolute_import, division, print_function

__all__ = ['TestDateClass', 'TestParse', 'TestGuessFormat']

import unittest

from .. import date


class TestDateClass(unittest.TestCase):

    def test_1_nodate(self):

        d = date.Date()
        self.assertIsNone(d.year)
        self.assertIsNone(d.month)
        self.assertIsNone(d.day)
        self.assertIsNone(d.year_jc)
        self.assertIsNone(d.month_jc)
        self.assertIsNone(d.day_jc)

    def test_2_simple(self):

        d = date.Date(2000, 12, 31)
        self.assertEqual(d.year, 2000)
        self.assertEqual(d.month, 12)
        self.assertEqual(d.day, 31)
        self.assertIsNone(d.year_jc)
        self.assertIsNone(d.month_jc)
        self.assertIsNone(d.day_jc)
        self.assertEqual(str(d), "31.12.2000")
        self.assertEqual(d.fmt(date.YMD, '-'), "2000-12-31")
        self.assertEqual(d.fmt(date.MDY, '/'), "12/31/2000")
        self.assertEqual(d.fmt(date.DMY, '.'), "31.12.2000")

    def test_4_julian(self):

        d = date.Date(2000, 12, 31, 2000, 12, 17)
        self.assertEqual(d.year, 2000)
        self.assertEqual(d.month, 12)
        self.assertEqual(d.day, 31)
        self.assertEqual(d.year_jc, 2000)
        self.assertEqual(d.month_jc, 12)
        self.assertEqual(d.day_jc, 17)
        self.assertEqual(str(d), "31.12.2000 (17.12.2000 JC)")
        self.assertEqual(d.fmt(date.YMD, '-'), "2000-12-31 (2000-12-17 JC)")
        self.assertEqual(d.fmt(date.MDY, '/'), "12/31/2000 (12/17/2000 JC)")
        self.assertEqual(d.fmt(date.DMY, '.'), "31.12.2000 (17.12.2000 JC)")

    def test_5_cmp(self):

        d1 = date.Date(2000, 12, 31)
        d2 = date.Date(2026, 6, 6)
        self.assertGreater(d2, d1)
        self.assertLess(d1, d2)
        self.assertGreaterEqual(d2, d1)
        self.assertLessEqual(d1, d2)
        self.assertEqual(d1, d1)
        self.assertEqual(d2, d2)
        self.assertLessEqual(d1, d1)
        self.assertGreaterEqual(d1, d1)

    def test_6_invalid(self):

        with self.assertRaises(ValueError):
            d1 = date.Date(2000, 12, 32)
        with self.assertRaises(ValueError):
            d1 = date.Date(2000, 12, -1)
        with self.assertRaises(ValueError):
            d1 = date.Date(2000, 13, 1)
        with self.assertRaises(ValueError):
            d1 = date.Date(2000, 0, 1)
        with self.assertRaises(ValueError):
            d1 = date.Date(2000, None, 1)
        with self.assertRaises(ValueError):
            d1 = date.Date(2000, 1, 1, 1999, 12, 32)
        with self.assertRaises(ValueError):
            d1 = date.Date(2000, 1, 1, 1999, 0, 1)


class TestDateStringClass(unittest.TestCase):

    def test_1_nodate(self):

        d = date.DateString(None, None)
        self.assertIsNone(d.dates)
        # in boolean context it evaluates to False
        self.assertFalse(d)
        self.assertEqual(str(d), "")

    def test_2_simple(self):

        d = date.Date(2000, 12, 31)
        d = date.DateString([d], "{0}")
        self.assertEqual(len(d.dates), 1)
        # in boolean context it evaluates to True
        self.assertTrue(d)
        self.assertEqual(str(d), "31.12.2000")
        self.assertEqual(d.fmt(date.YMD, '-'), "2000-12-31")
        self.assertEqual(d.fmt(date.MDY, '/'), "12/31/2000")
        self.assertEqual(d.fmt(date.DMY, '.'), "31.12.2000")

    def test_3_multi(self):

        d = [date.Date(2000, 12, 31), date.Date(2001, 1, 1)]
        d = date.DateString(d, "between {0} and {1}")
        self.assertEqual(len(d.dates), 2)
        self.assertTrue(d)
        self.assertEqual(str(d), "between 31.12.2000 and 01.01.2001")
        self.assertEqual(d.fmt(date.YMD, '-'), "between 2000-12-31 and 2001-01-01")
        self.assertEqual(d.fmt(date.MDY, '/'), "between 12/31/2000 and 01/01/2001")
        self.assertEqual(d.fmt(date.DMY, '.'), "between 31.12.2000 and 01.01.2001")

    def test_4_julian(self):

        d = date.Date(2000, 12, 31, 2000, 12, 17)
        d = date.DateString([d], "{0}")
        self.assertEqual(len(d.dates), 1)
        # in boolean context it evaluates to True
        self.assertTrue(d)
        self.assertEqual(str(d), "31.12.2000 (17.12.2000 JC)")
        self.assertEqual(d.fmt(date.YMD, '-'), "2000-12-31 (2000-12-17 JC)")
        self.assertEqual(d.fmt(date.MDY, '/'), "12/31/2000 (12/17/2000 JC)")
        self.assertEqual(d.fmt(date.DMY, '.'), "31.12.2000 (17.12.2000 JC)")

    def test_5_cmp(self):

        d1 = date.DateString([date.Date(2000, 12, 31)], "{0}")
        d2 = date.DateString([date.Date(2026, 6, 6)], "{0}")
        self.assertGreater(d2, d1)
        self.assertLess(d1, d2)
        self.assertGreaterEqual(d2, d1)
        self.assertLessEqual(d1, d2)
        self.assertEqual(d1, d1)
        self.assertEqual(d2, d2)
        self.assertLessEqual(d1, d1)
        self.assertGreaterEqual(d1, d1)

    def test_6_partial(self):

        d = date.DateString([date.Date(2000, 12)], "{0}")
        self.assertEqual(len(d.dates), 1)
        self.assertEqual(str(d), "12.2000")

        d = date.DateString([date.Date(2000)], "{0}")
        self.assertEqual(len(d.dates), 1)
        self.assertEqual(str(d), "2000")


class TestParse(unittest.TestCase):

    def test_1_nodate(self):

        d = date.parse("", date.YMD)
        self.assertIsNone(d.dates)
        self.assertFalse(d)
        self.assertEqual(str(d), "")

        d = date.parse("no date", date.YMD)
        self.assertEqual(len(d.dates), 0)
        self.assertEqual(str(d), "no date")


    def test_2_simple(self):

        d = date.parse("2000.12.31", date.YMD)
        self.assertEqual(str(d), "31.12.2000")

        d = date.parse("12.31.2000", date.MDY)
        self.assertEqual(str(d), "31.12.2000")

        d = date.parse("31.12.2000", date.DMY)
        self.assertEqual(str(d), "31.12.2000")

        with self.assertRaises(ValueError):
            d = date.parse("2000.12.31", date.MDY)
        with self.assertRaises(ValueError):
            d = date.parse("2000.12.31", date.DMY)

        # year and month
        d = date.parse("2000.12", date.YMD)
        self.assertEqual(str(d), "12.2000")
        d = date.parse("12.2000", date.MDY)
        self.assertEqual(str(d), "12.2000")
        d = date.parse("12.2000", date.DMY)
        self.assertEqual(str(d), "12.2000")

        with self.assertRaises(ValueError):
            d = date.parse("2000.12", date.MDY)
        with self.assertRaises(ValueError):
            d = date.parse("2000.12", date.DMY)

        # year only
        d = date.parse("2000", date.YMD)
        self.assertEqual(str(d), "2000")
        d = date.parse("2000", date.MDY)
        self.assertEqual(str(d), "2000")
        d = date.parse("2000", date.DMY)
        self.assertEqual(str(d), "2000")

    def test_3_separators(self):

        d = date.parse("2000.12.31", date.YMD)
        self.assertEqual(str(d), "31.12.2000")

        d = date.parse("2000-12-31", date.YMD)
        self.assertEqual(str(d), "31.12.2000")

        d = date.parse("2000/12/31", date.YMD)
        self.assertEqual(str(d), "31.12.2000")

    def test_4_validate(self):

        with self.assertRaises(ValueError):
            d = date.parse("2000.13.31", date.YMD)
        with self.assertRaises(ValueError):
            d = date.parse("2000.12.32", date.YMD)
        with self.assertRaises(ValueError):
            d = date.parse("2000.13", date.YMD)

        with self.assertRaises(ValueError):
            d = date.parse("13.31.2000", date.MDY)
        with self.assertRaises(ValueError):
            d = date.parse("12.32.2000", date.MDY)
        with self.assertRaises(ValueError):
            d = date.parse("13.2000", date.MDY)

        with self.assertRaises(ValueError):
            d = date.parse("31.13.2000", date.DMY)
        with self.assertRaises(ValueError):
            d = date.parse("32.12.2000", date.DMY)
        with self.assertRaises(ValueError):
            d = date.parse("13.2000", date.DMY)


class TestGuessFormat(unittest.TestCase):

    def test_1_ymd(self):

        # days are all in range 1-12
        dates = ["1812.01.02", "1917.02.03", "2038/04", "2012"]
        self.assertEqual(date.guessFormat(dates), date.YMD)

        # dates are in range 1-31
        dates = ["1812.01.20", "1917.02.28", "2038-04"]
        self.assertEqual(date.guessFormat(dates), date.YMD)

        # months only
        dates = ["1812.01", "1917.02", "2038/04"]
        self.assertEqual(date.guessFormat(dates), date.YMD)

    def test_2_mdy(self):

        # day must be beyond 12 to disambiguate with DMY
        dates = ["01.02.1812", "02.23.1917", "04/2038"]
        self.assertEqual(date.guessFormat(dates), date.MDY)

    def test_3_dmy(self):

        # day must be beyond 12 to disambiguate with MDY
        dates = ["01.02.1812", "23.02.1917", "04/2038"]
        self.assertEqual(date.guessFormat(dates), date.DMY)

    def test_4_failures(self):

        # year only is ambiguous
        dates = ["1812", "1917", "2038"]
        with self.assertRaises(ValueError):
            date.guessFormat(dates)

        # have to have three components in MDY or DMY
        dates = ["02/1812", "13.1917", "2038"]
        with self.assertRaises(ValueError):
            date.guessFormat(dates)

        # date must be >12 to disambiguate DMY from MDY
        dates = ["01/02/1812"]
        with self.assertRaises(ValueError):
            date.guessFormat(dates)

        # invalid day
        dates = ["1812.12.32"]
        with self.assertRaises(ValueError):
            date.guessFormat(dates)

        # invalid month
        dates = ["1812.13.01"]
        with self.assertRaises(ValueError):
            date.guessFormat(dates)

        # invalid day/month
        dates = ["13.13.1812"]
        with self.assertRaises(ValueError):
            date.guessFormat(dates)

        # just some nonsense
        dates = ["not-a-date"]
        with self.assertRaises(ValueError):
            date.guessFormat(dates)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDateClass)
    unittest.TextTestRunner(verbosity=2).run(suite)
