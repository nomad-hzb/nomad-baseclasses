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
    SubSection,
    Reference)
from nomad.datamodel.data import ArchiveSection


from .wet_chemical_deposition import WetChemicalDeposition


class DipCoatingProperties(ArchiveSection):

    time = Quantity(
        type=np.dtype(
            np.float64),
        unit=('min'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='min',
            props=dict(
                minValue=0)))


class DipCoating(WetChemicalDeposition):
    '''Base class for spin coating of a sample'''

    properties = SubSection(
        section_def=DipCoatingProperties)

    def normalize(self, archive, logger):
        super(DipCoating, self).normalize(archive, logger)
        self.method = "Dip Coating"
