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

from .. import BaseProcess


class LaminationSettings(ArchiveSection):
    temperature = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0000146',
            'https://purl.archive.org/tfsco/TFSCO_00002111',
        ],
        type=np.dtype(np.float64),
        unit=('°C'),
        shape=[],
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'),
    )

    time = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0000165',
            'https://purl.archive.org/tfsco/TFSCO_00005085',
        ],
        type=np.dtype(np.float64),
        unit=('s'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='seconds',
            props=dict(minValue=0),
        ),
    )

    pressure = Quantity(
        type=np.dtype(np.float64),
        unit=('MPa'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='MPa',
            props=dict(minValue=0),
        ),
    )

    force = Quantity(
        type=np.dtype(np.float64),
        unit=('N'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='N',
            props=dict(minValue=0),
        ),
    )

    area = Quantity(
        type=np.dtype(np.float64),
        unit=('mm^2'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mm^2',
            props=dict(minValue=0),
        ),
    )

    heat_up_time = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='seconds',
            props=dict(minValue=0),
        ),
    )

    cool_down_time = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='seconds',
            props=dict(minValue=0),
        ),
    )

    stamp_material = Quantity(
        type=str,
        shape=[],
        a_eln=dict(
            component='TextEditQuantity',
        ),
    )

    stamp_thickness = Quantity(
        type=np.dtype(np.float64),
        unit=('mm'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mm',
            props=dict(minValue=0),
        ),
    )

    stamp_area = Quantity(
        type=np.dtype(np.float64),
        unit=('mm^2'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mm^2',
            props=dict(minValue=0),
        ),
    )


class Lamination(BaseProcess):
    """Base class for lamination of a sample"""

    settings = SubSection(section_def=LaminationSettings)
