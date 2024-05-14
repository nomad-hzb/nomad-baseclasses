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

from nomad.metainfo import (Quantity, SubSection, Section)
from nomad.datamodel.data import ArchiveSection

from nomad.datamodel.metainfo.basesections import PubChemPureSubstanceSection
from .. import LayerDeposition


class ALDProperties(ArchiveSection):
    m_def = Section(label_quantity='name')
    name = Quantity(
        type=str
    )

    chemical_2 = SubSection(
        links=['http://purl.obolibrary.org/obo/RO_0000057'],
        section_def=PubChemPureSubstanceSection)

    source = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=[
                    'LTE1',
                    'LTE2',
                    'LTE3',
                    'LTE4',
                    'ULTE1',
                    'ULTE2'])))

    thickness = Quantity(
        links = ['http://purl.obolibrary.org/obo/PATO_0000915'],
        type=np.dtype(np.float64),
        unit=('nm'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='nm',
            props=dict(
                minValue=0)))

    temperature = Quantity(
        links = ['http://purl.obolibrary.org/obo/PATO_0000146','https://purl.archive.org/tfsco/TFSCO_00002111'],
        type=np.dtype(
            np.float64),
        unit=('°C'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='°C'
        ))

    rate = Quantity(
        links = ['https://purl.archive.org/tfsco/TFSCO_00002110'],
        type=np.dtype(
            np.float64),
        unit=('angstrom/s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='angstrom/s', props=dict(minValue=0)))

    time = Quantity(
        links = ['http://purl.obolibrary.org/obo/PATO_0000165', 'https://purl.archive.org/tfsco/TFSCO_00005085'],
        type=np.dtype(
            np.float64),
        unit=('s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='s',
            props=dict(
                minValue=0)))

    def normalize(self, archive, logger):

        if self.chemical_2:
            if self.chemical_2.name:
                self.name = self.chemical_2.name

        if self.thickness:
            if self.name:
                self.name += ' ' + str(self.thickness)
            else:
                self.name = str(self.thickness)


class AtomicLayerDeposition(LayerDeposition):
    '''Base class for evaporation of a sample'''

    m_def = Section(
        links = ['http://purl.obolibrary.org/obo/CHMO_0001311']
    )

    properties = SubSection(
        section_def=ALDProperties)

    def normalize(self, archive, logger):
        super(AtomicLayerDeposition, self).normalize(archive, logger)

        self.method = "Atomic Layer Deposition"
