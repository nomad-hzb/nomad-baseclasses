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

from .wet_chemical_deposition import WetChemicalDeposition

class MeshProperties(ArchiveSection):
    '''A screen mesh to enable the deposition of exactly the right amount of ink onto
      the substrate and holds the emulsion that makes patterning possible. It consists
      of nodes, threads, and the openings between them.'''
    
    mesh_material=Quantity(
        links=[],
        type=str,
        a_eln=dict(component='StringEditQuantity'),
        description=(
            'Material of screen mesh.'
        ),
    )

    mesh_count=Quantity(
        links=[],
        type=np.dtype(np.float64),
        a_eln=dict(
            component='NumberEditQuantity',
            props=dict(minValue=0),
        ),
        description='how many threads or nodes are in the mesh per unit of length '
        '(meshes/cm).',
    )

    mesh_thickness=Quantity(
        links=[],
        type=np.dtype(np.float64),
        unit = ('um'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='um',
            props=dict(minValue=0),
        ),
        description='The combined thickness of the overlapping threads.',
    )

    thread_diameter=Quantity(
        links=[],
        type=np.dtype(np.float64),
        unit = ('um'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='um',
            props=dict(minValue=0),
        ),
        description='Diameter of a thread of the mesh.',
    )

    mesh_opening=Quantity(
        links=[],
        type=np.dtype(np.float64),
        unit = ('um'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='um',
            props=dict(minValue=0),
        ),
        description='The empty area between a mesh.',
    ) 

    mesh_tension=Quantity(
        links=[],
        type=np.dtype(np.float64),
        unit = ('N/cm'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='N/cm',
            props=dict(minValue=0),
        ),
        description='Screen mesh tension measured by a tension meter.',
    )

    mesh_angle=Quantity(
        links=[],
        type=np.dtype(np.float64),
        unit = ('°'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='°',
            props=dict(minValue=0),
        ),
        description='The angle at which the mesh is mounted relative to the direction '
        'of the threads.',
    ) 

class ScreenPrintingProperties(ArchiveSection):
    screen_mesh = SubSection(section_def=MeshProperties, repeats=False)
    
    emulsion_material=Quantity(
        links=[],
        type=str,
        a_eln=dict(component='StringEditQuantity'),
        description=(
            'A photosensitive emulsion spread over the screen and dried.'
        ),
    )

    emulsion_thickness=Quantity(
        links=[],
        type=np.dtype(np.float64),
        unit = ('um'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='um',
            props=dict(minValue=0),
        ),
    )
    squeegee_material=Quantity(
        links=[],
        type=str,
        a_eln=dict(component='StringEditQuantity'),
        description=(
            'Material of the squeegee used for screen printing.'
        ),
    )

    squeegee_shape=Quantity(
        links=[],
        type=str,
        a_eln=dict(component='StringEditQuantity'),
        description=(
            'The shape of the queegee rubbers/blades, e.g. rectangle, diamond.'
        ),
    )
    
    squeegee_angle=Quantity(
        links=[],
        type=np.dtype(np.float64),
        unit = ('°'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='°',
            props=dict(minValue=0),
        ),
        description='The angle of the squeegee during the printing process.',
    ) 

    sp_speed = Quantity(
        links=[],
        type=np.dtype(np.float64),
        unit=('mm/s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mm/s',
            props=dict(minValue=0),
        ),
        description='The speed of squeegee printing the ink.',
    )
    
    sp_direction = Quantity(
        type=MEnum('Forward', 'Backward'),
        shape=[],
        a_eln=dict(component='EnumEditQuantity'),
        description=(
            'Moving direction of the squeegee with reference to the screen.'
        ),
    )

    sp_pressure=Quantity(
        links=[],
        type=np.dtype(np.float64),
        unit = ('bar'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='bar',
            props=dict(minValue=0),
        ),
        description='Pressure of printing squeegee.',
    ) 

    snap_off = Quantity(
        links=[],
        type=np.dtype(np.float64),
        unit = ('mm'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mm',
            props=dict(minValue=0),
        ),
        description='Distance between screen and substrate.',
    )

    sp_method = Quantity(
        type=MEnum('R2R', 'S2S'),
        shape=[],
        a_eln=dict(component='EnumEditQuantity'),
        description='Rotary screen(R2R) or Flatbed(S2S) screen printing.',
    )
    
class ScreenPrinting(WetChemicalDeposition):
    """Base class for the screen printing process of a sample"""

    m_def = Section(links=[])

    properties = SubSection(section_def=ScreenPrintingProperties)

    def normalize(self, archive, logger):
        self.method = 'Screen Printing'
        super().normalize(archive, logger)


