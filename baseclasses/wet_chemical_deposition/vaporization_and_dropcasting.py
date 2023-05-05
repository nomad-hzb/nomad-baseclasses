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
    Section,
    SubSection,
    Reference,
    Datetime)
from nomad.datamodel.data import ArchiveSection

from ..solution import Solution
from ..chemical import Chemical
from .. import LayerDeposition


class PrecursorSolution(ArchiveSection):

    m_def = Section(label_quantity='name')
    name = Quantity(type=str)

    solution = Quantity(
        type=Reference(Solution.m_def),
        a_eln=dict(component='ReferenceEditQuantity'))

    solution_volume = Quantity(
        type=np.dtype(
            np.float64),
        unit=('ml'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='ml',
            props=dict(
                minValue=0)))

    def normalize(self, archive, logger):

        if self.solution and self.solution.name:
            if self.solution_volume:
                self.name = self.solution.name + \
                    ' ' + str(self.solution_volume)
            else:
                self.name = self.solution.name


class AntiSolvent(ArchiveSection):

    m_def = Section(label_quantity='name')
    name = Quantity(type=str)

    anti_solvent = Quantity(
        type=Reference(Chemical.m_def),
        a_eln=dict(component='ReferenceEditQuantity'))

    anti_solvent_volume = Quantity(
        type=np.dtype(
            np.float64),
        unit=('ml'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='ml',
            props=dict(
                minValue=0)))

    anti_solvent_dropping_time = Quantity(
        type=np.dtype(
            np.float64), unit=('s'), a_eln=dict(
            component='NumberEditQuantity', defaultDisplayUnit='s', props=dict(
                minValue=0)))

    def normalize(self, archive, logger):

        if self.anti_solvent and self.anti_solvent.name:
            if self.anti_solvent_volume:
                self.name = self.anti_solvent.name + \
                    ' ' + str(self.anti_solvent_volume)
            else:
                self.name = self.anti_solvent.name


class VaporizationProperties(ArchiveSection):

    temperature = Quantity(
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'))

    initial_time = Quantity(
        type=Datetime,
        a_eln=dict(component='DateTimeEditQuantity'))


class HotPlateProperties(ArchiveSection):

    temperature = Quantity(
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'))

    time_on_hotplate = Quantity(
        type=np.dtype(
            np.float64),
        unit=('minute'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='minute',
            props=dict(
                minValue=0)))


class VaporizationAndDropCasting(LayerDeposition):
    '''Base class for spin coating of a sample'''

    small_vial = SubSection(
        section_def=PrecursorSolution, repeats=True)

    big_vial = SubSection(
        section_def=AntiSolvent, repeats=True)

    vaporization_properties = SubSection(
        section_def=VaporizationProperties, repeats=True)

    hotplate_properties = SubSection(
        section_def=HotPlateProperties, repeats=True)

    def normalize(self, archive, logger):
        super(VaporizationAndDropCasting, self).normalize(archive, logger)
        self.method = "Vaporization and Drop Casting"
