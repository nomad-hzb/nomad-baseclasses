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

    manual_energy_shift = Quantity(
        type=np.dtype(np.float64),
        description='User-applied offset to shift the measured X-ray photon energy scale, where positive values are added and negative values are subtracted, in order to align the spectrum with a known reference (e.g. absorption edge of a reference foil).',
        unit='keV',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='keV'),
    )

    # TODO add connected experiments and maybe redo description

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

    def normalize(self, archive, logger, k0=None):
        if k0 is None:  # needed for reprocessing
            return
        super().normalize(archive, logger)
        if self.fluo is not None and self.icr is not None and self.ocr is not None:

            def exp_func(icr, a, k):
                return a * (1 - np.exp(-k * icr))

            # estimate starting values
            a0 = self.ocr.max()
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

    quality_annotation = Quantity(
        type=str,
        description='Label for basic quality assessment of the measured values.',
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=['ICR out of bounds', 'ICR within specified bounds']),
        ),
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
            },
        ],
    )

    def normalize(self, archive, logger):
        super().normalize(archive, logger)
        for detector in self.sdd_parameters:
            detector.normalize(archive, logger, self.k0)

        if all(((0 <= sdd.get('icr')) & (sdd.get('icr') <= 250000)).all() for sdd in self.sdd_parameters):
            self.quality_annotation = 'ICR within specified bounds'
        else:
            self.quality_annotation = 'ICR out of bounds'
            return
            # TODO return here or just set the flag

        fluo_result_list = [sdd.get('fluo_tlt_result') for sdd in self.sdd_parameters]
        if self.absorbance_of_the_sample is None:
            if self.method == 'XAS Fluorescence' and fluo_result_list is not None:
                self.absorbance_of_the_sample = np.nanmean(fluo_result_list, axis=0)
            if self.method == 'XAS Transmission' and self.k1 is not None and self.k0 is not None:
                self.absorbance_of_the_sample = -np.log(self.k1 / self.k0)

        self.figures = []
        if self.sdd_parameters is not None:
            fig1 = make_xas_plot(
                'Absorbance of Sample (FluoResult of SDD channels)',
                self.energy,
                'Energy',
                fluo_result_list,
                'Fluo corrected',
            )
            self.figures.append(PlotlyFigure(label='SDD overview', figure=json.loads(fig1.to_json())))

        if self.manual_energy_shift is not None and self.absorbance_of_the_sample is not None:
            fig2 = make_xas_plot(
                'Absorbance of Sample',
                self.energy + self.manual_energy_shift,
                'Energy (aligned energy scale)',
                [self.absorbance_of_the_sample],
                'µ',
            )
            self.figures.append(PlotlyFigure(label='Sample Absorbance Plot', figure=json.loads(fig2.to_json())))


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
        self.method = 'XAS Fluorescence'
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
