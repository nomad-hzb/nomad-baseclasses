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
    Section,
    SubSection)
from nomad.datamodel.data import ArchiveSection

from .. import BaseMeasurement, SingleLibraryMeasurement, LibraryMeasurement


class XRFData(ArchiveSection):
    m_def = Section(
        label_quantity='name')

    name = Quantity(
        type=str)

    intensity = Quantity(
        type=np.dtype(
            np.float64), shape=['*'])


class XRFComposition(ArchiveSection):
    m_def = Section(
        label_quantity='name')

    name = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'))
    
    layer = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'))

    amount = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity'))


class XRFProperties(ArchiveSection):

    xray_energy = Quantity(
        type=np.dtype(np.float64),
        unit=('eV'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='eV'))

    current = Quantity(
        type=np.dtype(np.float64),
        unit=('uA'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='uA'))

    spot_size = Quantity(
        type=np.dtype(np.float64),
        unit=('mm'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mm'))

    integration_time = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='s'))

    filter_settings = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'))


class XRF(BaseMeasurement):
    '''UV vis Measurement'''

    m_def = Section(
        a_eln=dict(hide=['certified_values', 'certification_institute']))

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    # data = SubSection(
    #     section_def=XRFData)

    composition = SubSection(
        section_def=XRFComposition, repeats=True)

    properties = SubSection(
        section_def=XRFProperties)

    def normalize(self, archive, logger):
        super(XRF, self).normalize(archive, logger)
        self.method = "XRF"


class XRFSingleLibraryMeasurement(SingleLibraryMeasurement):
    m_def = Section(label_quantity='name',
                    a_eln=dict(properties=dict(
                        order=[
                            "name", "data_file", "position_x_relative", "position_y_relative", "position_index", "thickness", "position_x", "position_y"
                        ]))
                    )

    # data = SubSection(
    #     section_def=XRFData)

    composition = SubSection(
        section_def=XRFComposition, repeats=True)

    thickness = Quantity(
        type=np.dtype(np.float64),
        unit=('nm'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='nm'))


class XRFLibrary(LibraryMeasurement):
    '''UV vis Measurement'''

    m_def = Section(
        a_eln=dict(hide=['certified_values', 'certification_institute']))
    
    data_folder = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'))
    
    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    images = Quantity(
        type=str,
        shape=["*"],
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    composition_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    energy = Quantity(
        type=np.dtype(
            np.float64), unit=('nm'), shape=['*'])

    properties = SubSection(
        section_def=XRFProperties)

    measurements = SubSection(
        section_def=XRFSingleLibraryMeasurement, repeats=True)

    def normalize(self, archive, logger):
        super(XRFLibrary, self).normalize(archive, logger)
        self.method = "XRF"
