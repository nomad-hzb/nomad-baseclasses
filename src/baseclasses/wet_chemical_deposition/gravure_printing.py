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
from nomad.metainfo import MEnum, Quantity, Section, SubSection

from .wet_chemical_deposition import WetChemicalDeposition


class GravurePrintingProperties(ArchiveSection):
    gp_coating_speed = Quantity(
        links=[],
        type=np.dtype(np.float64),
        unit=('m/minute'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='m/minute',
            props=dict(minValue=0),
        ),
        description='The speed of substrate during gravure printing',
    )

    screen_ruling = Quantity(
        links=[],
        type=np.dtype(np.float64),
        a_eln=dict(
            component='NumberEditQuantity',
            props=dict(minValue=0),
        ),
        description='Screen ruling of the gravure printing cylinder (lines per cm).',
    )

    gp_method = Quantity(
        type=MEnum('R2R', 'S2S'),
        shape=[],
        a_eln=dict(component='EnumEditQuantity'),
        description='Roll-to-Roll or Sheet-to-Sheet gravure printing.',
    )

    gp_direction = Quantity(
        type=MEnum('Forward', 'Reverse'),
        shape=[],
        a_eln=dict(component='EnumEditQuantity'),
        description=(
            'Material and cylinder moving in the same direction for forward mode, '
            'and in opposite directions for reverse mode.'
        ),
    )

    cell_type = Quantity(
        links=[],
        type=str,
        a_eln=dict(component='StringEditQuantity'),
        description='The shape of the engraving cell.',
    )

    ink_temperature = Quantity(
        links=[],
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='°C',
            props=dict(minValue=0),
        ),
        description=(
            'Measured by the water temperature when ink in water bath in S2S,'
            'and by the whole ink reservoir temperature in R2R'
        ),
    )


class GravurePrinting(WetChemicalDeposition):
    """Base class for the gravure printing process of a sample"""

    m_def = Section(links=['https://purl.archive.org/tfsco/TFSCO_00002054'])

    properties = SubSection(section_def=GravurePrintingProperties)

    def normalize(self, archive, logger):
        self.method = 'Gravure Printing'
        super().normalize(archive, logger)
