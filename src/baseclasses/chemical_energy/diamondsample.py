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
from nomad.metainfo import Quantity, SubSection

from .cesample import CENSLISample


class DiamondProperties(ArchiveSection):
    diamond_type = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=[
                    'Single Crytal',
                    'Polycrystal',
                    'Nanostructured',
                    'Nanodiamonds',
                ]
            ),
        ),
    )

    diamond_type_comment = Quantity(
        type=str, a_eln=dict(component='StringEditQuantity')
    )

    surface_orientation = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity', props=dict(suggestions=['<100>', '<111>'])
        ),
    )

    doping = Quantity(
        links=['https://w3id.org/nfdi4cat/voc4cat_0000015'],
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=['None', 'B', 'N', 'P', 'unknown']),
        ),
    )

    doping_level = Quantity(
        type=np.dtype(np.float64), a_eln=dict(component='NumberEditQuantity')
    )

    surface_termination = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=['H', 'O', 'N', 'F', 'mixed', 'unknown']),
        ),
    )


class DiamondSample(CENSLISample):
    diamond_properties = SubSection(section_def=DiamondProperties)

    def normalize(self, archive, logger):
        super().normalize(archive, logger)
