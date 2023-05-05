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
    Reference,
    SubSection)

from nomad.datamodel.data import ArchiveSection

from .. import LayerDeposition
from ..solution import Solution
from ..material_processes_misc import Annealing


class SprayPyrolysisProperties(ArchiveSection):

    solution = Quantity(
        type=Reference(Solution.m_def),
        a_eln=dict(component='ReferenceEditQuantity'))

    volume = Quantity(
        type=np.dtype(
            np.float64),
        unit=('ml'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='ml',
            props=dict(
                minValue=0)))

    temperature = Quantity(
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'))


class SprayPyrolysis(LayerDeposition):
    '''Base class for spray pyrolysis of a sample'''

    precursor_solution = SubSection(section_def=SprayPyrolysisProperties)
    annealing = SubSection(section_def=Annealing, repeats=True)

    def normalize(self, archive, logger):
        super(SprayPyrolysis, self).normalize(archive, logger)

        self.method = "Spray Pyrolysis"
