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
    SubSection)

from nomad.datamodel.data import ArchiveSection

from .wet_chemical_deposition import WetChemicalDeposition
from ..material_processes_misc import Annealing


class SprayPyrolysisProperties(ArchiveSection):

    temperature = Quantity(
        #Link to ontology class 'temperature' and 'temperature setting datum'
        links = ['http://purl.obolibrary.org/obo/PATO_0000146', 'https://purl.archive.org/tfsco/TFSCO_00002111'],
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'))

    time = Quantity(
        #Link to ontology class 'time' and 'time setting datum'
        links = ['http://purl.obolibrary.org/obo/PATO_0000165', 'https://purl.archive.org/tfsco/TFSCO_00005085'],
        type=np.dtype(np.float64),
        unit=('minute'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='minute'))


class SprayPyrolysis(WetChemicalDeposition):
    '''Base class for spray pyrolysis of a sample'''
    m_def = Section(
        #Link to ontology class 'Spray pyrolysis'
        links = ['http://purl.obolibrary.org/obo/CHMO_0001516']
    )

    properties = SubSection(section_def=SprayPyrolysisProperties)

    def normalize(self, archive, logger):
        super(SprayPyrolysis, self).normalize(archive, logger)

        self.method = "Spray Pyrolysis"
