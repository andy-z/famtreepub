"""Unit test for utils module
"""

from __future__ import absolute_import, division, print_function

__all__ = ['TestResize']

import unittest

from .. import utils

class TestResize(unittest.TestCase):

    def test_1_reduceonly(self):

        bound = (10, 10)

        box = (1, 1)
        resized = utils.resize(box, bound, reduce_only=True)
        self.assertEqual(resized, box)

        box = (100, 100)
        resized = utils.resize(box, bound, reduce_only=True)
        self.assertEqual(resized, bound)

        box = (1, 100)
        resized = utils.resize(box, bound, reduce_only=True)
        self.assertEqual(resized, (0.1, 10))

        box = (100, 1)
        resized = utils.resize(box, bound, reduce_only=True)
        self.assertEqual(resized, (10, .1))

    def test_2(self):

        bound = (10, 10)

        box = (1, 1)
        resized = utils.resize(box, bound, reduce_only=False)
        self.assertEqual(resized, bound)

        box = (100, 100)
        resized = utils.resize(box, bound, reduce_only=False)
        self.assertEqual(resized, bound)

        box = (1, 2)
        resized = utils.resize(box, bound, reduce_only=False)
        self.assertEqual(resized, (5, 10))

        box = (2, 1)
        resized = utils.resize(box, bound, reduce_only=False)
        self.assertEqual(resized, (10, 5))


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestResize)
    unittest.TextTestRunner(verbosity=2).run(suite)
