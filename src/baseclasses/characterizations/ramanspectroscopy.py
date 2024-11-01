#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os

import numpy as np
from nomad.metainfo import Quantity

from .. import BaseMeasurement


class Raman(BaseMeasurement):

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    minimal_height = Quantity(
        type=np.dtype(
            np.float64),
        a_eln=dict(
            component='NumberEditQuantity'))

    intensity = Quantity(
        type=np.dtype(np.float64),
        shape=['n_values'],
        a_plot=[
            {
                'label': 'Intensity',
                'x': 'raman_shift',
                'y': 'intensity',
                'layout': {'yaxis': {'type': 'lin', "title": "Intensity"}},
                "config": {
                    "editable": True,
                    "scrollZoom": True
                }
            }])

    raman_shift = Quantity(
        type=np.dtype(np.float64),
        shape=['n_values'],
        unit='1/cm',
        a_plot=[
            {
                'label': 'Intensity',
                'x': 'raman_shift',
                'y': 'intensity',
                'layout': {'yaxis': {'type': 'lin', "title": "Intensity"}},
                "config": {
                    "editable": True,
                    "scrollZoom": True
                }
            }])

    peaks_raman = Quantity(
        type=np.dtype(np.float64),
        unit='1/cm',
        shape=['*'],
    )

    peaks_intensity = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
    )

    def derive_n_values(self):
        if self.intensity or self.raman_shift:
            return max(len(self.intensity), len(self.raman_shift))
        return 0

    n_values = Quantity(type=int, derived=derive_n_values)

    def normalize(self, archive, logger):
        super().normalize(archive, logger)
        self.method = "Raman Spectroscopy"

        if self.data_file and os.path.splitext(self.data_file)[-1] == ".txt":
            try:
                import pandas as pd
                from scipy import signal
                with archive.m_context.raw_file(self.data_file) as f:
                    data = pd.read_csv(f.name, sep="\t", header=None)
                    self.intensity = data[1]
                    self.raman_shift = data[0]
                    height = self.minimal_height if self.minimal_height else 40
                    peaks, _ = signal.find_peaks(self.intensity, height=height)

                    self.peaks_raman = self.raman_shift[peaks]
                    self.peaks_intensity = self.intensity[peaks]

            except Exception as e:
                logger.error(e)
