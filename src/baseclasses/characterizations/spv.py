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


class SPV(BaseMeasurement):
    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'),
    )

    energy = Quantity(
        type=np.dtype(np.float64),
        shape=['n_values'],
        unit='eV',
        a_plot=[
            {
                'label': 'Voltage',
                'x': 'energy',
                'y': 'volt',
                'layout': {'yaxis': {'type': 'lin', 'title': 'Voltage'}},
                'config': {'editable': True, 'scrollZoom': True},
            }
        ],
    )

    wavelength = Quantity(
        type=np.dtype(np.float64),
        shape=['n_values'],
        unit='nm',
        a_plot=[
            {
                'label': 'Voltage',
                'x': 'wavelength',
                'y': 'volt',
                'layout': {'yaxis': {'type': 'lin', 'title': 'Voltage'}},
                'config': {'editable': True, 'scrollZoom': True},
            }
        ],
    )

    volt = Quantity(
        type=np.dtype(np.float64),
        shape=['n_values'],
        unit='V',
        a_plot=[
            {
                'label': 'Voltage',
                'x': 'wavelength',
                'y': 'volt',
                'layout': {'yaxis': {'type': 'lin', 'title': 'Voltage'}},
                'config': {'editable': True, 'scrollZoom': True},
            }
        ],
    )

    def derive_n_values(self):
        if self.energy or self.wavelength or self.volt:
            return max(len(self.energy), len(self.wavelength), len(self.volt))
        return 0

    n_values = Quantity(type=int, derived=derive_n_values)

    def normalize(self, archive, logger):
        super().normalize(archive, logger)
        self.method = 'SPV'

        if self.data_file and os.path.splitext(self.data_file)[-1] == '.dat':
            try:
                import pandas as pd

                with archive.m_context.raw_file(self.data_file) as f:
                    data = pd.read_csv(f.name, sep='\t', header=2)
                    self.energy = np.array(data.iloc[:, 0])
                    self.wavelength = np.array(data.iloc[:, 1])
                    self.volt = np.array(data.iloc[:, 2])

            except Exception as e:
                logger.error(e)
