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
from datetime import datetime
import pandas as pd


from nomad.metainfo import (
    Quantity,
    Section,
    SubSection,
    Datetime)
from nomad.datamodel.data import ArchiveSection

from .. import BaseMeasurement, SingleLibraryMeasurement


class UVvisDataSimple(ArchiveSection):
    m_def = Section(label_quantity='name')

    name = Quantity(
        type=str)

    intensity = Quantity(
        type=np.dtype(
            np.float64), shape=['*'])


class UVvisData(UVvisDataSimple):
    m_def = Section(label_quantity='name',
                    a_plot=[{
                        'x': 'wavelength',
                             'y': 'intensity',
                             'layout': {'yaxis': {"fixedrange": False},
                                        'xaxis': {"fixedrange": False}},
                             "config": {"scrollZoom": True,
                                        'staticPlot': False,
                                        }}])

    datetime = Quantity(
        type=Datetime,
        description='The date and time associated with this section.',
        a_eln=dict(component='DateTimeEditQuantity'))

    wavelength = Quantity(
        type=np.dtype(
            np.float64), shape=['*'], unit='nm', a_plot=[
            {
                'x': 'wavelength', 'y': 'intensity', 'layout': {
                    'yaxis': {
                        "fixedrange": False}, 'xaxis': {
                            "fixedrange": False}}, "config": {
                    "editable": True, "scrollZoom": True}}])


class UVvisProperties(ArchiveSection):

    integration_time = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='s'))

    number_of_averages = Quantity(
        type=np.dtype(np.int64),
        a_eln=dict(component='NumberEditQuantity'))

    spot_size = Quantity(
        type=np.dtype(np.float64),
        unit=('mm'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mm'))


class UVvisMeasurement(BaseMeasurement):
    '''UV vis Measurement'''

    m_def = Section(
        a_eln=dict(hide=['certified_values', 'certification_institute']))

    data_file = Quantity(
        type=str,
        shape=['*'],
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    measurements = SubSection(
        section_def=UVvisData, repeats=True)

    def normalize(self, archive, logger):
        self.method = "UVvis Measurement"
        super(UVvisMeasurement, self).normalize(archive, logger)


class UVvisSingleLibraryMeasurement(SingleLibraryMeasurement):
    m_def = Section(label_quantity='name',
                    a_eln=dict(properties=dict(
                        order=[
                            "name", "position_x_relative", "position_y_relative", "position_index", "position_x", "position_y"
                        ]))
                    )

    data = SubSection(
        section_def=UVvisDataSimple)


class UVvisMeasurementLibrary(BaseMeasurement):
    '''UV vis Measurement'''

    m_def = Section(
        a_eln=dict(hide=['certified_values', 'certification_institute']))

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    reference_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    wavelength = Quantity(
        type=np.dtype(
            np.float64), unit=('nm'), shape=['*'])

    properties = SubSection(
        section_def=UVvisProperties)

    measurements = SubSection(
        section_def=UVvisSingleLibraryMeasurement, repeats=True)

    def normalize(self, archive, logger):
        super(UVvisMeasurementLibrary, self).normalize(archive, logger)
        self.method = "UVvis Measurement Mapping"
