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

from nomad.metainfo import (Quantity, Reference, SubSection, Section)
from nomad.datamodel.data import ArchiveSection

from ..chemical import Chemical
from nomad.datamodel.metainfo.basesections import PubChemPureSubstanceSection
from .. import LayerDeposition


class PVDProcess(ArchiveSection):

    target = Quantity(
        links = ['https://purl.archive.org/tfsco/TFSCO_00002035'],
        type=Reference(Chemical.m_def),
        shape=['*'],
        a_eln=dict(component='ReferenceEditQuantity'))

    target_2 = SubSection(
        links=['http://purl.obolibrary.org/obo/OBI_0000295','http://purl.obolibrary.org/obo/OBI_0000293'],
        section_def=PubChemPureSubstanceSection, repeats=True)

    power = Quantity(
        links = ['http://purl.obolibrary.org/obo/PATO_0001024','https://purl.archive.org/tfsco/TFSCO_00002104'],
        type=np.dtype(
            np.float64),
        unit=('W'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='W',
            props=dict(
                minValue=0)))

    pressure = Quantity(
        links = ['https://purl.archive.org/tfsco/TFSCO_00001094'],
        type=np.dtype(
            np.float64),
        unit=('ubar'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='ubar',
            props=dict(
                minValue=0)))

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

    rotation_speed = Quantity(
        links = ['https://purl.archive.org/tfsco/TFSCO_00002026','https://purl.archive.org/tfsco/TFSCO_00002005'],
        type=np.dtype(np.float64),
        unit=('1/s'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='1/s'))

    temperature = Quantity(
        links = ['http://purl.obolibrary.org/obo/PATO_0000146','https://purl.archive.org/tfsco/TFSCO_00002111'],
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'))

    voltage = Quantity(
        type=np.dtype(
            np.float64),
        unit=('V'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='V'))


class PVDeposition(LayerDeposition):
    '''Base class for evaporation of a sample'''
    m_def = Section(
        links = ['http://purl.obolibrary.org/obo/CHMO_0001356'],
    )

    process = SubSection(
        section_def=PVDProcess)

    def normalize(self, archive, logger):
        super(PVDeposition, self).normalize(archive, logger)

        self.method = "Physical Vapour Deposition"
