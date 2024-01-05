import numpy as np

from nomad.datamodel.data import ArchiveSection

from nomad.metainfo import (
    Quantity)


class DataWithStatistics(ArchiveSection):
    mean = Quantity(
        type=np.dtype(np.float64))

    variance = Quantity(
        type=np.dtype(np.float64))

    minimum = Quantity(
        type=np.dtype(np.float64))

    maximum = Quantity(
        type=np.dtype(np.float64))

    data = Quantity(
        type=np.dtype(np.float64),
        shape=['*'])

    def normalize(self, archive, logger):
        self.mean = np.mean(self.data)
        self.minimum = np.min(self.data)
        self.maximum = np.max(self.data)
        self.variance = np.var(self.data)
