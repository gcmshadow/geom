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

__all__ = ["IntervalI"]

import numpy as np

from lsst.utils import continueClass
from ._geom import IntervalI


@continueClass  # noqa: F811 (FIXME: remove for py 3.8+)
class IntervalI:  # noqa: F811

    def range(self):
        """Return a `range` object containing all points in the interval.

        Returns
        -------
        range : `range`
            Range instance that can be used to iterate over all points in the
            interval.
        """
        return range(self.begin, self.end)

    def arange(self, dtype=np.int32):
        """Return an array containing all points in the interval.

        Parameters
        ----------
        dtype : convertible to `numpy.dtype`
            The data type of the returned arrays.

        Returns
        -------
        points : `numpy.ndarray`
            1-d array with `size == self.size` containing points.
        """
        return np.arange(self.begin, self.end, 1, dtype=dtype)

    def slice(self):
        """Return a `slice` object corresponding to the interval's points.

        Returns
        -------
        slice : `slice`
            Slice instance that can be used to select the elements of a
            container that correspond to the points in the interval.
        """
        return slice(self.begin, self.end, None)
