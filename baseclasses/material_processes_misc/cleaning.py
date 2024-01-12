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
    Section, SubSection)
from nomad.datamodel.data import ArchiveSection

from .. import BaseProcess
from ..chemical import Chemical
from nomad.datamodel.metainfo.basesections import PubChemPureSubstanceSection


class CleaningTechnique(ArchiveSection):
    time = Quantity(
        #Link to ontology class 'time' and 'time setting datum'
        links = ['http://purl.obolibrary.org/obo/PATO_0000165', 'http://www.semanticweb.org/ot2661/ontologies/2022/8/TFSCO#TFSCO_00005085'],
        type=np.dtype(
            np.float64),
        unit=('minute'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='minute', props=dict(minValue=0)))


class SolutionCleaning(CleaningTechnique):
    '''Base class for cleaning of a sample'''
    m_def = Section(
        #Link to ontology class 'solvent cleaning'
        links = ['http://www.semanticweb.org/ot2661/ontologies/2022/8/TFSCO#TFSCO_00001042'],
        label_quantity='name')
    name = Quantity(
        type=str
    )
    solvent = Quantity(
        #Link to ontology class 'solvent'
        links = ['http://www.semanticweb.org/ot2661/ontologies/2022/8/TFSCO#TFSCO_00000026'],
        type=Reference(Chemical.m_def),
        a_eln=dict(component='ReferenceEditQuantity'))

    solvent_2 = SubSection(
        #Link to ontology class 'solvent'
        links = ['http://www.semanticweb.org/ot2661/ontologies/2022/8/TFSCO#TFSCO_00000026'],
        section_def=PubChemPureSubstanceSection)

    temperature = Quantity(
        #Link to ontology class 'temperature' and 'temperature setting datum'
        links = ['http://purl.obolibrary.org/obo/PATO_0000146','http://www.semanticweb.org/ot2661/ontologies/2022/8/TFSCO#TFSCO_00002111'],
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'))

    def normalize(self, archive, logger):

        if self.solvent:
            if self.solvent.name:
                self.name = self.solvent.name

        if self.solvent_2:
            if self.solvent_2.name:
                self.name = self.solvent_2.name


class UVCleaning(CleaningTechnique):
    '''Base class for cleaning of a sample'''
    m_def = Section(
        #Link to ontology class 'uv cleaning'
        links = ['http://www.semanticweb.org/ot2661/ontologies/2022/8/TFSCO#TFSCO_00001043'],
    )

    pressure = Quantity(
        #Link to ontology class 'presssure', Link to ontology class 'pressure setting datum'
        links = ['http://purl.obolibrary.org/obo/PATO_0001025','http://www.semanticweb.org/ot2661/ontologies/2022/8/TFSCO#TFSCO_00005040'],
        type=np.dtype(
            np.float64),
        unit=('mbar'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mbar',
            props=dict(
                minValue=0)))


class PlasmaCleaning(CleaningTechnique):
    '''Base class for cleaning of a sample'''
    m_def = Section(
        #Link to ontology class 'plasma cleaning'
        links = ['http://www.semanticweb.org/ot2661/ontologies/2022/8/TFSCO#TFSCO_00001044'],
    )

    pressure = Quantity(
        #Link to ontology class 'presssure', Link to ontology class 'pressure setting datum'
        links = ['http://purl.obolibrary.org/obo/PATO_0001025','http://www.semanticweb.org/ot2661/ontologies/2022/8/TFSCO#TFSCO_00005040'],
        type=np.dtype(
            np.float64),
        unit=('mbar'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mbar',
            props=dict(
                minValue=0)))

    power = Quantity(
        #Link to ontology class 'power', Link to ontology class 'power setting datum'
        links = ['http://purl.obolibrary.org/obo/PATO_0001024','http://www.semanticweb.org/ot2661/ontologies/2022/8/TFSCO#TFSCO_00002104'],
        type=np.dtype(
            np.float64),
        unit=('W'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='W',
            props=dict(
                minValue=0)))

    plasma_type = Quantity(
        #Link to ontology class 'plasma'
        links = ['http://www.semanticweb.org/ot2661/ontologies/2022/8/TFSCO#TFSCO_00005019'],
        type=str,
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=['Oxygen', 'Nitrogen', 'Argon'])
        ))


class Cleaning(BaseProcess):
    m_def = Section(
        #Link to ontology class 'cleaning'
        links = ['http://www.semanticweb.org/ot2661/ontologies/2022/8/TFSCO#TFSCO_00000068'],
        a_eln=dict(
            hide=[
                'lab_id', 'user', 'author']))

    def normalize(self, archive, logger):
        super(Cleaning,
              self).normalize(archive, logger)

        self.method = "Cleaning"
