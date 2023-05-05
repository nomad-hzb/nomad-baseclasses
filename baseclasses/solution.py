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
    SubSection,
    Section,
    Reference,
    MEnum, SectionProxy)
from nomad.datamodel.data import ArchiveSection

from .chemical import Solvent, Powder, LiquidSolute
from nomad.datamodel.metainfo.eln import Entity


class SolutionPowder(ArchiveSection):
    m_def = Section(label_quantity='name')
    name = Quantity(type=str)

    chemical = Quantity(
        type=Reference(Powder.m_def),
        a_eln=dict(component='ReferenceEditQuantity'))

    powder_mass = Quantity(
        type=np.dtype(np.float64),
        unit=('mg'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mg'))

    def normalize(self, archive, logger):

        if self.chemical and self.chemical.name:
            if self.powder_mass:
                self.name = self.chemical.name + ' ' + str(self.powder_mass)
            else:
                self.name = self.chemical.name


class SolutionLiquidSolute(ArchiveSection):
    m_def = Section(label_quantity='name')
    name = Quantity(type=str)

    chemical = Quantity(
        type=Reference(LiquidSolute.m_def),
        a_eln=dict(component='ReferenceEditQuantity'))

    solute_volume = Quantity(
        type=np.dtype(np.float64),
        unit=('ml'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='ml'))

    def normalize(self, archive, logger):

        if self.chemical and self.chemical.name:
            if self.solute_volume:
                self.name = self.chemical.name + ' ' + str(self.solute_volume)
            else:
                self.name = self.chemical.name


class SolutionSolvent(ArchiveSection):
    m_def = Section(label_quantity='name')

    name = Quantity(type=str)

    solvent = Quantity(
        type=Reference(Solvent.m_def),
        a_eln=dict(component='ReferenceEditQuantity'))

    solvent_volume = Quantity(
        type=np.dtype(np.float64),
        unit=('ml'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='ml'))

    def normalize(self, archive, logger):

        if self.solvent and self.solvent.name:
            if self.solvent_volume:
                self.name = self.solvent.name + ' ' + str(self.solvent_volume)
            else:
                self.name = self.solvent.name


class OtherSolution(ArchiveSection):
    m_def = Section(label_quantity='name')

    name = Quantity(type=str)

    solution = Quantity(
        type=Reference(SectionProxy("Solution")),
        a_eln=dict(component='ReferenceEditQuantity'))

    solution_volume = Quantity(
        type=np.dtype(np.float64),
        unit=('ml'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='ml'))

    def normalize(self, archive, logger):

        if self.solution and self.solution.name:
            if self.solution_volume:
                self.name = self.solution.name + \
                    ' ' + str(self.solution_volume)
            else:
                self.name = self.solution.name


class Solution(Entity):
    '''Base class for a solution'''

    method = Quantity(
        type=MEnum('Shaker', 'Ultrasoncic', 'Waiting'),
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
        ))

    solvent_ratio = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'))

    temperature = Quantity(
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'))

    time = Quantity(
        type=np.dtype(
            np.float64),
        unit=('minute'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='minute'))

    speed = Quantity(
        type=np.dtype(np.float64),
        unit=('Hz'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='rpm'))

    powder = SubSection(
        section_def=SolutionPowder, repeats=True)

    liquid_solute = SubSection(
        section_def=SolutionLiquidSolute, repeats=True)

    solvent = SubSection(
        section_def=SolutionSolvent, repeats=True)

    other_solution = SubSection(
        section_def=OtherSolution, repeats=True)


class Ink(Solution):
    pass
