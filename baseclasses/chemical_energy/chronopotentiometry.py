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
    Quantity, SubSection)
from nomad.datamodel.data import ArchiveSection

from .voltammetry import Voltammetry
from .potentiostat_measurement import PotentiostatProperties


class CPProperties(PotentiostatProperties):

    pre_step_current = Quantity(
        type=np.dtype(np.float64),
        unit=('A'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='A'))

    pre_step_delay_time = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='s'))

    step_1_current = Quantity(
        type=np.dtype(np.float64),
        unit=('A'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='A'))

    step_1_time = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='s'))

    step_2_current = Quantity(
        type=np.dtype(np.float64),
        unit=('A'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='A'))

    step_2_time = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='s'))

    sample_period = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='s'))

    lower_limit_potential = Quantity(
        type=np.dtype(np.float64),
        unit=('V'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='V'))

    upper_limit_potential = Quantity(
        type=np.dtype(np.float64),
        unit=('V'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='V'))


class Chronopotentiometry(Voltammetry):

    properties = SubSection(
        section_def=CPProperties)

    def normalize(self, archive, logger):
        self.method = "Chronopotentiometry"
        super(Chronopotentiometry, self).normalize(archive, logger)
