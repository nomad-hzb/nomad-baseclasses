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
    solar_cell_area = Quantity(
        type=np.dtype(np.float64),
        unit='cm**2',
        shape=[],
        a_eln=dict(component='NumberEditQuantity'),
    )

    number_of_pixels = Quantity(
        type=np.dtype(np.float64), shape=[], a_eln=dict(component='NumberEditQuantity')
    )

    pixel_area = Quantity(
        type=np.dtype(np.float64),
        unit='cm**2',
        shape=[],
        a_eln=dict(component='NumberEditQuantity'),
    )

    substrate = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=['glass', 'Ti-foil', 'silicon wafer']),
        ),
    )

    conducting_material = Quantity(
        type=str,
        shape=['*'],
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=[
                    'SLG',
                    'FTO',
                    'ITO',
                    'PET',
                    'PEN',
                    'AZO',
                    'IZO',
                    'Graphene',
                    'Ti',
                    'Ag',
                    'Ag-nw',
                    'Ag-grid',
                    'Au',
                    'PDMS',
                ]
            ),
        ),
    )

    substrate_properties = SubSection(section_def=LayerProperties, repeats=True)

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
        super().normalize(archive, logger)
        add_solar_cell(archive)

        if self.substrate:
            # Set up the substrate materials list
            substrate_materials = [self.substrate]

            # Add conducting materials if present
            if self.conducting_material:
                substrate_materials.extend(self.conducting_material)

            # Assign the materials list to the proper field
            archive.results.properties.optoelectronic.solar_cell.substrate = (
                substrate_materials
            )

            # Handle substrate properties separately - use the proper field names
            if self.substrate_properties:
                # Create a properties dictionary or object to store the values
                props = {}

                # Use the correct property names as defined in LayerProperties
                if (
                    hasattr(self.substrate_properties, 'layer_thickness')
                    and self.substrate_properties.layer_thickness is not None
                ):
                    props['thickness'] = self.substrate_properties.layer_thickness

                if (
                    hasattr(self.substrate_properties, 'layer_transmission')
                    and self.substrate_properties.layer_transmission is not None
                ):
                    props['transmission'] = self.substrate_properties.layer_transmission

                if (
                    hasattr(self.substrate_properties, 'sheet_resistance')
                    and self.substrate_properties.layer_sheet_resistance is not None
                ):
                    props['sheet_resistance'] = (
                        self.substrate_properties.sheet_resistance
                    )

                # Assign the properties to a separate field
                archive.results.properties.optoelectronic.solar_cell.substrate_properties = props
