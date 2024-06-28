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

import numpy as np
import os

from nomad.metainfo import (
    Quantity,
    SubSection,
    Section)
from nomad.datamodel.data import ArchiveSection

from .. import BaseMeasurement, SingleLibraryMeasurement, LibraryMeasurement


class TRPLPropertiesBasic(ArchiveSection):
    m_def = Section(label_quantity='name')

    name = Quantity(
        type=str)

    repetition_rate = Quantity(
        type=np.dtype(
            np.float64),
        unit=('MHz'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='MHz',
            props=dict(
                minValue=0)))

    spotsize = Quantity(
        type=np.dtype(
            np.float64),
        unit=('cm^2'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='cm^2', props=dict(minValue=0)))

    integration_time = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='s'))

    laser_power = Quantity(
        type=np.dtype(
            np.float64),
        unit=('nW'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='nW',
            props=dict(
                minValue=0)))

    excitation_peak_wavelength = Quantity(
        type=np.dtype(
            np.float64), unit=('nm'), shape=[], a_eln=dict(
            component='NumberEditQuantity', defaultDisplayUnit='nm', props=dict(
                minValue=0)))

    detection_wavelength = Quantity(
        type=np.dtype(
            np.float64), unit=('nm'), shape=[], a_eln=dict(
            component='NumberEditQuantity', defaultDisplayUnit='nm', props=dict(
                minValue=0)))

    excitation_FWHM = Quantity(
        type=np.dtype(
            np.float64),
        unit=('nm'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='nm',
            props=dict(
                minValue=0)))

    excitation_attenuation_filter = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        a_eln=dict(component='NumberEditQuantity'))

    ns_per_bin = Quantity(
        type=np.dtype(
            np.float64),
        unit=('ns'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='ns',
            props=dict(
                minValue=0)))


class TRPLProperties(TRPLPropertiesBasic):
    m_def = Section(label_quantity='name',
                    a_plot=[{
                        'x': 'time',
                             'y': 'counts',
                             'layout': {'yaxis': {"fixedrange": False},
                                        'xaxis': {"fixedrange": False}},
                             "config": {"scrollZoom": True,
                                        'staticPlot': False,
                                        }}])

    signal_attenuation_filter = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        a_eln=dict(component='NumberEditQuantity'))

    time = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        unit=('ns'),
        description='Counts of the trpl measurement per bin.',
        a_plot={
            'x': 'time', 'y': 'counts'
        })

    counts = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        description='Counts of the trpl measurement per bin.',
        a_plot={
            'x': 'time', 'y': 'counts'
        })


class TimeResolvedPhotoluminescence(BaseMeasurement):

    m_def = Section(label_quantity='file_name', validate=False)

    data_file = Quantity(
        type=str,
        shape=['*'],
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    trpl_properties = SubSection(
        section_def=TRPLProperties, repeats=True)

    def normalize(self, archive, logger):
        self.method = "Time-Resolved Photoluminescence"
        super(TimeResolvedPhotoluminescence, self).normalize(archive, logger)


class TRPLDataSimple(ArchiveSection):
    m_def = Section(label_quantity='name')

    name = Quantity(
        type=str)

    counts = Quantity(
        type=np.dtype(
            np.int32), shape=['*'])


class TimeResolvedPhotoluminescenceSingleLibraryMeasurement(SingleLibraryMeasurement):
    m_def = Section(label_quantity='name',
                    a_eln=dict(properties=dict(
                        order=[
                            "name", "position_x", "position_y"
                        ]))
                    )

    data = SubSection(
        section_def=TRPLDataSimple)


class TimeResolvedPhotoluminescenceMeasurementLibrary(LibraryMeasurement):
    '''UV vis Measurement'''

    m_def = Section(
        a_eln=dict(hide=['certified_values', 'certification_institute']))

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    time = Quantity(
        type=np.dtype(
            np.float64), unit=('ps'), shape=['*'])

    properties = SubSection(
        section_def=TRPLPropertiesBasic)

    measurements = SubSection(
        section_def=TimeResolvedPhotoluminescenceSingleLibraryMeasurement, repeats=True)

    def normalize(self, archive, logger):
        super(TimeResolvedPhotoluminescenceMeasurementLibrary, self).normalize(archive, logger)
        self.method = "TRPL Measurement Mapping"
