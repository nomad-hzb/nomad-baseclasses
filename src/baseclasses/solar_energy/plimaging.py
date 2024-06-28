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
from .. import BaseMeasurement
from nomad.datamodel.data import ArchiveSection


class PLIproperties(ArchiveSection):
    lamp = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'))

    integration_time = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='ms'))

    excitation_wavelength = Quantity(
        type=np.dtype(np.float64),
        unit=('nm'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='nm'))

    excitation_current = Quantity(
        type=np.dtype(np.float64),
        unit=('A'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mA'))

    light_intensity = Quantity(
        type=np.dtype(np.float64),
        unit=('W/m^2'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mW/cm^2'))

    number_of_averages = Quantity(
        type=np.dtype(np.int64),
        a_eln=dict(component='NumberEditQuantity'))


class PLImaging(BaseMeasurement):
    '''PL Imaging'''

    m_def = Section(
        a_eln=dict(hide=['certified_values', 'certification_institute']))

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    properties = SubSection(
        section_def=PLIproperties)

    def normalize(self, archive, logger):
        super(PLImaging, self).normalize(archive, logger)
        self.method = "PL Imaging"
