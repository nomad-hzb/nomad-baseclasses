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
    Reference)
from nomad.datamodel.data import ArchiveSection

from nomad.datamodel.metainfo.eln import Entity

from ..solution import Solution
from .. import LayerDeposition


class SpinCoatingRecipeSteps(ArchiveSection):
    m_def = Section(label_quantity='name')

    name = Quantity(type=str,
                    a_eln=dict(component='StringEditQuantity'))

    time = Quantity(
        type=np.dtype(
            np.float64),
        unit=('s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='s',
            props=dict(
                minValue=0)))

    speed = Quantity(
        type=np.dtype(
            np.float64),
        unit=('rpm'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='rpm',
            props=dict(
                minValue=0)))

    acceleration = Quantity(
        type=np.dtype(
            np.float64),
        unit=('rpm/minute'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='rpm/minute', props=dict(minValue=0)))


class SpinCoatingRecipe(Entity):

    steps = SubSection(
        section_def=SpinCoatingRecipeSteps, repeats=True)


class SpinCoatingPrecursorSolution(ArchiveSection):

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


class SpinCoating(LayerDeposition):
    '''Base class for spin coating of a sample'''

    recipe = Quantity(
        type=Reference(SpinCoatingRecipe.m_def),
        a_eln=dict(component='ReferenceEditQuantity'))

    precursor_solution = SubSection(
        section_def=SpinCoatingPrecursorSolution, repeats=True)

    def normalize(self, archive, logger):
        super(SpinCoating, self).normalize(archive, logger)
        self.method = "Spin Coating"
