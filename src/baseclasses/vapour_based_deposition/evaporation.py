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
from nomad.metainfo import Quantity, Reference, Section, SubSection

from baseclasses import PubChemPureSubstanceSectionCustom

from .. import LayerDeposition
from ..chemical import Chemical


class EvaporationSources(ArchiveSection):
    chemical = Quantity(
        links=['http://purl.obolibrary.org/obo/CHEBI_59999'],
        type=Reference(Chemical.m_def),
        a_eln=dict(component='ReferenceEditQuantity'),
    )

    chemical_2 = SubSection(
        links=['http://purl.obolibrary.org/obo/RO_0000057'],
        section_def=PubChemPureSubstanceSectionCustom,
    )

    sources = Quantity(
        type=str,
        a_eln=dict(
            component='StringEditQuantity',
            props=dict(suggestions=['TE1', 'TE2', 'UE1', 'UE2']),
        ),
    )

    tooling_factor = Quantity(
        type=np.dtype(np.float64), a_eln=dict(component='NumberEditQuantity')
    )

    mass_before_weighing = Quantity(
        links=['http://purl.obolibrary.org/obo/PATO_0000125'],
        type=np.dtype(np.float64),
        unit=('g'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='g',
            props=dict(minValue=0),
        ),
    )

    mass_after_weighing = Quantity(
        links=['http://purl.obolibrary.org/obo/PATO_0000125'],
        type=np.dtype(np.float64),
        unit=('g'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='g',
            props=dict(minValue=0),
        ),
    )

    mass_after_processing = Quantity(
        links=['http://purl.obolibrary.org/obo/PATO_0000125'],
        type=np.dtype(np.float64),
        unit=('g'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='g',
            props=dict(minValue=0),
        ),
    )

    comment = Quantity(type=str, a_eln=dict(component='RichTextEditQuantity'))

    # def normalize(self, archive, logger):
    # TODO add check if mass increased
    # if self.mass_before_weighing and self.mass_after_weighing:
    #     diff = self.mass_after_weighing - self.mass_before_weighing


class PerovskiteEvaporation(ArchiveSection):
    evaporation_sources = SubSection(
        links=['http://purl.obolibrary.org/obo/RO_0000057'],
        section_def=EvaporationSources,
        repeats=True,
    )


class Evaporation(ArchiveSection):
    m_def = Section(
        label_quantity='name', links=['https://purl.archive.org/tfsco/TFSCO_00002008']
    )

    name = Quantity(type=str)

    chemical = Quantity(
        links=['http://purl.obolibrary.org/obo/CHEBI_59999'],
        type=Reference(Chemical.m_def),
        a_eln=dict(component='ReferenceEditQuantity'),
    )

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

    pressure = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0001025',
            'https://purl.archive.org/tfsco/TFSCO_00005040',
        ],
        type=np.dtype(np.float64),
        unit=('mbar'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mbar',
            props=dict(minValue=0),
        ),
    )

    start_rate = Quantity(
        links=['http://purl.obolibrary.org/obo/PATO_0000161'],
        type=np.dtype(np.float64),
        unit=('angstrom/s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='angstrom/s',
            props=dict(minValue=0),
        ),
    )

    target_rate = Quantity(
        links=['http://purl.obolibrary.org/obo/PATO_0000161'],
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

    time_delay_to_start = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='s',
            props=dict(minValue=0),
        ),
    )

    substrate_temparature = Quantity(
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(
            component='NumberEditQuantity', defaultDisplayUnit='°C', label='Temperature'
        ),
    )

    def normalize(self, archive, logger):
        if self.chemical:
            if self.chemical.name:
                self.name = self.chemical.name

        if self.chemical_2:
            if self.chemical_2.name:
                self.name = self.chemical_2.name

        if self.thickness:
            if self.name:
                self.name += ' ' + str(self.thickness)
            else:
                self.name = str(self.thickness)


class OrganicEvaporation(Evaporation):
    temparature = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0000146',
            'https://purl.archive.org/tfsco/TFSCO_00002111',
        ],
        type=np.dtype(np.float64),
        unit=('°C'),
        shape=[2],
        a_eln=dict(
            component='NumberEditQuantity', defaultDisplayUnit='°C', label='Temperature'
        ),
    )


class InorganicEvaporation(Evaporation):
    power = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0001024',
            'https://purl.archive.org/tfsco/TFSCO_00002104',
        ],
        type=np.dtype(np.float64),
        unit=('W'),
        shape=[2],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='W',
            props=dict(minValue=0),
        ),
    )

    power_percentage = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0001024',
            'https://purl.archive.org/tfsco/TFSCO_00002104',
        ],
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity', props=dict(minValue=0)),
    )


class Evaporations(LayerDeposition):
    """Base class for evaporation of a sample"""

    organic_evaporation = SubSection(section_def=OrganicEvaporation, repeats=True)

    inorganic_evaporation = SubSection(section_def=InorganicEvaporation, repeats=True)

    perovskite_evaporation = SubSection(section_def=InorganicEvaporation, repeats=True)

    def normalize(self, archive, logger):
        super().normalize(archive, logger)

        self.method = 'Evaporation'
