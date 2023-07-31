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
from .wet_chemical_deposition import WetChemicalDeposition
from ..material_processes_misc import Annealing, AirKnifeGasQuenching


class SlotDieCoatingProperties(ArchiveSection):

    flow_rate = Quantity(
        type=np.dtype(
            np.float64),
        unit=('ml/minute'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='ml/minute', props=dict(minValue=0)))

    slot_die_head_width = Quantity(
        type=np.dtype(
            np.float64),
        unit=('mm'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mm',
            props=dict(
                minValue=0)))

    slot_die_shim_width = Quantity(
        type=np.dtype(
            np.float64),
        unit=('mm'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mm',
            props=dict(
                minValue=0)))

    slot_die_shim_thickness = Quantity(
        type=np.dtype(
            np.float64),
        unit=('mm'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mm',
            props=dict(
                minValue=0)))

    slot_die_head_distance_to_thinfilm = Quantity(
        type=np.dtype(
            np.float64),
        unit=('mm'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mm',
            props=dict(
                minValue=0)))
    slot_die_head_speed = Quantity(
        type=np.dtype(
            np.float64),
        unit=('mm/s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mm/s',
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


class SlotDieCoating(WetChemicalDeposition):
    '''Spin Coating'''

    properties = SubSection(section_def=SlotDieCoatingProperties)

    def normalize(self, archive, logger):
        super(SlotDieCoating, self).normalize(archive, logger)

        self.method = "Slot Die Coating"
