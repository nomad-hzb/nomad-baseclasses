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
from nomad.metainfo import Quantity, Reference, Section, SectionProxy, SubSection
from scipy.optimize import curve_fit

from baseclasses.helper.plotly_plots import make_xas_plot

from .. import BaseMeasurement


class XAS(BaseMeasurement):
    """XAS Measurement"""
    m_def = Section(
        links=['https://w3id.org/nfdi4cat/voc4cat_0000286']
    )

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'),
    )

    energy = Quantity(
        links=['https://w3id.org/nfdi4cat/voc4cat_0008097'],
        type=np.dtype(np.float64),
        shape=['*'],
        unit='keV',
        description='The energy range of the spectrum.',
    )

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
        description='X-ray intensity before the sample.',
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
        description='X-ray intensity after the sample.',
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
        description='X-ray intensity after sample and after energy standard/reference '
                    '(depending on the setup in the beamline). '
                    'In KMC-2 the setup in transmission mode may contain a metal foil as the energy reference '
                    'while KMC-3 uses a fixed energy standard.',
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
        links=['https://w3id.org/nfdi4cat/voc4cat_0008090'],
        type=np.dtype(np.float64),
        description='Aligns the energy spectrum with a known reference like the absorption edge of a reference foil. '
                    '(true energy value = measured energy value + manual_energy_shift)',
        unit='keV',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='keV'),
    )

    connected_measurements = Quantity(
        type=Reference(SectionProxy('XAS')),
        shape=['*'],
        a_eln=dict(component='ReferenceEditQuantity'),
    )

    def normalize(self, archive, logger):
        super().normalize(archive, logger)


class SiliconDriftDetector(PlotSection, ArchiveSection):
    m_def = Section(
        links=['https://w3id.org/nfdi4cat/voc4cat_0008083'],
    )
    fluo = Quantity(
        links=['https://w3id.org/nfdi4cat/voc4cat_0008091'],
        type=np.dtype(np.float64),
        shape=['*'],
    )
    icr = Quantity(
        links=['https://w3id.org/nfdi4cat/voc4cat_0008092'],
        type=np.dtype(np.float64),
        shape=['*'],
        description='Incoming Count Rate',
    )
    ocr = Quantity(
        links=['https://w3id.org/nfdi4cat/voc4cat_0008093'],
        type=np.dtype(np.float64),
        shape=['*'],
        description='Outgoing Count Rate',
    )
    tlt = Quantity(
        links=['https://w3id.org/nfdi4cat/voc4cat_0008094'],
        type=np.dtype(np.float64),
        shape=['*'],
        description='Trigger Live Time',
    )
    lt = Quantity(
        links=['https://w3id.org/nfdi4cat/voc4cat_0008095'],
        type=np.dtype(np.float64),
        shape=['*'],
        description='Live Time',
    )
    rt = Quantity(
        links=['https://manual.nexusformat.org/classes/base_classes/NXdetector.html#nxdetector-real-time-field',
               'https://w3id.org/nfdi4cat/voc4cat_0008096'],
        type=np.dtype(np.float64),
        shape=['*'],
        description='Real Time',
    )
    slope = Quantity(
        type=np.dtype(np.float64),
        description='slope=A*k for fit of OCR = A * (1 - exp(-k * ICR))',
    )
    fluo_dead_time_corrected = Quantity(
        links=['https://w3id.org/nfdi4cat/voc4cat_0008085'],
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
            initial_k = 1e-5
            try:
                params, _ = curve_fit(
                    exp_func, self.icr, self.ocr, p0=(a0, initial_k), maxfev=10000
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
        links=['https://w3id.org/nfdi4cat/voc4cat_0008089'],
        type=np.dtype(np.float64),
        shape=['*'],
        description='For XAS Fluorescence absorbance_of_the_sample = mean(all fluo_tlt_results from the sdd channels). '
                    'For XAS Transmission absorbance_of_the_sample = -ln(k1 / k0) .',
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

        fluo_result_list = [sdd.get('fluo_tlt_result') for sdd in self.sdd_parameters]
        fluo_result_list = np.array(fluo_result_list, dtype=float)
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
    m_def = Section(
        links=['https://w3id.org/nfdi4cat/voc4cat_0008082']
    )
    absorbance_of_the_reference = Quantity(
        links=['https://w3id.org/nfdi4cat/voc4cat_0008088'],
        type=np.dtype(np.float64),
        shape=['*'],
        description='absorbance_of_the_reference = -ln(k1 / k0)',
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
        links=['https://w3id.org/nfdi4cat/voc4cat_0008086'],
        type=np.dtype(np.float64),
        shape=['*'],
        description='fluorescence_yield = k3 / k0',
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
    m_def = Section(
        links=['https://w3id.org/nfdi4cat/voc4cat_0008081']
    )

    absorbance_of_the_reference = Quantity(
        links=['https://w3id.org/nfdi4cat/voc4cat_0008088'],
        type=np.dtype(np.float64),
        shape=['*'],
        description='absorbance_of_the_reference = -ln(k3/k1)',
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
        links=['https://w3id.org/nfdi4cat/voc4cat_0008089'],
        type=np.dtype(np.float64),
        shape=['*'],
        description='absorbance_of_the_sample = -ln(k1/k0)',
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
