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
from nomad.datamodel.results import Results, Material

from .chemical import Chemical
from nomad.datamodel.metainfo.basesections import PubChemPureSubstanceSection

from nomad.datamodel.metainfo.basesections import CompositeSystem
from .customreadable_identifier import ReadableIdentifiersCustom

from nomad.atomutils import Formula

from baseclasses.helper.utilities import rewrite_json_recursively


class SolutionChemical(ArchiveSection):
    m_def = Section(label_quantity='name')

    name = Quantity(type=str)

    chemical = Quantity(
        type=Reference(Chemical.m_def),
        a_eln=dict(component='ReferenceEditQuantity'))

    chemical_2 = SubSection(
        section_def=PubChemPureSubstanceSection)

    chemical_volume = Quantity(
        type=np.dtype(np.float64),
        unit=('ml'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='ml'))

    chemical_mass = Quantity(
        type=np.dtype(np.float64),
        unit=('mg'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mg'))

    concentration_mass = Quantity(
        type=np.dtype(np.float64),
        unit=('mg/ml'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mg/ml'))

    concentration_mol = Quantity(
        type=np.dtype(np.float64),
        unit=('mol/ml'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mol/ml'))

    def normalize(self, archive, logger):

        if self.chemical is not None and self.chemical.name is not None:
            if self.chemical_volume is not None:
                self.name = self.chemical.name + \
                    ' ' + str(self.chemical_volume)
            elif self.chemical_mass is not None:
                self.name = self.chemical.name + ' ' + str(self.chemical_mass)
            else:
                self.name = self.chemical.name

        if self.chemical_2 is not None and self.chemical_2.name is not None:
            if self.chemical_volume is not None:
                self.name = self.chemical_2.name + \
                    ' ' + str(self.chemical_volume)
            elif self.chemical_mass is not None:
                self.name = self.chemical_2.name + ' ' + str(self.chemical_mass)
            else:
                self.name = self.chemical_2.name


class BasicSolutionProperties(ArchiveSection):

    solvent_ratio = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'))

    solute = SubSection(
        section_def=SolutionChemical, repeats=True)

    solvent = SubSection(
        section_def=SolutionChemical, repeats=True)

    other_solution = SubSection(
        section_def=SectionProxy("OtherSolution"), repeats=True)


class OtherSolution(ArchiveSection):
    m_def = Section(label_quantity='name')

    reload_referenced_solution = Quantity(
        type=bool,
        default=False,
        a_eln=dict(component='ButtonEditQuantity')
    )

    name = Quantity(type=str)

    solution = Quantity(
        type=Reference(SectionProxy("Solution")),
        a_eln=dict(component='ReferenceEditQuantity', label="Solution Reference"))

    solution_volume = Quantity(
        type=np.dtype(np.float64),
        unit=('ml'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='ml'))

    solution_loaded = SubSection(
        section_def=BasicSolutionProperties)

    def normalize(self, archive, logger):

        if self.reload_referenced_solution and self.solution:
            self.reload_referenced_solution = False
            # TODO rewrite to FALSE in json for reprocess
            rewrite_json_recursively(archive, "reload_referenced_solution", False)
            self.solution_loaded = BasicSolutionProperties(
                solute=self.solution.solute,
                solvent=self.solution.solvent,
                other_solution=self.solution.other_solution,
                solvent_ratio=self.solution.solvent_ratio
            )

        if self.solution and self.solution.name:
            if self.solution_volume:
                self.name = self.solution.name + \
                    ' ' + str(self.solution_volume)
            else:
                self.name = self.solution.name


class Solution(CompositeSystem):
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

    solute = SubSection(
        section_def=SolutionChemical, repeats=True)

    solvent = SubSection(
        section_def=SolutionChemical, repeats=True)

    other_solution = SubSection(
        section_def=OtherSolution, repeats=True)

    solution_id = SubSection(
        section_def=ReadableIdentifiersCustom)

    def normalize(self, archive, logger):
        super(Solution, self).normalize(archive, logger)

        # if not archive.results:
        #     archive.results = Results()
        # if not archive.results.material:
        #     archive.results.material = Material()
        # elements = []
        # if self.solute:
        #     for s in self.solute:
        #         if s.molecular_formula is not None:
        #             elements.extend(Formula(s.molecular_formula).elements())
        # if self.solvent:
        #     for s in self.solvent:
        #         if s.molecular_formula is not None:
        #             elements.extend(Formula(s.molecular_formula).elements())
        # if self.other_solution:
        #     for s in self.solvent:
        #         if s.results.material is not None:
        #             elements.extend(Formula(s.molecular_formula).elements())


class Ink(Solution):
    pass
