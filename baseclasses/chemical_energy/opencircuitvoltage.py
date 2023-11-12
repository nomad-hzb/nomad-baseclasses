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

from nomad.metainfo import (Quantity, SubSection)
from nomad.datamodel.data import ArchiveSection

from .voltammetry import Voltammetry
from .potentiostat_measurement import PotentiostatProperties


class OCVProperties(PotentiostatProperties):

    total_time = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        shape=[],
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='s'))

    sample_period = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        shape=[],
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='s'))

    stability = Quantity(
        type=np.dtype(np.float64),
        unit=('mV/s'),
        shape=[],
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mV/s'))


class OpenCircuitVoltage(Voltammetry):

    properties = SubSection(
        section_def=OCVProperties)

    def normalize(self, archive, logger):
        self.method = "Open Circuit Voltage"
        super(OpenCircuitVoltage, self).normalize(archive, logger)
