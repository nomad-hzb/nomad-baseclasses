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
from nomad.metainfo import Quantity

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

    conducting_material_thickness = Quantity(
        #links=['http://purl.obolibrary.org/obo/PATO_0000915'], took it from ALD, does it apply here too?
        type=np.dtype(np.float64),
        unit='nm',
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='nm',
            props=dict(minValue=0),
        ),
    )

    conducting_material_sheet_resistance = Quantity(
        type=np.dtype(np.float64),
        unit='ohm',  
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='ohm',
            props=dict(
                minValue=0,
                description="Sheet resistance in ohms per square (Ω/□)"
            ),
        ),
    )

    conducting_material_transmission = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity', props=dict(minValue=0)), #is described in percentage
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
