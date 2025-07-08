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
from nomad.datamodel.data import ArchiveSection
from nomad.metainfo import Datetime, Quantity, Section, SubSection

from .. import BaseMeasurement


class TemperatureSensors(ArchiveSection):
    m_def = Section(label_quantity='name')

    name = Quantity(type=str)

    temperature = Quantity(
        links=["http://purl.obolibrary.org/obo/PATO_0000146"],
        type=np.dtype(np.float64), unit=('°C'), shape=['*'])


class EnvironmentData(ArchiveSection):
    time = Quantity(type=np.dtype(np.float64), unit=('s'), shape=['*'])

    datetime = Quantity(type=Datetime, shape=['*'])

    temperature = Quantity(type=np.dtype(np.float64), unit=('°C'), shape=['*'])

    humidity = Quantity(type=np.dtype(np.float64), shape=['*'])

    pressure = Quantity(type=np.dtype(np.float64), unit=('mbar'), shape=['*'])

    temperature_sensors = SubSection(section_def=TemperatureSensors, repeats=True)


class EnvironmentMeasurement(BaseMeasurement):
    """Base class for environment measurement"""

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'),
    )

    data = SubSection(section_def=EnvironmentData)

    # properties = SubSection(section_def=XRDProperties)

    def normalize(self, archive, logger):
        super().normalize(archive, logger)
        self.method = 'Environment measurement'
