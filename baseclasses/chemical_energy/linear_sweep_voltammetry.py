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

import os
import numpy as np

from nomad.metainfo import (Quantity, SubSection, MEnum, Section)
from nomad.datamodel.data import ArchiveSection

from .voltammetry import Voltammetry
from .potentiostat_measurement import PotentiostatProperties


class LSVProperties(PotentiostatProperties):

    initial_potential = Quantity(
        links=['https://w3id.org/nfdi4cat/voc4cat_0007216'],
        type=np.dtype(np.float64),
        unit=('V'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='V'))

    initial_potential_measured_against = Quantity(
        type=MEnum('Eoc', 'Eref'),
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
        ))

    final_potential = Quantity(
        links=['https://w3id.org/nfdi4cat/voc4cat_0007217'],
        type=np.dtype(np.float64),
        unit=('V'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='V'))

    final_potential_measured_against = Quantity(
        type=MEnum('Eoc', 'Eref'),
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
        ))

    scan_rate = Quantity(
        type=np.dtype(np.float64),
        unit=('mV/s'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mV/s'))

    step_size = Quantity(
        type=np.dtype(np.float64),
        unit=('mV'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mV'))

    open_circuit_potential = Quantity(
        type=np.dtype(np.float64),
        unit=('V'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='V'))


class LinearSweepVoltammetry(Voltammetry):

    m_def = Section(
        links=['https://w3id.org/nfdi4cat/voc4cat_0007211'],
    )

    properties = SubSection(
        section_def=LSVProperties)

    def normalize(self, archive, logger):
        self.method = "Linear Sweep Voltammetry"
        super(LinearSweepVoltammetry, self).normalize(archive, logger)
