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
        links=["https://purl.archive.org/tfsco/TFSCO/TFSCO_00003507"],
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
