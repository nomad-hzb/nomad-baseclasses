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
from nomad.metainfo import MEnum, Quantity, Section


class ModuleConfiguration(ArchiveSection):
    """
    Tracks whether this solar cell device is a module, i.e. multiple pixels
    are electrically connected. This is orthogonal to the multi-junction concept:
    a tandem can also be a module.

    Note: The total number of pixels on the substrate is tracked on the
    Substrate section (number_of_pixels). This section captures which and
    how those pixels are connected at the device level.
    The scribing parameters (P1/P2/P3, laser settings, dead area) are tracked
    in the LaserScribing process entry and are not duplicated here.
    """

    m_def = Section()

    is_module = Quantity(
        type=bool,
        default=False,
        description='Whether this device has pixels electrically connected (module configuration).', 
        a_eln=dict(component='BoolEditQuantity'),
    )

    pixel_connection = Quantity(
        type=MEnum('Series', 'Parallel', 'Mixed'),
        description='How the pixels are electrically connected within the module.',
        a_eln=dict(component='EnumEditQuantity'),
    )

    module_active_area = Quantity(
        type=np.dtype(np.float64),
        unit='cm**2',
        description=(
            'Total active area of the module. Computed in normalization as '
            'substrate.active_area (falling back to pixel_area) × '
            'substrate.number_of_pixels.'
        ),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='cm**2'),
    )

    #module_dead_area = picks up from Substrate.dead_area
    
    #module_aperture_area = picks up from Substrate.aperture_area (sum of active and dead area)

    #module_geometrical_fill_factor = picks up for Substrate.geometrical_fill_factor

    module_dimension_after_encapsulation = Quantity(
        type=str,
        description=(
            'Physical dimensions of the module after encapsulation. '
            'Inherited from the encapsulation barrier foil dimension.'
        ),
        a_eln=dict(component='StringEditQuantity'),
    )

    # jv_data_recalculated_per_cell = Quantity(
    #     type=bool,
    #     description=(
    #         'Whether the JV data has been recalculated to average per-cell values. '
    #         'Preferred for modules to enable downstream comparisons with single cells.'
    #     ),
    #     a_eln=dict(component='BoolEditQuantity'),
    # )
