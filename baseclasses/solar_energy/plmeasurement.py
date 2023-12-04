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
from nomad.metainfo import (
    Quantity,
    Section, SubSection)
from .. import BaseMeasurement, SingleLibraryMeasurement, LibraryMeasurement
from nomad.datamodel.data import ArchiveSection


class PLDataSimple(ArchiveSection):
    m_def = Section(label_quantity='name')

    name = Quantity(
        type=str)

    intensity = Quantity(
        type=np.dtype(
            np.float64), shape=['*'])


class PLData(PLDataSimple):
    wavelength = Quantity(
        type=np.dtype(
            np.float64), unit=('nm'), shape=['*'])


class PLProperties(ArchiveSection):

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

    wavelength_start = Quantity(
        type=np.dtype(np.float64),
        unit=('nm'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='nm'))

    wavelength_stop = Quantity(
        type=np.dtype(np.float64),
        unit=('nm'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='nm'))

    wavelength_step_size = Quantity(
        type=np.dtype(np.float64),
        unit=('nm'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='nm'))

    temperature = Quantity(
        type=np.dtype(np.float64),
        unit=('K'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'))

    lamp = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'))


class PLMeasurement(BaseMeasurement):
    '''PL Measurement'''

    m_def = Section(
        a_eln=dict(hide=['certified_values', 'certification_institute']))

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    properties = SubSection(
        section_def=PLProperties)

    data = SubSection(
        section_def=PLData)

    def normalize(self, archive, logger):
        self.method = "PL Measurement"
        super(PLMeasurement, self).normalize(archive, logger)


class PLSingleLibraryMeasurement(SingleLibraryMeasurement):
    m_def = Section(label_quantity='name',
                    a_eln=dict(properties=dict(
                        order=[
                            "name", "position_x_relative", "position_y_relative", "position_index", "position_x", "position_y"
                        ]))
                    )

    data = SubSection(
        section_def=PLDataSimple)


class PLMeasurementLibrary(LibraryMeasurement):
    '''PL Measurement'''

    m_def = Section(
        a_eln=dict(hide=['certified_values', 'certification_institute']))

    reference_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    wavelength = Quantity(
        type=np.dtype(
            np.float64), unit=('nm'), shape=['*'])

    properties = SubSection(
        section_def=PLProperties)

    measurements = SubSection(
        section_def=PLSingleLibraryMeasurement, repeats=True)

    def normalize(self, archive, logger):
        super(PLMeasurementLibrary, self).normalize(archive, logger)
        self.method = "PL Measurement Mapping"
