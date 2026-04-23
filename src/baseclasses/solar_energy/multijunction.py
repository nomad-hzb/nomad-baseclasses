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
from nomad.metainfo import MEnum, Quantity, Section, SubSection


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

    number_of_connected_pixels = Quantity(
        type=np.dtype(np.int64),
        description=(
            'Number of pixels connected in this module. '
            'The total pixels on the substrate are tracked on the Substrate entry.'
        ),
        a_eln=dict(component='NumberEditQuantity'),
    )

    total_module_area = Quantity(
        type=np.dtype(np.float64),
        unit='cm**2',
        description='Total active area of the module (sum of connected pixel areas).',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='cm**2'),
    )

    geometric_fill_factor = Quantity(
        type=np.dtype(np.float64),
        description=(
            'Ratio of active area to total aperture area. '
            'Accounts for dead area from scribing lines (P1/P2/P3). '
            'Key figure of merit for module efficiency comparisons.'
        ),
        a_eln=dict(component='NumberEditQuantity'),
    )


class SubcellInfo(ArchiveSection):
    """
    Metadata for a single subcell within a multi-junction device.
    Position 1 = bottom cell (closest to substrate), increasing toward the top.

    Manufacturing process data for tracked subcells (e.g. perovskite) lives
    in dedicated process entries that reference this sample. For externally
    sourced subcells (e.g. CIGS, silicon), supplier provenance is captured here.
    """

    m_def = Section(label_quantity='material_system')

    position = Quantity(
        type=np.dtype(np.int64),
        description='Position in the junction stack. 1 = bottom (closest to substrate).',
        a_eln=dict(component='NumberEditQuantity'),
    )

    role = Quantity(
        type=MEnum('bottom', 'middle', 'top'),
        description='Role of this subcell in the multi-junction stack.',
        a_eln=dict(component='EnumEditQuantity'),
    )

    material_system = Quantity(
        type=str,
        description='Absorber material system of this subcell.',
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=[
                    'perovskite',
                    'CIGS',
                    'CdTe',
                    'silicon',
                    'organic',
                    'GaAs',
                    'InGaP',
                    'amorphous silicon',
                    'kesterite',
                ]
            ),
        ),
    )

    band_gap = Quantity(
        type=np.dtype(np.float64),
        unit='eV',
        description='Target or measured band gap of the absorber in this subcell.',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='eV'),
    )

    manufacturing_tracked = Quantity(
        type=bool,
        default=False,
        description=(
            'Whether the manufacturing of this subcell is tracked via process entries '
            'in NOMAD. If False, provenance is captured via supplier fields below.'
        ),
        a_eln=dict(component='BoolEditQuantity'),
    )

    supplier = Quantity(
        type=str,
        description='Supplier of this subcell (relevant for externally sourced cells, e.g. CIGS).',
        a_eln=dict(component='StringEditQuantity'),
    )

    supplier_id = Quantity(
        type=str,
        description='Supplier batch or wafer ID for traceability.',
        a_eln=dict(component='StringEditQuantity'),
    )

    cell_reference_id = Quantity(
        type=str,
        description=(
            'Lab ID of the NOMAD entry for this subcell if it is tracked as a '
            'separate sample (manufacturing_tracked = True).'
        ),
        a_eln=dict(component='StringEditQuantity'),
    )

    open_circuit_voltage = Quantity(
        type=np.dtype(np.float64),
        unit='V',
        description='Voc of this subcell measured as a standalone device (if available).',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='V'),
    )

    notes = Quantity(
        type=str,
        description='Additional notes or remarks about this subcell.',
        a_eln=dict(component='RichTextEditQuantity'),
    )


class MultijunctionConfiguration(ArchiveSection):
    """
    Configuration and metadata for multi-junction solar cells.
    Designed to be extensible from tandem (2J) to triple-junction (3J) and beyond
    by adding SubcellInfo entries.

    The top-level number_of_junctions on SolcarCellSample is kept in sync
    with len(subcells) during normalization.
    """

    m_def = Section()

    number_of_junctions = Quantity(
        type=np.dtype(np.int64),
        description='Total number of junctions (subcells) in the device (e.g. 2 for tandem).',
        a_eln=dict(component='NumberEditQuantity'),
    )

    interconnection_type = Quantity(
        type=MEnum(
            'monolithic (2-terminal)',
            'mechanically stacked (4-terminal)',
            'mechanically stacked (3-terminal)',
            'spectral splitting',
            'other',
        ),
        description=(
            'Electrical interconnection between subcells. '
            'Monolithic 2-terminal and mechanically stacked 4-terminal are the most '
            'common for perovskite/CIGS tandems.'
        ),
        a_eln=dict(component='EnumEditQuantity'),
    )

    current_matching = Quantity(
        type=bool,
        description=(
            'Whether the subcell photocurrents are matched. '
            'Critical for 2-terminal monolithic devices where the same current '
            'flows through all subcells.'
        ),
        a_eln=dict(component='BoolEditQuantity'),
    )

    recombination_layer = Quantity(
        type=str,
        description=(
            'Material of the recombination/tunnel junction layer between subcells '
            '(for monolithic devices).'
        ),
        a_eln=dict(component='StringEditQuantity'),
    )

    subcells = SubSection(
        section_def=SubcellInfo,
        repeats=True,
        description='Subcell metadata ordered from bottom (position 1) to top.',
    )
