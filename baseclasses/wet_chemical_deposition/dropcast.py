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

from . import WetChemicalDeposition


class DropCastingProperties(ArchiveSection):
    suspension_concentration = Quantity(
        type=np.dtype(
            np.float64),
        a_eln=dict(
            component='NumberEditQuantity'))

    dropcast_amount = Quantity(
        #Link to ontology class 'volume' and 'volume setting datum'
        links = ['http://purl.obolibrary.org/obo/PATO_0000918', 'https://purl.archive.org/tfsco/TFSCO_00002158'],
        type=np.dtype(
            np.float64),
        unit=('ml'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='ml'))

    temperature = Quantity(
        #Link to ontology class 'temperature' and 'temperature setting datum'
        links = ['http://purl.obolibrary.org/obo/PATO_0000146', 'https://purl.archive.org/tfsco/TFSCO_00002111'],
        type=np.dtype(
            np.float64),
        unit=('°C'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='°C'))

    atmosphere = Quantity(
        #Link to ontology class 'atmosphere'
        links = ['https://purl.archive.org/tfsco/TFSCO_00001012'],
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=["N2O flow", "ambient"])
        ))


class DropCasting(WetChemicalDeposition):
    m_def = Section(
        #Link to ontology class 'Drop casting'
        links = ['https://purl.archive.org/tfsco/TFSCO_00002059'],
    )

    properties = SubSection(
        section_def=DropCastingProperties)

    def normalize(self, archive, logger):
        super(DropCasting,
              self).normalize(archive, logger)

        self.method = "Drop Casting"
