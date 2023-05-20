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

from nomad.metainfo import (Quantity, Reference, SubSection)

from .. import MeasurementOnSample
from .cesample import Environment, ElectroChemicalSetup

from nomad.datamodel.data import ArchiveSection


class PotentiostatSetup(ArchiveSection):

    flow_cell_pump_rate = Quantity(
        type=np.dtype(np.float64),
        unit=('mL/minute'),
        a_eln=dict(component='NumberEditQuantity',
                   defaultDisplayUnit='mL/minute'))

    flow_cell_pressure = Quantity(
        type=np.dtype(np.float64),
        unit=('bar'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='bar'))

    rotation_speed = Quantity(
        type=np.dtype(np.float64),
        unit=('rpm'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='rpm'))


class PotentiostatMeasurement(MeasurementOnSample):

    station = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'))

    environment = Quantity(
        type=Reference(Environment.m_def),
        a_eln=dict(component='ReferenceEditQuantity'))

    setup = Quantity(
        type=Reference(ElectroChemicalSetup.m_def),
        a_eln=dict(component='ReferenceEditQuantity'))

    setup_parameters = SubSection(
        section_def=PotentiostatSetup)

    def normalize(self, archive, logger):
        super(PotentiostatMeasurement, self).normalize(archive, logger)
