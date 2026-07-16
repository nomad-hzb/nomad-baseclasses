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

from .. import LayerDeposition, LayerProperties
from ..product_info import ProductInfo
from .lamination import LaminationSettings


class UVCuring(ArchiveSection):
    """Curing of a UV-curable adhesive using a UV-lamp."""

    lamp_details = Quantity(
        type=str, shape=[], a_eln=dict(component='StringEditQuantity')
    )

    wavelength = Quantity(
        links=['http://purl.obolibrary.org/obo/PATO_0001242'],
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
        links=['https://purl.archive.org/tfsco/TFSCO_00001128'],
        type=np.dtype(np.float64),
        unit=('mW/cm**2'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mW/cm**2',
            props=dict(minValue=0),
        ),
    )

    exposure_time = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='s',
            props=dict(minValue=0),
        ),
    )

    distance = Quantity(
        links=['https://purl.archive.org/tfsco/TFSCO_00005720'],
        type=np.dtype(np.float64),
        unit=('mm'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mm',
            props=dict(minValue=0),
        ),
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
        type=str,
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=[
                    'Spiral Bar Coating',
                    'Slot Die Coating',
                    'Blade Coating',
                    'Dispensing',
                    'Pressure Sensitive Adhesive Film',
                    'Other',
                ]
            ),
        ),
    )

    adhesive_layer_info = SubSection(
        section_def=LayerProperties, description='Product information'
    )


class Encapsulation(LayerDeposition):
    """Base class for the encapsulation of a solar cell/module.

    Encapsulation is typically a lamination stack: an adhesive (a UV-curable
    resin or a pressure sensitive adhesive) is applied and a barrier foil is
    laminated on top of it, after which the adhesive may be cured (e.g. under a
    UV-lamp). This sequence can be applied to a single side of the sample (e.g.
    if the substrate itself is already a barrier foil) or to both sides.
    """

    encapsulation_method = Quantity(
        type=str,
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=['Sheet-to-Sheet (S2S)', 'Roll-to-Roll (R2R)']),
        ),
    )

    sides_encapsulated = Quantity(
        type=str,
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=['Single Side', 'Both Sides']),
        ),
        description='Whether the encapsulation sequence below was applied to a '
        'single side of the sample (e.g. because the substrate itself is already '
        'a barrier foil) or to both sides.',
    )

    adhesive_application = SubSection(section_def=AdhesiveApplication)
    barrier_lamination = SubSection(section_def=BarrierFoilLamination)
    curing = SubSection(section_def=UVCuring)

    def normalize(self, archive, logger):
        if not self.method:
            self.method = 'Encapsulation'
        super().normalize(archive, logger)
