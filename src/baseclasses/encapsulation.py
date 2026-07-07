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

from . import LayerDeposition
from .material_processes_misc.lamination import LaminationSettings
from .product_info import ProductInfo
from .wet_chemical_deposition.blade_coating import BladeCoatingProperties
from .wet_chemical_deposition.slot_die_coating import SlotDieCoatingProperties
from .wet_chemical_deposition.spiral_bar_coating import SpiralBarCoatingProperties


class UVCuring(ArchiveSection):
    """Curing of a UV-curable adhesive using a UV-lamp."""

    lamp_type = Quantity(type=str, shape=[], a_eln=dict(component='StringEditQuantity'))

    wavelength = Quantity(
        type=np.dtype(np.float64),
        unit=('nm'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='nm',
            props=dict(minValue=0),
        ),
    )

    intensity = Quantity(
        type=np.dtype(np.float64),
        unit=('mW/cm**2'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mW/cm**2',
            props=dict(minValue=0),
        ),
    )

    time = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='s',
            props=dict(minValue=0),
        ),
    )

    belt_speed = Quantity(
        type=np.dtype(np.float64),
        unit=('mm/s'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mm/s',
            props=dict(minValue=0),
        ),
        description='Conveyor/belt speed under the UV lamp for in-line '
        '(e.g. roll-to-roll) curing.',
    )

    number_of_passes = Quantity(
        type=np.dtype(np.int32),
        shape=[],
        a_eln=dict(component='NumberEditQuantity', props=dict(minValue=0)),
    )

    atmosphere = Quantity(
        type=str,
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=['N2', 'ambient', 'Ar']),
        ),
    )


class BarrierFoilLamination(LaminationSettings):
    """Lamination of the barrier foil onto the (wet or pre-applied) adhesive layer."""

    barrier_foil = Quantity(
        type=str,
        shape=[],
        a_eln=dict(component='StringEditQuantity'),
        description='Name/product of the barrier foil laminated onto the adhesive.',
    )

    product_info = SubSection(
        section_def=ProductInfo, description='Product information'
    )

    line_speed = Quantity(
        type=np.dtype(np.float64),
        unit=('mm/s'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mm/s',
            props=dict(minValue=0),
        ),
        description='Web/line speed, for roll-to-roll lamination.',
    )


class AdhesiveApplication(ArchiveSection):
    """Application of the adhesive that bonds the barrier foil to the sample.

    Depending on the lab and equipment, this can be a wet chemical coating step
    (spiral bar coating, slot-die coating, blade coating, dispensing) of a
    UV-curable resin, or simply laminating a ready-made pressure sensitive
    adhesive (PSA) film, in which case no separate curing step is needed.
    """

    m_def = Section(label_quantity='method')

    method = Quantity(
        type=MEnum(
            'Spiral Bar Coating',
            'Slot Die Coating',
            'Blade Coating',
            'Dispensing',
            'Pressure Sensitive Adhesive Film',
            'Other',
        ),
        shape=[],
        a_eln=dict(component='EnumEditQuantity'),
    )

    adhesive_name = Quantity(
        type=str,
        shape=[],
        a_eln=dict(component='StringEditQuantity'),
        description='Name/product of the adhesive or pressure sensitive adhesive '
        '(PSA) film.',
    )

    product_info = SubSection(
        section_def=ProductInfo, description='Product information'
    )

    curable_by = Quantity(
        type=MEnum('UV', 'Heat', 'Pressure Only', 'Other'),
        shape=[],
        a_eln=dict(component='EnumEditQuantity'),
    )

    wet_thickness = Quantity(
        type=np.dtype(np.float64),
        unit=('um'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='um',
            props=dict(minValue=0),
        ),
    )

    spiral_bar_coating = SubSection(section_def=SpiralBarCoatingProperties)
    slot_die_coating = SubSection(section_def=SlotDieCoatingProperties)
    blade_coating = SubSection(section_def=BladeCoatingProperties)


class Encapsulation(LayerDeposition):
    """Base class for the encapsulation of a solar cell/module.

    Encapsulation is typically a lamination stack: an adhesive (a UV-curable
    resin or a pressure sensitive adhesive) is applied and a barrier foil is
    laminated on top of it, after which the adhesive may be cured (e.g. under a
    UV-lamp). This sequence can be applied to a single side of the sample (e.g.
    if the substrate itself is already a barrier foil) or to both sides.
    """

    processing_type = Quantity(
        type=MEnum('Sheet-to-Sheet (S2S)', 'Roll-to-Roll (R2R)'),
        shape=[],
        a_eln=dict(component='EnumEditQuantity'),
    )

    sides_encapsulated = Quantity(
        type=MEnum('Single Side', 'Both Sides'),
        shape=[],
        a_eln=dict(component='EnumEditQuantity'),
        description='Whether the encapsulation sequence below was applied to a '
        'single side of the sample (e.g. because the substrate itself is already '
        'a barrier foil) or to both sides.',
    )

    rewind = Quantity(
        type=bool,
        shape=[],
        a_eln=dict(component='BoolEditQuantity'),
        description='Whether the roll was rewound',
    )

    adhesive_application = SubSection(section_def=AdhesiveApplication)
    barrier_lamination = SubSection(section_def=BarrierFoilLamination)
    curing = SubSection(section_def=UVCuring)

    def normalize(self, archive, logger):
        if not self.method:
            self.method = 'Encapsulation'
        super().normalize(archive, logger)
