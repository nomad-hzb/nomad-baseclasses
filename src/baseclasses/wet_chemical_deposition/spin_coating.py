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
from nomad.datamodel.metainfo.eln import Entity
from nomad.metainfo import Quantity, Reference, Section, SubSection

from .wet_chemical_deposition import WetChemicalDeposition


class SpinCoatingRecipeSteps(ArchiveSection):
    m_def = Section(label_quantity='name')

    name = Quantity(type=str, a_eln=dict(component='StringEditQuantity'))

    time = Quantity(
        links=[
            'https://purl.archive.org/tfsco/TFSCO_00001063',
            'https://purl.archive.org/tfsco/TFSCO_00002072',
        ],
        type=np.dtype(np.float64),
        unit=('s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='s',
            props=dict(minValue=0),
        ),
    )

    speed = Quantity(
        links=[
            'https://purl.archive.org/tfsco/TFSCO_00002026',
            'https://purl.archive.org/tfsco/TFSCO_00002005',
        ],
        type=np.dtype(np.float64),
        unit=('rpm'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='rpm',
            props=dict(minValue=0),
        ),
    )

    acceleration = Quantity(
        links=[
            'https://purl.archive.org/tfsco/TFSCO_00002049',
            'https://purl.archive.org/tfsco/TFSCO_00002002',
        ],
        type=np.dtype(np.float64),
        unit=('rpm/s'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='rpm/s'),
    )


class SpinCoatingRecipe(Entity):
    steps = SubSection(section_def=SpinCoatingRecipeSteps, repeats=True)


class SpinCoating(WetChemicalDeposition):
    """Base class for spin coating of a sample"""

    m_def = Section(links=['http://purl.obolibrary.org/obo/CHMO_0001472'])

    recipe_steps = SubSection(section_def=SpinCoatingRecipeSteps, repeats=True)

    recipe = Quantity(
        type=Reference(SpinCoatingRecipe.m_def),
        a_eln=dict(component='ReferenceEditQuantity'),
    )

    def normalize(self, archive, logger):
        self.method = 'Spin Coating'
        super().normalize(archive, logger)

        if self.recipe_steps is None and self.recipe and self.recipe.steps is not None:
            steps = [step for step in self.recipe.steps]
            self.recipe_steps = steps
