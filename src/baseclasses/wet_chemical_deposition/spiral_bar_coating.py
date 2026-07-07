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

from .wet_chemical_deposition import WetChemicalDeposition


class SpiralBarCoatingProperties(ArchiveSection):
    """Parameters of a spiral (wire-wound) bar / rod coating step."""

    bar_type = Quantity(
        type=str,
        shape=[],
        a_eln=dict(component='StringEditQuantity'),
        description='Designation of the wire-wound (Meyer) rod used, e.g. "RDS 24".',
    )

    wire_diameter = Quantity(
        type=np.dtype(np.float64),
        unit=('um'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='um',
            props=dict(minValue=0),
        ),
        description='Diameter of the wire wound around the bar, which sets the '
        'theoretical wet film thickness.',
    )

    coating_speed = Quantity(
        type=np.dtype(np.float64),
        unit=('mm/s'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mm/s',
            props=dict(minValue=0),
        ),
    )

    wet_film_thickness = Quantity(
        type=np.dtype(np.float64),
        unit=('um'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='um',
            props=dict(minValue=0),
        ),
        description='Theoretical wet film thickness set by the bar/wire geometry.',
    )

    dispensed_volume = Quantity(
        type=np.dtype(np.float64),
        unit=('uL'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='uL',
            props=dict(minValue=0),
        ),
        description='Volume of ink/adhesive dispensed ahead of the bar before '
        'drawdown.',
    )

    number_of_passes = Quantity(
        type=np.dtype(np.int32),
        shape=[],
        a_eln=dict(component='NumberEditQuantity', props=dict(minValue=0)),
    )


class SpiralBarCoating(WetChemicalDeposition):
    """Base class for spiral (wire-wound) bar / rod coating of a sample."""

    m_def = Section()

    properties = SubSection(section_def=SpiralBarCoatingProperties)

    def normalize(self, archive, logger):
        self.method = 'Spiral Bar Coating'
        super().normalize(archive, logger)
