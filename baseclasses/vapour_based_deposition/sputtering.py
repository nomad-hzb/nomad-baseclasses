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
from nomad.metainfo import (Quantity, Reference, SubSection, Section)

from ..chemical import Chemical
from .. import LayerDeposition
from nomad.datamodel.metainfo.basesections import PubChemPureSubstanceSection


class SputteringProcess(ArchiveSection):

    target = Quantity(
        #Link to ontology class 'pvd source'
        links = ['https://purl.archive.org/tfsco/TFSCO_00002035'],
        type=Reference(Chemical.m_def),
        a_eln=dict(component='ReferenceEditQuantity'))

    target_2 = SubSection(
        #Link to ontology class 'pvd source'
        links = ['https://purl.archive.org/tfsco/TFSCO_00002035'],
        section_def=PubChemPureSubstanceSection)

    thickness = Quantity(
        #Link to ontology class 'thickness'
        links = ['http://purl.obolibrary.org/obo/PATO_0000915'],
        type=np.dtype(
            np.float64),
        unit=('nm'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='nm',
            props=dict(
                minValue=0)))

    gas = Quantity(
        #Link to ontology class 'chemical substance'
        links = ['http://purl.obolibrary.org/obo/CHEBI_59999'],
        type=Reference(Chemical.m_def),
        a_eln=dict(component='ReferenceEditQuantity'))

    source = Quantity(
        #Link to ontology class 'pvd source'
        links = ['https://purl.archive.org/tfsco/TFSCO_00002035'],
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=[
                    '1',
                    '2',
                    '3',
                    '4',
                ])))

    pressure = Quantity(
        #Link to ontology class 'pressure' and 'pressure setting datum'
        links = ['http://purl.obolibrary.org/obo/PATO_0001025','https://purl.archive.org/tfsco/TFSCO_00005040'],
        type=np.dtype(
            np.float64),
        unit=('mbar'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mbar',
            props=dict(
                minValue=0)))

    capman_pressure = Quantity(
        #Link to ontology class 'pressure' and 'pressure setting datum'
        links = ['http://purl.obolibrary.org/obo/PATO_0001025','https://purl.archive.org/tfsco/TFSCO_00005040'],
        type=np.dtype(
            np.float64),
        unit=('mmmHg'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mmmHg',
            props=dict(
                minValue=0)))

    temperature = Quantity(
        #Link to ontology class 'temperature' and 'temperature setting datum'
        links = ['http://purl.obolibrary.org/obo/PATO_0000146','https://purl.archive.org/tfsco/TFSCO_00002071'],
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'))

    burn_in_time = Quantity(
        #Link to ontology class 'time' and 'time setting datum' (missing class)
        links = ['http://purl.obolibrary.org/obo/PATO_0000165','https://purl.archive.org/tfsco/TFSCO_00005085'],
        type=np.dtype(
            np.float64),
        unit=('s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='s',
            props=dict(
                minValue=0)))

    deposition_time = Quantity(
        #Link to ontology class 'time' and 'time setting datum'
        links = ['http://purl.obolibrary.org/obo/PATO_0000165','https://purl.archive.org/tfsco/TFSCO_00005085'],
        type=np.dtype(
            np.float64),
        unit=('s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='s',
            props=dict(
                minValue=0)))

    power = Quantity(
        #Link to ontology class 'power' and 'power setting datum'
        links = ['http://purl.obolibrary.org/obo/PATO_0001024','https://purl.archive.org/tfsco/TFSCO_00002104'],
        type=np.dtype(
            np.float64),
        unit=('W'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='W', props=dict(minValue=0)))

    voltage = Quantity(
        type=np.dtype(
            np.float64),
        unit=('V'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='V'))

    gas_flow_rate = Quantity(
        #Link to ontology class 'gas flow rate' and 'gas flow rate setting datum'
        links = ['https://purl.archive.org/tfsco/TFSCO_00002114','https://purl.archive.org/tfsco/TFSCO_00002108'],
        type=np.dtype(
            np.float64),
        unit=('cm**3/minute'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='cm**3/minute', props=dict(minValue=0)))


class Sputtering(LayerDeposition):
    '''Base class for evaporation of a sample'''
    m_def = Section(
        #Link to ontology class 'sputter deposition'
        links = ['http://purl.obolibrary.org/obo/CHMO_0001364']
    )

    processes = SubSection(
        section_def=SputteringProcess, repeats=True)

    def normalize(self, archive, logger):
        super(Sputtering, self).normalize(archive, logger)

        self.method = "Sputtering"
