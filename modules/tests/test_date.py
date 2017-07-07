"""Unit test for date module
"""

from __future__ import absolute_import, division, print_function

__all__ = ['TestDateClass']

import unittest

from .. import date

class TestDateClass(unittest.TestCase):

    def test_1_nodate(self):

        d = date.Date(None, None)
        self.assertIsNone(d.tuples)
        # in boolean context it evaluates to False
        self.assertFalse(d)
        self.assertEqual(str(d), "")

    def test_2_simple(self):

        d = (2000, 12, 31)
        d = date.Date([d], "{0}")
        self.assertEqual(len(d.tuples), 1)
        # in boolean context it evaluates to True
        self.assertTrue(d)
        self.assertEqual(str(d), "31.12.2000")
        self.assertEqual(d.fmt(date.YMD, '-'), "2000-12-31")
        self.assertEqual(d.fmt(date.MDY, '/'), "12/31/2000")
        self.assertEqual(d.fmt(date.DMY, '.'), "31.12.2000")

    def test_3_multi(self):

        d = [(2000, 12, 31), (2001, 1, 1)]
        d = date.Date(d, "between {0} and {1}")
        self.assertEqual(len(d.tuples), 2)
        self.assertTrue(d)
        self.assertEqual(str(d), "between 31.12.2000 and 01.01.2001")
        self.assertEqual(d.fmt(date.YMD, '-'), "between 2000-12-31 and 2001-01-01")
        self.assertEqual(d.fmt(date.MDY, '/'), "between 12/31/2000 and 01/01/2001")
        self.assertEqual(d.fmt(date.DMY, '.'), "between 31.12.2000 and 01.01.2001")

    def test_4_julian(self):

        d = (2000, 12, 31, 2000, 12, 17)
        d = date.Date([d], "{0}")
        self.assertEqual(len(d.tuples), 1)
        # in boolean context it evaluates to True
        self.assertTrue(d)
        self.assertEqual(str(d), "31.12.2000 (17.12.2000 JC)")
        self.assertEqual(d.fmt(date.YMD, '-'), "2000-12-31 (2000-12-17 JC)")
        self.assertEqual(d.fmt(date.MDY, '/'), "12/31/2000 (12/17/2000 JC)")
        self.assertEqual(d.fmt(date.DMY, '.'), "31.12.2000 (17.12.2000 JC)")

    def test_5_cmp(self):

        d1 = date.Date([(2000, 12, 31)], "{0}")
        d2 = date.Date([(2026, 6, 6)], "{0}")
        self.assertGreater(d2, d1)
        self.assertLess(d1, d2)
        self.assertGreaterEqual(d2, d1)
        self.assertLessEqual(d1, d2)
        self.assertEqual(d1, d1)
        self.assertEqual(d2, d2)
        self.assertLessEqual(d1, d1)
        self.assertGreaterEqual(d1, d1)

    def test_6_partial(self):

        d = date.Date([(2000, 12, 0)], "{0}")
        self.assertEqual(len(d.tuples), 1)
        self.assertEqual(str(d), "12.2000")

        d = date.Date([(2000, 0, 0)], "{0}")
        self.assertEqual(len(d.tuples), 1)
        self.assertEqual(str(d), "2000")


class TestParse(unittest.TestCase):

    def test_1_nodate(self):

        d = date.parse("", date.YMD)
        self.assertIsNone(d.tuples)
        self.assertFalse(d)
        self.assertEqual(str(d), "")

        d = date.parse("no date", date.YMD)
        self.assertEqual(len(d.tuples), 0)
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

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDateClass)
    unittest.TextTestRunner(verbosity=2).run(suite)
