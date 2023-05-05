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

from nomad.metainfo import (Quantity, Reference, SubSection)
from nomad.datamodel.data import ArchiveSection

from ..chemical import Solid
from .. import LayerDeposition


class PVDProcess(ArchiveSection):

    target = Quantity(
        type=Reference(Solid.m_def),
        shape=['*'],
        a_eln=dict(component='ReferenceEditQuantity'))

    power = Quantity(
        type=np.dtype(
            np.float64),
        unit=('W'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='W',
            props=dict(
                minValue=0)))

    pressure = Quantity(
        type=np.dtype(
            np.float64),
        unit=('ubar'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='ubar',
            props=dict(
                minValue=0)))

    time = Quantity(
        type=np.dtype(
            np.float64),
        unit=('s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='s',
            props=dict(
                minValue=0)))

    rotation_speed = Quantity(
        type=np.dtype(np.float64),
        unit=('1/s'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='1/s'))

    temperature = Quantity(
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'))

    voltage = Quantity(
        type=np.dtype(
            np.float64),
        unit=('V'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='V'))


class PVDeposition(LayerDeposition):
    '''Base class for evaporation of a sample'''

    process = SubSection(
        section_def=PVDProcess)

    def normalize(self, archive, logger):
        super(PVDeposition, self).normalize(archive, logger)

        self.method = "Physical Vapour Deposition"
