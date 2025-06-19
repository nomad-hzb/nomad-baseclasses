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

import json
import numpy as np

from nomad.metainfo import Quantity, SubSection

from .. import BaseMeasurement
from nomad.datamodel.data import ArchiveSection
from nomad.datamodel.metainfo.plot import PlotlyFigure, PlotSection

from baseclasses.helper.plotly_plots import make_xas_plot


class XAS(BaseMeasurement):
    """XAS Measurement"""

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'),
    )

    energy = Quantity(type=np.dtype(np.float64), shape=['*'], unit='keV')

    seconds = Quantity(
        type=np.dtype(np.float64),
        unit='s',
        shape=['*'],
        a_plot=[
            {
                'x': 'energy',
                'y': 'seconds',
                'layout': {
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
            }
        ],
    )

    k0 = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        a_plot=[
            {
                'x': 'energy',
                'y': 'k0',
                'layout': {
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
            }
        ],
    )

    k1 = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        a_plot=[
            {
                'x': 'energy',
                'y': 'k1',
                'layout': {
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
            }
        ],
    )

    k3 = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        a_plot=[
            {
                'x': 'energy',
                'y': 'k3',
                'layout': {
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
            }
        ],
    )

    def normalize(self, archive, logger):
        super().normalize(archive, logger)


class KMC3Detector(PlotSection, ArchiveSection):
    fluo = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
    )
    icr = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        description='Input Count Rate',
    )
    ocr = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        description='Output Count Rate',
    )
    tlt = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        description='Trigger Life Time',
    )
    lt = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        description='Life Time',
    )
    rt = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        description='Real Life Time',
    )
    fluo_dead_time_corrected = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
    )

    def normalize(self, archive, logger):
        super().normalize(archive, logger)
        # TODO use slope in dead time correction
        if self.fluo is not None and self.icr is not None and self.ocr is not None:
            self.fluo_dead_time_corrected = self.fluo * self.icr / np.where(self.ocr == 0, np.nan, self.ocr)
        fig1 = make_xas_plot('ICR/OCR', self.ocr, 'OCR', [self.icr], 'ICR')
        self.figures = [
            PlotlyFigure(label='ICR/OCR Plot', figure=json.loads(fig1.to_json())),
        ]



class XASKMC3(XAS, PlotSection):
    k00 = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        a_plot=[
            {
                'x': 'energy',
                'y': 'k0',
                'layout': {
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
            }
        ],
    )

    sdd_parameters = SubSection(section_def=KMC3Detector, repeats=True)

    def normalize(self, archive, logger):
        self.method = 'XAS Fluoresence'
        for detector in self.sdd_parameters:
            detector.normalize(archive, logger)
        super().normalize(archive, logger)
        icr_list = [sdd.get('icr') for sdd in self.sdd_parameters]
        ocr_list = [sdd.get('icr') for sdd in self.sdd_parameters]
        fig1 = make_xas_plot('Input Count Rate (ICR)', self.energy, 'Energy', icr_list, 'ICR')
        fig2 = make_xas_plot('Output Count Rate (OCR)', self.energy, 'Energy', ocr_list, 'OCR')
        self.figures = [
            PlotlyFigure(label='ICR Plot', figure=json.loads(fig1.to_json())),
            PlotlyFigure(label='OCR Plot', figure=json.loads(fig2.to_json())),
        ]


class XASFluorescence(XAS):
    absorbance_of_the_reference = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        a_plot=[
            {
                'x': 'energy',
                'y': 'absorbance_of_the_reference',
                'layout': {
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
            }
        ],
    )

    fluorescence_yield = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        a_plot=[
            {
                'x': 'energy',
                'y': 'fluorescence_yield',
                'layout': {
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
            }
        ],
    )

    def normalize(self, archive, logger):
        self.method = 'XAS Fluoresence'
        super().normalize(archive, logger)

        if self.k1 is not None and self.k0 is not None:
            self.absorbance_of_the_reference = -np.log(self.k1 / self.k0)

        if self.k3 is not None and self.k0 is not None:
            self.fluorescence_yield = self.k3 / self.k0


class XASTransmission(XAS):
    absorbance_of_the_reference = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        a_plot=[
            {
                'x': 'energy',
                'y': 'absorbance_of_the_reference',
                'layout': {
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
            }
        ],
    )

    absorbance_of_the_sample = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        a_plot=[
            {
                'x': 'energy',
                'y': 'absorbance_of_the_sample',
                'layout': {
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
            }
        ],
    )

    def normalize(self, archive, logger):
        self.method = 'XAS Transmission'
        super().normalize(archive, logger)

        if self.k1 is not None and self.k0 is not None:
            self.absorbance_of_the_sample = -np.log(self.k1 / self.k0)

        if self.k1 is not None and self.k0 is not None:
            self.absorbance_of_the_reference = -np.log(self.k3 / self.k1)
