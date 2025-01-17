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


class CSSProcess(ArchiveSection):
    chemical = Quantity(
        links=['http://purl.obolibrary.org/obo/CHEBI_59999'],
        type=Reference(Chemical.m_def),
        a_eln=dict(component='ReferenceEditQuantity'),
    )

    chemical_2 = SubSection(
        links=['http://purl.obolibrary.org/obo/RO_0000057'],
        section_def=PubChemPureSubstanceSectionCustom,
    )

    material_state = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=['solid', 'liquid', 'gas']),
        ),
    )

    pressure = Quantity(
        links=[],
        type=np.dtype(np.float64),
        unit=('mbar'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mbar',
            props=dict(minValue=0),
        ),
    )

    source_temperature = Quantity(
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='°C',
        ),
    )

    substrate_temperature = Quantity(
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='°C',
        ),
    )

    substrate_source_distance = Quantity(
        type=np.dtype(np.float64),
        unit=('mm'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mm',
            props=dict(minValue=0),
        ),
    )

    thickness = Quantity(
        type=np.dtype(np.float64),
        unit=('nm'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='nm',
            props=dict(minValue=0),
        ),
    )

    deposition_time = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='s',
            props=dict(minValue=0),
        ),
    )

    carrier_gas = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=['N2', 'Ar', 'He', 'H2', 'O2', 'Air']),
        ),
    )

    comment = Quantity(type=str, a_eln=dict(component='RichTextEditQuantity'))


class CloseSpaceSublimation(LayerDeposition):
    """Base class for CSS of a sample"""

    process = SubSection(section_def=CSSProcess)

    def normalize(self, archive, logger):
        self.method = 'Close Space Sublimation'
        super().normalize(archive, logger)
