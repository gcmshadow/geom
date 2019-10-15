#
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
from __future__ import annotations

import unittest
import itertools
from typing import ClassVar

import numpy as np

import lsst.utils.tests
from lsst.pex.exceptions import InvalidParameterError
from lsst.geom import IntervalI, IntervalD


class IntervalTestData:
    """Test helper that constructs and organizes intervals to be tested.

    Parameters
    ----------
    IntervalClass : `type`
        Type object that specifies the interval class to be tested (either
        `IntervalI` or `IntervalD`).
    points : `list`
        List of scalar values to use as endpoints, sorted from smallest to
        largest.
    n : `int`, optional
        If not `None`, the number of intervals to retain in each category
        (a random subset).
    """

    def __init__(self, IntervalClass, points, n=None):
        self.concrete = []
        self.infinite = []
        self.empty = [IntervalClass()]
        for i, lhs in enumerate(points):
            for j, rhs in enumerate(points):
                if np.isfinite(lhs) and np.isfinite(rhs):
                    if i < j:
                        self.concrete.append(IntervalClass(min=lhs, max=rhs))
                    elif i > j:
                        self.empty.append(IntervalClass(min=lhs, max=rhs))
                    else:
                        assert i == j
                        self.concrete.append(IntervalClass(min=lhs, max=rhs))
                else:
                    if i < j:
                        self.infinite.append(IntervalClass(min=lhs, max=rhs))
                    elif i > j:
                        self.empty.append(IntervalClass(min=lhs, max=rhs))
        if n is not None:
            self.concrete = self.subset(self.concrete, n)
            self.infinite = self.subset(self.infinite, n)
            self.empty = self.subset(self.empty, n)

    @staticmethod
    def subset(seq, n):
        """Return `n` random elements from the given sequence.
        """
        if len(seq) > n:
            return [seq[i] for i in np.random.choice(len(seq), n)]
        return seq

    @property
    def nonempty(self):
        """Iterate over all test intervals that are not empty.
        """
        return itertools.chain(self.concrete, self.infinite)

    @property
    def finite(self):
        """Iterate over all test intervals that have finite size.
        """
        return itertools.chain(self.concrete, self.empty)

    @property
    def all(self):
        """Iterate over all test intervals.
        """
        return itertools.chain(self.concrete, self.infinite, self.empty)


class IntervalTests:
    """Base class that provides common tests for IntervalI and IntervalD.
    """

    IntervalClass: ClassVar[type]
    """Interval class object to be tested.

    Subclasses must define this as a class attribute.
    """

    intervals: IntervalTestData
    """Example intervals to be tested, categorized.

    Subclasses must define this, typically as an instance attribute during
    `setUp`.
    """

    points: list
    """List of points to use when testing interval operations that take
    scalars of the appropriate type.

    These points must be finite.

    Subclasses must define this, typically as an instance attribute during
    `setUp`.
    """

    nonfinitePoints: list
    """Additional points representing non-finite values.

    Subclasses must define this, typically as an instance attribute during
    `setUp`.  An empty list should be used for intervals whose bound type does
    not support non-finite values.
    """

    def assertAllTrue(self, iterable):
        seq = list(iterable)
        self.assertEqual(seq, [True]*len(seq))

    def assertAllFalse(self, iterable):
        seq = list(iterable)
        self.assertEqual(seq, [False]*len(seq))

    def testEmpty(self):
        self.assertTrue(self.IntervalClass().isEmpty())
        self.assertAllFalse(s.isEmpty() for s in self.intervals.nonempty)
        for interval in self.intervals.empty:
            with self.subTest(interval=interval):
                self.checkEmptyIntervalInvariants(interval)

    def testConstructors(self):
        for i in self.intervals.finite:
            with self.subTest(i=i):
                self.assertEqual(i, self.IntervalClass(min=i.min, max=i.max))
                self.assertEqual(i, self.IntervalClass(min=i.min, size=i.size))
                self.assertEqual(i, self.IntervalClass(max=i.max, size=i.size))
        for i in self.intervals.infinite:
            with self.subTest(i=i):
                self.assertEqual(i, self.IntervalClass(min=i.min, max=i.max))
            with self.assertRaises(InvalidParameterError):
                self.IntervalClass(min=i.min, size=i.size)
            with self.assertRaises(InvalidParameterError):
                self.IntervalClass(max=i.max, size=i.size)

    def testContains(self):
        for lhs in self.intervals.nonempty:
            for rhs in self.intervals.nonempty:
                with self.subTest(lhs=lhs, rhs=rhs):
                    self.assertEqual(lhs.contains(rhs), lhs.min <= rhs.min and lhs.max >= rhs.max)
            for rhs in self.intervals.empty:
                with self.subTest(lhs=lhs, rhs=rhs):
                    self.assertTrue(lhs.contains(rhs))
            for rhs in self.points:
                with self.subTest(lhs=lhs, rhs=rhs):
                    self.assertEqual(lhs.contains(rhs), lhs.min <= rhs and lhs.max >= rhs)
        for lhs in self.intervals.empty:
            for rhs in self.intervals.nonempty:
                with self.subTest(lhs=lhs, rhs=rhs):
                    self.assertFalse(lhs.contains(rhs))
            for rhs in self.intervals.empty:
                with self.subTest(lhs=lhs, rhs=rhs):
                    self.assertTrue(lhs.contains(rhs))
            for rhs in self.points:
                with self.subTest(lhs=lhs, rhs=rhs):
                    self.assertFalse(lhs.contains(rhs))

    def testOverlaps(self):
        for lhs in self.intervals.nonempty:
            for rhs in self.intervals.nonempty:
                with self.subTest(lhs=lhs, rhs=rhs):
                    self.assertEqual(lhs.overlaps(rhs),
                                     lhs.contains(rhs.min) or lhs.contains(rhs.max) or
                                     rhs.contains(lhs.min) or rhs.contains(lhs.max))
            for rhs in self.intervals.empty:
                with self.subTest(lhs=lhs, rhs=rhs):
                    self.assertFalse(lhs.overlaps(rhs))
        for lhs in self.intervals.empty:
            for rhs in self.intervals.all:
                with self.subTest(lhs=lhs, rhs=rhs):
                    self.assertFalse(lhs.overlaps(rhs))

    def testEquality(self):
        for lhs in self.intervals.all:
            for rhs in self.intervals.all:
                with self.subTest(lhs=lhs, rhs=rhs):
                    shouldBeEqual = lhs.contains(rhs) and rhs.contains(lhs)
                    self.assertIs(lhs == rhs, shouldBeEqual)
                    self.assertIs(lhs != rhs, not shouldBeEqual)


class IntervalDTestCase(unittest.TestCase, IntervalTests):
    IntervalClass = IntervalD

    def setUp(self):
        inf = float("inf")
        self.points = [-1.5, 5.0, 6.75, 8.625]
        self.intervals = IntervalTestData(self.IntervalClass, [-inf] + self.points + [inf], n=3)
        self.nonfinitePoints = [np.nan, -np.inf, np.inf]

    def checkEmptyIntervalInvariants(self, interval):
        self.assertTrue(interval.isEmpty())
        self.assertEqual(interval.size, 0.0)
        self.assertTrue(np.isnan(interval.min))
        self.assertTrue(np.isnan(interval.max))

    def testBadConstruction(self):
        with self.assertRaises(InvalidParameterError):
            IntervalD(min=np.inf, max=np.inf)
        with self.assertRaises(InvalidParameterError):
            IntervalD(min=-np.inf, max=-np.inf)
        with self.assertRaises(InvalidParameterError):
            IntervalD(min=np.inf, size=2.0)
        with self.assertRaises(InvalidParameterError):
            IntervalD(max=-np.inf, size=2.0)

    def testCenter(self):
        for interval in self.intervals.concrete:
            self.assertEqual(interval.center, 0.5*(interval.min + interval.max))
        for i in self.intervals.finite:
            self.assertEqual(i, self.IntervalClass(center=i.center, size=i.size))

    def testInfinite(self):
        for interval in self.intervals.finite:
            with self.subTest(interval=interval):
                self.assertTrue(interval.isFinite())
                self.assertTrue(np.isfinite(interval.size))
        for interval in self.intervals.infinite:
            with self.subTest(interval=interval):
                self.assertFalse(interval.isEmpty())
                self.assertFalse(interval.isFinite())
                self.assertEqual(interval.size, np.inf)


class IntervalITestCase(unittest.TestCase, IntervalTests):
    IntervalClass = IntervalI

    def setUp(self):
        self.points = [-2, 4, 7, 11]
        self.intervals = IntervalTestData(self.IntervalClass, self.points, n=3)
        self.nonfinitePoints = []

    def checkEmptyIntervalInvariants(self, interval):
        self.assertTrue(interval.isEmpty())
        self.assertEqual(interval.size, 0.0)
        self.assertLess(interval.max, interval.min)
        # Actual values of min and max are unspecified; while implementation
        # tries to make them consistent, nothing (not even tests) should depend
        # on that.

    def testOverflow(self):
        # Small enough to fit in int32 without any problem at all.
        small = 1 << 16
        # Fits in int32, barely.
        medium = (1 << 31) - 1
        # Definitely doesn't fit in int32.
        large = 1 << 33
        # Pass in a too-large value for either min or max.
        # Just check for exception because pybind11 is actually what catches
        # this overflow case.
        with self.assertRaises(Exception):
            IntervalI(min=-small, max=large)
        with self.assertRaises(Exception):
            IntervalI(min=-large, max=small)
        # Pass two values that are individually okay, but together overflow
        # the size, min, or max.
        with self.assertRaises(OverflowError):
            IntervalI(min=-medium, max=medium)
        with self.assertRaises(OverflowError):
            IntervalI(min=2, size=medium)
        with self.assertRaises(OverflowError):
            IntervalI(max=-3, size=medium)


class MemoryTester(lsst.utils.tests.MemoryTestCase):
    pass


def setup_module(module):
    lsst.utils.tests.init()


if __name__ == "__main__":
    lsst.utils.tests.init()
    unittest.main()
