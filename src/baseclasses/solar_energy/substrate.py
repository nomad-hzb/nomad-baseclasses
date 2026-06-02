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
from nomad.datamodel.metainfo.eln import Entity
from nomad.metainfo import Quantity, SubSection

from baseclasses import LayerProperties

from ..helper.add_solar_cell import add_solar_cell


class Substrate(Entity):
    substrate_dimension = Quantity(
        type=str,
        description=(
            'Physical dimensions of the substrate '
            '(e.g. "10 cm × 10 cm"). '
            'Maps from "Sample dimension" in the batch mapping spreadsheet.'
        ),
        a_eln=dict(component='StringEditQuantity'),
    )

    solar_cell_area = Quantity(
        type=np.dtype(np.float64),
        unit='cm**2',
        shape=[],
        description=(
            'Sample area from the spreadsheet. Kept for legacy compatibility; '
            'in practice often used as pixel area.'
        ),
        a_eln=dict(component='NumberEditQuantity'),
    )

    pixel_area = Quantity(
        type=np.dtype(np.float64),
        unit='cm**2',
        shape=[],
        description=(
            'Total area of the cell. '
            'Defined as the overlap between front and back contacts.'
        ),
        a_eln=dict(component='NumberEditQuantity'),
    )

    active_area = Quantity(
        type=np.dtype(np.float64),
        unit='cm**2',
        shape=[],
        description=(
            'The effective area of the cell during IV and stability measurements '
            'under illumination. If measured with a mask, this corresponds to the '
            'area of the hole in the mask. Otherwise equals the pixel area.'
        ),
        a_eln=dict(component='NumberEditQuantity'),
    )

    dead_area = Quantity(
        type=np.dtype(np.float64),
        unit='cm**2',
        shape=[],
        description=(
            'Interconnect area of the cell, inactive to solar conversion. '
            'Includes scribing lines and borders between cells in a module.'
        ),
        a_eln=dict(component='NumberEditQuantity'),
    )

    aperture_area = Quantity(
        type=np.dtype(np.float64),
        unit='cm**2',
        shape=[],
        description=(
            'Sum of active area and dead area per cell. '
            'Not to be confused with the illumination aperture.'
        ),
        a_eln=dict(component='NumberEditQuantity'),
    )

    geometrical_fill_factor = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='Ratio of active area to the total aperture area.',
        a_eln=dict(component='NumberEditQuantity'),
    )

    number_of_pixels = Quantity(
        type=np.dtype(np.float64), shape=[], a_eln=dict(component='NumberEditQuantity')
    )

    substrate = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=[
                    'Glass',
                    'Ti-foil',
                    'silicon wafer',
                    'SLG',
                    'PET',
                    'Quartz',
                    'PDMS',
                ]
            ),
        ),
    )

    conducting_material = Quantity(
        type=str,
        shape=['*'],
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=[
                    'FTO',
                    'ITO',
                    'PEN',
                    'AZO',
                    'IZO',
                    'Graphene',
                    'Ti',
                    'Ag',
                    'Ag-nw',
                    'Ag-grid',
                    'Au',
                ]
            ),
        ),
    )

    substrate_properties = SubSection(
        section_def=LayerProperties,
        repeats=True,
    )

    # back_contact = Quantity(
    #     type=str,
    #     shape=['*'],
    #     a_eln=dict(
    #         component='EnumEditQuantity',
    #         props=dict(
    #             suggestions=['Au', 'Ag', 'Al', 'Carbon', 'MoO3', 'Cu', 'Ca',
    #                          'ITO', 'MoOx', 'FTO', 'SLG', 'PEDOT:PSS'])
    #     ))

    def normalize(self, archive, logger):
        from baseclasses.helper.naming_normalizer import (
            layer_material_name_normalizer,
            substrate_normalizer,
        )

        if self.substrate is not None:
            self.substrate = substrate_normalizer.normalize(self.substrate)
        if self.conducting_material:
            self.conducting_material = [
                layer_material_name_normalizer.normalize(m)
                for m in self.conducting_material
            ]

        super().normalize(archive, logger)
        add_solar_cell(archive)
        if self.substrate:
            if self.conducting_material:
                archive.results.properties.optoelectronic.solar_cell.substrate = [
                    self.substrate
                ] + self.conducting_material
            else:
                archive.results.properties.optoelectronic.solar_cell.substrate = [
                    self.substrate
                ]
