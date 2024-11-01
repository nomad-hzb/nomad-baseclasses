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
from nomad.metainfo import Quantity, Section, SubSection

from .wet_chemical_deposition import WetChemicalDeposition


class DipCoatingProperties(ArchiveSection):
    time = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0000165',
            'https://purl.archive.org/tfsco/TFSCO_00005085',
        ],
        type=np.dtype(np.float64),
        unit=('minute'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='minute',
            props=dict(minValue=0),
        ),
    )


class DipCoating(WetChemicalDeposition):
    """Base class for dip coating of a sample"""

    m_def = Section(
        links=['http://purl.obolibrary.org/obo/CHMO_0001471'],
    )

    properties = SubSection(section_def=DipCoatingProperties)

    def normalize(self, archive, logger):
        self.method = 'Dip Coating'
        super().normalize(archive, logger)
