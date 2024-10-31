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
from nomad.metainfo import Quantity, Reference, Section

from .. import BaseProcess
from ..chemical import Chemical


class CleaningTechnique(ArchiveSection):
    time = Quantity(
        type=np.dtype(
            np.float64),
        unit=('minute'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='minute'))


class SolutionCleaning(CleaningTechnique):
    '''Base class for cleaning of a sample'''
    m_def = Section(label_quantity='name')
    name = Quantity(
        type=str
    )
    solvent = Quantity(
        links=['https://w3id.org/nfdi4cat/voc4cat_0007246'],
        type=Reference(Chemical.m_def),
        a_eln=dict(component='ReferenceEditQuantity'))

    temperature = Quantity(
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'))

    def normalize(self, archive, logger):

        if self.solvent:
            if self.solvent.name:
                self.name = self.solvent.name


class UVCleaning(CleaningTechnique):
    '''Base class for cleaning of a sample'''

    pressure = Quantity(
        type=np.dtype(np.float64),
        unit=('mbar'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mbar'))


class PlasmaCleaning(CleaningTechnique):
    '''Base class for cleaning of a sample'''

    pressure = Quantity(
        type=np.dtype(np.float64),
        unit=('mbar'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mbar'))

    plasma_type = Quantity(
        type=str,
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=['Oxygen', 'Nitrogen'])
        ))


class Cleaning(BaseProcess):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'user', 'author']))

    def normalize(self, archive, logger):
        super(Cleaning,
              self).normalize(archive, logger)

        self.method = "Cleaning"
