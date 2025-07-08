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

from baseclasses import PubChemPureSubstanceSectionCustom

from .. import LayerDeposition


class ALDProperties(ArchiveSection):
    m_def = Section(label_quantity='name')
    name = Quantity(type=str)

    chemical_2 = SubSection(
        links=['http://purl.obolibrary.org/obo/RO_0000057'],
        section_def=PubChemPureSubstanceSectionCustom,
    )

    source = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=['LTE1', 'LTE2', 'LTE3', 'LTE4', 'ULTE1', 'ULTE2']),
        ),
    )

    thickness = Quantity(
        links=['http://purl.obolibrary.org/obo/PATO_0000915'],
        type=np.dtype(np.float64),
        unit=('nm'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='nm',
            props=dict(minValue=0),
        ),
    )

    temperature = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0000146',
            'https://purl.archive.org/tfsco/TFSCO_00002111',
        ],
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'),
    )

    rate = Quantity(
        links=['https://purl.archive.org/tfsco/TFSCO_00002110'],
        type=np.dtype(np.float64),
        unit=('angstrom/s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='angstrom/s',
            props=dict(minValue=0),
        ),
    )

    time = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0000165',
            'https://purl.archive.org/tfsco/TFSCO_00005085',
        ],
        type=np.dtype(np.float64),
        unit=('s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='s',
            props=dict(minValue=0),
        ),
    )

    number_of_cycles = Quantity(
        type=np.dtype(np.int64),
        a_eln=dict(component='NumberEditQuantity', props=dict(minValue=1)),
    )

    def normalize(self, archive, logger):
        if self.chemical_2:
            if self.chemical_2.name:
                self.name = self.chemical_2.name

        if self.thickness:
            if self.name:
                self.name += ' ' + str(self.thickness)
            else:
                self.name = str(self.thickness)


class ALDMaterial(ArchiveSection):
    material = SubSection(
        links=['http://purl.obolibrary.org/obo/RO_0000057'],
        section_def=PubChemPureSubstanceSectionCustom,
    )

    pulse_duration = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='s',
            props=dict(minValue=0),
        ),
    )

    pulse_flow_rate = Quantity(
        links=["http://purl.obolibrary.org/obo/PATO_0001574"],
        type=np.dtype(np.float64),
        unit=('cm**3/minute'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='cm**3/minute',
            props=dict(minValue=0),
        ),
    )

    purge_duration = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='s',
            props=dict(minValue=0),
        ),
    )

    purge_flow_rate = Quantity(
        type=np.dtype(np.float64),
        unit=('cm**3/minute'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='cm**3/minute',
            props=dict(minValue=0),
        ),
    )

    manifold_temperature = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0000146',
            'https://purl.archive.org/tfsco/TFSCO_00002111',
        ],
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'),
    )

    bottle_temperature = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0000146',
            'https://purl.archive.org/tfsco/TFSCO_00002111',
        ],
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'),
    )


class ALDPropertiesIris(ALDProperties):
    m_def = Section(
        label_quantity='name',
        a_eln=dict(
            hide=['chemical_2'],
            properties=dict(
                order=[
                    'source',
                    'thickness',
                    'number_of_cycles',
                    'temperature',
                    'door_temperature',
                ]
            ),
        ),
    )

    door_temperature = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0000146',
            'https://purl.archive.org/tfsco/TFSCO_00002111',
        ],
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'),
    )

    material = SubSection(section_def=ALDMaterial)

    oxidizer_reducer = SubSection(section_def=ALDMaterial)

    def normalize(self, archive, logger):
        if self.material and self.material.material:
            if self.material.material.name:
                self.name = self.material.material.name

        if self.thickness:
            if self.name:
                self.name += ' ' + str(self.thickness)
            else:
                self.name = str(self.thickness)


class AtomicLayerDeposition(LayerDeposition):
    """Base class for evaporation of a sample"""

    m_def = Section(links=['http://purl.obolibrary.org/obo/CHMO_0001311'])

    properties = SubSection(section_def=ALDProperties)

    def normalize(self, archive, logger):
        super().normalize(archive, logger)

        self.method = 'Atomic Layer Deposition'
