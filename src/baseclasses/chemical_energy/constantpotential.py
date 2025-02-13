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

from .. import BaseMeasurement
from .potentiostat_measurement import PotentiostatProperties
from baseclasses.chemical_energy.chronoamperometry import CAProperties
from baseclasses.chemical_energy.chronopotentiometry import CPProperties
import numpy as np
from nomad.metainfo import Quantity

class ConstProperties(PotentiostatProperties):
    total_time = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        shape=[],
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='s'),
    )

    sample_period = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        shape=[],
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='s'),
    )

    lower_limit_potential = Quantity(
        links=['https://w3id.org/nfdi4cat/voc4cat_0007214'],
        type=np.dtype(np.float64),
        unit=('V'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='V'),
    )

    upper_limit_potential = Quantity(
        links=['https://w3id.org/nfdi4cat/voc4cat_0007215'],
        type=np.dtype(np.float64),
        unit=('V'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='V'),
    )

    cycles = Quantity(
        links=['https://w3id.org/nfdi4cat/voc4cat_0007228'],
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity'),
    )


class ConstCProperties(ConstProperties, CPProperties):
    def normalize(self, archive, logger):
        super().normalize(archive, logger)


class ConstVProperties(ConstProperties, CAProperties):
    def normalize(self, archive, logger):
        super().normalize(archive, logger)


class ConstantPotential(BaseMeasurement):
    """Eqe Measurement"""

    def normalize(self, archive, logger):
        super().normalize(archive, logger)
        self.method = 'EQE Measurement'
