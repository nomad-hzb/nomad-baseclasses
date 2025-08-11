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


class BladeCoatingProperties(ArchiveSection):
    blade_speed = Quantity(
        links=[
            'https://purl.archive.org/tfsco/TFSCO_00007009', 
            'https://purl.archive.org/tfsco/TFSCO_00007010'
            ],
        type=np.dtype(np.float64),
        unit=('mm/s'),
        a_eln=dict(
            compontent='NumberEditQuantity',
            DefaultDisplayUnit='mm/s',
            props=dict(minValue=0),
        ),
        description='Speed of the blade during coating process',
    )

    dispensed_volume = Quantity(
        links=[
            'https://purl.archive.org/tfsco/TFSCO_00007022',
            'https://purl.archive.org/tfsco/TFSCO_00002160'
            ],
        type=np.dtype(np.float64),
        unit=('uL'),
        a_eln=dict(
            compontent='NumberEditQuantity',
            DefaultDisplayUnit='uL',
            props=dict(minValue=0),
        ),
        description='Volume of dispensed ink administered by a pipette on the sample'
        'surface',
    )

    blade_substrate_gap = Quantity(
        links=[
            'https://purl.archive.org/tfsco/TFSCO_00007007', 
            'https://purl.archive.org/tfsco/TFSCO_00007008'
            ],
        type=np.dtype(np.float64),
        unit=('um'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='um',
            props=dict(minValue=0),
        ),
        description='The distance between the blade and the substrate',
    )

    blade_size = Quantity(
        links= 'https://purl.archive.org/tfsco/TFSCO_00007016',
        type=str,
        a_eln=dict(component='StringEditQuantity'),
        description='Size of the blade. Normally, the blade is larger than the '
        'substrate, resulting in the coating of the whole available area.'
        'If the substrate is larger than the blade size, the coating area is that of'
        ' the blade size.',
    )

    coating_width = Quantity(
        links=[],
        type=np.dtype(np.float64),
        unit=('mm'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mm',
            props=dict(minValue=0),
        ),
    )

    coating_length = Quantity(
        links=[],
        type=np.dtype(np.float64),
        unit=('mm'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mm',
            props=dict(minValue=0),
        ),
    )

    dead_length = Quantity(
        links=[],
        type=np.dtype(np.float64),
        unit=('mm'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mm',
            props=dict(minValue=0),
        ),
        description=(
            'The length that is left before the real coating in order to '
            'stabilise the meniscus'
        ),
    )

    bed_temperature = Quantity(
        links=[],
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='°C',
            props=dict(minValue=0),
        ),
        description=(
            'Temperature of the bed at the start of blade coating. '
            'Measured by heated chuck, infrared thermometer or other methods, '
            'the substrate temperature is approximated to be equal to bed temperature'
        ),
    )

    ink_temperature = Quantity(
        links=[
            'https://purl.archive.org/tfsco/TFSCO_00002001',
            'https://purl.archive.org/tfsco/TFSCO_00002073',
        ],
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='°C',
            props=dict(minValue=0),
        ),
        description='Temperature of hot plate where the vial containing the ink '
        'solution is placed',
    )


class BladeCoating(WetChemicalDeposition):
    """Base class for blade coating of a sample"""

    m_def = Section(
        links = ['https://purl.archive.org/tfsco/TFSCO_00002060'],
    )

    properties = SubSection(section_def=BladeCoatingProperties)

    def normalize(self, archive, logger):
        self.method = 'Blade Coating'
        super().normalize(archive, logger)
