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


class InfraredSpectroscopy(BaseMeasurement):

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    absorbance = Quantity(
        type=np.dtype(
            np.float64),
        shape=['n_values'],
        a_plot=[
            {
                "label": "Absorbance",
                'x': 'wave_number',
                'y': 'absorbance',
                'layout': {
                    'yaxis': {
                        'type': 'lin',
                        "title": "Absorbance"}},
                "config": {
                    "editable": True,
                    "scrollZoom": True}}])

    wave_number = Quantity(
        type=np.dtype(
            np.float64),
        shape=['n_values'],
        unit='1/cm',
        a_plot=[
            {
                "label": "Absorbance",
                'x': 'wave_number',
                'y': 'absorbance',
                'layout': {
                    'yaxis': {
                        'type': 'lin',
                        "title": "Absorbance"}},
                "config": {
                    "editable": True,
                    "scrollZoom": True}}])

    def derive_n_values(self):
        if self.absorbance or self.wave_number:
            return max(len(self.absorbance), len(self.wave_number))
        return 0

    n_values = Quantity(type=int, derived=derive_n_values)

    def normalize(self, archive, logger):
        super().normalize(archive, logger)
        self.method = "Infrared Spectroscopy"

        if self.data_file and os.path.splitext(self.data_file)[-1] == ".DAT":
            try:
                import pandas as pd
                with archive.m_context.raw_file(self.data_file) as f:
                    data = pd.read_csv(f.name, sep=" ", header=None)
                    self.absorbance = data[1]
                    self.wave_number = data[0]

            except Exception as e:
                logger.error(e)
