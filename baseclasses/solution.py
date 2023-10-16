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
    MEnum, SectionProxy, Datetime)
from nomad.datamodel.data import ArchiveSection

from .chemical import Chemical
from nomad.datamodel.metainfo.basesections import PubChemPureSubstanceSection

from nomad.datamodel.metainfo.basesections import CompositeSystem
from .customreadable_identifier import ReadableIdentifiersCustom

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
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mmol/ml'))

    amount_relative = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity'))

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

    amount_relative = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity'))

    solution_details = SubSection(
        section_def=SectionProxy("Solution"))

    def normalize(self, archive, logger):

        if self.reload_referenced_solution and self.solution:
            self.reload_referenced_solution = False
            # TODO rewrite to FALSE in json for reprocess
            rewrite_json_recursively(archive, "reload_referenced_solution", False)
            self.solution_details = self.solution.m_copy()

        if self.solution and self.solution.name:
            if self.solution_volume:
                self.name = self.solution.name + \
                    ' ' + str(self.solution_volume)
            else:
                self.name = self.solution.name

        if self.solution_details and self.solution_details.name:
            if self.solution_volume:
                self.name = self.solution_details.name + \
                    ' ' + str(self.solution_volume)
            else:
                self.name = self.solution_details.name


class SolutionPreparation(ArchiveSection):

    atmosphere = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=['Ar', 'N2', "Air"])
        ))


class SolutionPreparationStandard(SolutionPreparation):
    method = Quantity(
        type=MEnum('Shaker', 'Ultrasoncic', 'Waiting', "Stirring"),
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
        ))

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

    solvent_ratio = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'))

    oil_bath = Quantity(
        type=bool,
        default=False,
        a_eln=dict(
            component='BoolEditQuantity',
        ))


class SolutionPreparationStandardWithSonication(SolutionPreparationStandard):

    sonication_time = Quantity(
        type=np.dtype(np.float64),
        unit=('second'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='hour'))


class MoltenSalt(ArchiveSection):
    prepared_in = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=['Glove box', 'Air'])
        ))

    salts = SubSection(section_def=PubChemPureSubstanceSection, repeats=True)


class SolutionPreparationMoltenSalt(SolutionPreparation):

    grinding_duration = Quantity(
        type=np.dtype(
            np.float64),
        unit=('second'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='hour'))

    heating_source = Quantity(type=str, a_eln=dict(component='StringEditQuantity'))
    crucible_type = Quantity(type=str, a_eln=dict(component='StringEditQuantity'))

    heating_temperature = Quantity(
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'))

    heating_time = Quantity(
        type=np.dtype(
            np.float64),
        unit=('second'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='minute'))

    sample_quantity_after = Quantity(
        type=np.dtype(
            np.float64),
        unit=('g'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='g'))

    salt_mixture = SubSection(section_def=MoltenSalt)


class SolutionProperties(ArchiveSection):
    ph_value = Quantity(
        type=np.dtype(np.int64),
        a_eln=dict(component='NumberEditQuantity'))


class SolutionWasching(ArchiveSection):
    washing_solvent = SubSection(
        section_def=PubChemPureSubstanceSection)

    washing_technique = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=['Filtration', 'Centrifugation'])
        ))

    number_of_washes = Quantity(
        type=np.dtype(np.int64),
        a_eln=dict(
            component='NumberEditQuantity'))

    centrifuge_speed = Quantity(
        type=np.dtype(np.float64),
        unit=('Hz'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='rpm'))

    centrifuge_time = Quantity(
        type=np.dtype(np.float64),
        unit=('second'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='minute'))


class SolutionStorage(ArchiveSection):
    start_date = Quantity(
        type=Datetime,
        a_eln=dict(component='DateTimeEditQuantity'))

    end_date = Quantity(
        type=Datetime,
        a_eln=dict(component='DateTimeEditQuantity'))

    storage_condition = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'),
    )
    temperature = Quantity(
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'))

    atmosphere = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=['Ar', 'N2', "Air"])
        ))

    comments = Quantity(
        type=str,
        a_eln=dict(component='RichTextEditQuantity'),
    )


class Solution(CompositeSystem):
    '''Base class for a solution'''

    method = Quantity(
        type=MEnum('Shaker', 'Ultrasoncic', 'Waiting', "Stirring"),
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

    solute = SubSection(section_def=SolutionChemical, repeats=True)
    additive = SubSection(section_def=SolutionChemical, repeats=True)
    solvent = SubSection(section_def=SolutionChemical, repeats=True)
    other_solution = SubSection(section_def=OtherSolution, repeats=True)
    preparation = SubSection(section_def=SolutionPreparation)
    washing = SubSection(section_def=SolutionWasching)
    properties = SubSection(section_def=SolutionProperties)
    storage = SubSection(section_def=SolutionStorage, repeats=True)
    solution_id = SubSection(section_def=ReadableIdentifiersCustom)

    def normalize(self, archive, logger):
        super(Solution, self).normalize(archive, logger)
        if (not self.preparation):
            if self.temperature is not None or self.time is not None or self.speed is not None or self.solvent_ratio is not None:
                self.preparation = SolutionPreparationStandard(
                    temperature=self.temperature,
                    time=self.time,
                    speed=self.speed,
                    solvent_ratio=self.solvent_ratio
                )
        # elements = []
        # for solute in self.solute:
        #     if solute.chemical_2 is not None and solute.chemical_2
        # if replaced_formula is not None:
        #     try:
        #         composition = Composition(replaced_formula)
        #         int_formula = composition.get_integer_formula_and_factor()[0]
        #         composition_final = Composition(int_formula)
        #         clean_formulas_no_brackets = composition_final.get_reduced_composition_and_factor()[
        #             0]
        #         composition_final_int = Composition(clean_formulas_no_brackets)
        #         # hill_formula = composition_final_int.hill_formula
        #         reduced_formula = composition_final_int.get_reduced_composition_and_factor()[
        #             0].to_pretty_string()
        #         # reduced_formula = Composition(hill_formula).reduced_formula
        #         elements = composition_final_int.chemical_system.split('-')
        #         return reduced_formula, elements

        #     except ValueError:
        #         print(
        #             'Perovskite formula with a cation abbreviation could not be parsed')

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
