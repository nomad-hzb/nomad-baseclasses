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
from nomad.datamodel.data import ArchiveSection
from nomad.datamodel.metainfo.plot import PlotlyFigure, PlotSection
from nomad.metainfo import Quantity, SubSection
from scipy.optimize import curve_fit

from baseclasses.helper.plotly_plots import make_xas_plot

from .. import BaseMeasurement


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


class SiliconDriftDetector(PlotSection, ArchiveSection):
    fluo = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
    )
    icr = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        description='Incoming Count Rate',
    )
    ocr = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        description='Outgoing Count Rate',
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
        description='Real Time',
    )
    slope = Quantity(
        type=np.dtype(np.float64),
        description='slope=A*k for fit of OCR = A * (1 - exp(-k * ICR))',
    )
    fluo_dead_time_corrected = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        description='fluo_dead_time_corrected = fluo * slope * ICR/OCR',
    )
    fluo_tlt = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        description='fluo_tlt = fluo_dead_time_corrected / TLT',
    )
    fluo_tlt_result = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        description='fluo_tlt_result = fluo_tlt / k0',
    )

    def normalize(self, archive, logger, k0):
        super().normalize(archive, logger)
        if self.fluo is not None and self.icr is not None and self.ocr is not None:

            def exp_func(icr, a, k):
                return a * (1 - np.exp(-k * icr))

            # estimate starting values
            a0 = self.ocr.max()
            k0 = 1e-5
            try:
                params, _ = curve_fit(
                    exp_func, self.icr, self.ocr, p0=(a0, k0), maxfev=10000
                )
                a_fit, k_fit = params
            except Exception:
                a_fit, k_fit = (1, 1)

            self.slope = a_fit * k_fit
            self.fluo_dead_time_corrected = (
                self.fluo
                * self.slope
                * self.icr
                / np.where(self.ocr == 0, np.nan, self.ocr)
            )
            self.fluo_tlt = self.fluo_dead_time_corrected / self.tlt
            self.fluo_tlt_result = self.fluo_tlt / k0
        fig1 = make_xas_plot('OCR/ICR', self.ocr, 'ICR', [self.icr], 'OCR')
        self.figures = [
            PlotlyFigure(label='OCR vs ICR Plot', figure=json.loads(fig1.to_json())),
        ]


class XASWithSDD(XAS, PlotSection):
    sdd_parameters = SubSection(section_def=SiliconDriftDetector, repeats=True)

    manual_energy_shift = Quantity(
        type=np.dtype(np.float64),
        description='manual energy shift',
        unit='keV',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='keV'),
    )

    def normalize(self, archive, logger):
        self.method = 'XAS Fluoresence'
        for detector in self.sdd_parameters:
            detector.normalize(archive, logger, self.k0)
        super().normalize(archive, logger)
        fluo_result_list = [sdd.get('fluo_tlt_result') for sdd in self.sdd_parameters]
        fig1 = make_xas_plot(
            'Absorption of Sample (FluoResult/k0)',
            self.energy,
            'Energy',
            fluo_result_list,
            'Fluo corrected',
        )
        self.figures = [
            PlotlyFigure(
                label='Sample Absorbance Plot', figure=json.loads(fig1.to_json())
            ),
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
