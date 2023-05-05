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

from nomad.metainfo import (
    Quantity,
    Reference,
    SubSection)
from nomad.datamodel.data import ArchiveSection

from ..solution import Solution
from .. import LayerDeposition
from ..material_processes_misc import Annealing


class SlotDieCoatingProperties(ArchiveSection):

    solution = Quantity(
        type=Reference(Solution.m_def),
        shape=['*'],
        a_eln=dict(component='ReferenceEditQuantity'))

    pre_pump = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        a_eln=dict(component='NumberEditQuantity', props=dict(minValue=0)))

    speed = Quantity(
        type=np.dtype(
            np.float64),
        unit=('mm/s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mm/s',
            props=dict(
                minValue=0)))

    gap = Quantity(
        type=np.dtype(
            np.float64),
        unit=('mm'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mm',
            props=dict(
                minValue=0)))

    coating_pump_rate = Quantity(
        type=np.dtype(
            np.float64),
        unit=('ml/minute'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='ml/minute', props=dict(minValue=0)))

    length_of_die_head = Quantity(
        type=np.dtype(
            np.float64),
        unit=('mm'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mm',
            props=dict(
                minValue=0)))

    temperature = Quantity(
        type=np.dtype(
            np.float64),
        unit=('°C'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='°C',
            props=dict(
                minValue=0)))

    air_knife_pressure = Quantity(
        type=np.dtype(
            np.float64),
        unit=('mbar'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mbar',
            props=dict(
                minValue=0)))


class SlotDieCoating(LayerDeposition):
    '''Spin Coating'''

    properties = SubSection(section_def=SlotDieCoatingProperties)
    annealing = SubSection(section_def=Annealing)

    def normalize(self, archive, logger):
        super(SlotDieCoating, self).normalize(archive, logger)

        self.method = "Slot Die Coating"
