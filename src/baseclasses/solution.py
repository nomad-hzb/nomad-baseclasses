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
from nomad.datamodel.metainfo.basesections import CompositeSystem
from nomad.metainfo import (
    Datetime,
    MEnum,
    Quantity,
    Reference,
    Section,
    SectionProxy,
    SubSection,
)

from baseclasses import PubChemPureSubstanceSectionCustom
from baseclasses.helper.utilities import rewrite_json_recursively

from .chemical import Chemical
from .customreadable_identifier import ReadableIdentifiersCustom


class SolutionChemical(ArchiveSection):
    m_def = Section(label_quantity='name')

    name = Quantity(type=str)

    chemical = Quantity(
        links=['http://purl.obolibrary.org/obo/CHEBI_59999'],
        type=Reference(Chemical.m_def),
        a_eln=dict(component='ReferenceEditQuantity'),
    )

    chemical_2 = SubSection(
        links=['http://purl.obolibrary.org/obo/CHEBI_59999'],
        section_def=PubChemPureSubstanceSectionCustom,
    )

    chemical_volume = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0000918',
            'https://purl.archive.org/tfsco/TFSCO_00002158',
        ],
        type=np.dtype(np.float64),
        unit=('ml'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='ml'),
    )

    chemical_mass = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0000125',
            'https://purl.archive.org/tfsco/TFSCO_00005020',
        ],
        type=np.dtype(np.float64),
        unit=('mg'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mg'),
    )

    concentration_mass = Quantity(
        links=['http://purl.obolibrary.org/obo/PATO_0000033'],
        type=np.dtype(np.float64),
        unit=('mg/ml'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mg/ml'),
    )

    concentration_mol = Quantity(
        links=['http://purl.obolibrary.org/obo/PATO_0000033'],
        type=np.dtype(np.float64),
        unit=('mol/ml'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mmol/ml'),
    )

    amount_relative = Quantity(
        type=np.dtype(np.float64), a_eln=dict(component='NumberEditQuantity')
    )

    chemical_id = Quantity(type=str, a_eln=dict(component='StringEditQuantity'))

    def normalize(self, archive, logger):
        if self.chemical is not None and self.chemical.name is not None:
            if self.chemical_volume is not None:
                self.name = self.chemical.name + ' ' + str(self.chemical_volume)
            elif self.chemical_mass is not None:
                self.name = self.chemical.name + ' ' + str(self.chemical_mass)
            else:
                self.name = self.chemical.name

        if self.chemical_2 is not None and self.chemical_2.name is not None:
            if self.chemical_volume is not None:
                self.name = self.chemical_2.name + ' ' + str(self.chemical_volume)
            elif self.chemical_mass is not None:
                self.name = self.chemical_2.name + ' ' + str(self.chemical_mass)
            else:
                self.name = self.chemical_2.name


class OtherSolution(ArchiveSection):
    m_def = Section(
        links=['http://purl.obolibrary.org/obo/CHEBI_75958'], label_quantity='name'
    )

    reload_referenced_solution = Quantity(
        type=bool, default=False, a_eln=dict(component='ActionEditQuantity')
    )

    name = Quantity(type=str)

    solution = Quantity(
        links=['http://purl.obolibrary.org/obo/CHEBI_75958'],
        type=Reference(SectionProxy('Solution')),
        a_eln=dict(component='ReferenceEditQuantity', label='Solution Reference'),
    )

    solution_volume = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0000918',
            'https://purl.archive.org/tfsco/TFSCO_00002158',
        ],
        type=np.dtype(np.float64),
        unit=('ml'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='ml'),
    )

    amount_relative = Quantity(
        type=np.dtype(np.float64), a_eln=dict(component='NumberEditQuantity')
    )

    solution_details = SubSection(section_def=SectionProxy('Solution'))

    def normalize(self, archive, logger):
        if self.reload_referenced_solution and self.solution:
            self.reload_referenced_solution = False
            rewrite_json_recursively(archive, 'reload_referenced_solution', False)
            self.solution_details = self.solution.m_copy(deep=True)
            self.solution = None

        if self.solution and self.solution.name:
            if self.solution_volume:
                self.name = self.solution.name + ' ' + str(self.solution_volume)
            else:
                self.name = self.solution.name

        if self.solution_details and self.solution_details.name:
            if self.solution_volume:
                self.name = self.solution_details.name + ' ' + str(self.solution_volume)
            else:
                self.name = self.solution_details.name


class SolutionPreparation(ArchiveSection):
    atmosphere = Quantity(
        links=['https://purl.archive.org/tfsco/TFSCO_00001012'],
        type=str,
        a_eln=dict(
            component='EnumEditQuantity', props=dict(suggestions=['Ar', 'N2', 'Air'])
        ),
    )


class SolutionPreparationStandard(SolutionPreparation):
    method = Quantity(
        type=MEnum('Shaker', 'Ultrasoncic', 'Waiting', 'Stirring'),
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
        ),
    )

    temperature = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0000146',
            'https://purl.archive.org/tfsco/TFSCO_00002111',
        ],
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'),
    )

    time = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0000165',
            'https://purl.archive.org/tfsco/TFSCO_00005085',
        ],
        type=np.dtype(np.float64),
        unit=('minute'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='minute'),
    )

    speed = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0000008',
            'https://purl.archive.org/tfsco/TFSCO_00005043',
        ],
        type=np.dtype(np.float64),
        unit=('Hz'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='rpm'),
    )

    solvent_ratio = Quantity(type=str, a_eln=dict(component='StringEditQuantity'))

    bath = Quantity(
        type=MEnum('Oil bath', 'Ice bath', 'Water bath'),
        a_eln=dict(
            component='RadioEnumEditQuantity',
        ),
    )

    filtered = Quantity(
        type=bool,
        a_eln=dict(
            component='BoolEditQuantity',
        ),
    )

    preparation_description = Quantity(
        type=str,
        description="""Any information on solution preparation
            that cannot be captured in other fields.""",
        a_eln=dict(component='RichTextEditQuantity'),
    )


class SolutionPreparationStandardWithSonication(SolutionPreparationStandard):
    sonication_time = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0000165',
            'https://purl.archive.org/tfsco/TFSCO_00005085',
        ],
        type=np.dtype(np.float64),
        unit=('second'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='hour'),
    )


class MoltenSalt(ArchiveSection):
    prepared_in = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity', props=dict(suggestions=['Glove box', 'Air'])
        ),
    )

    atmosphere = Quantity(
        links=['https://purl.archive.org/tfsco/TFSCO_00001012'],
        type=str,
        a_eln=dict(
            component='EnumEditQuantity', props=dict(suggestions=['Ar', 'N2', 'Air'])
        ),
    )

    grinding_duration = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0001309',
            'https://purl.archive.org/tfsco/TFSCO_00002006',
        ],
        type=np.dtype(np.float64),
        unit=('second'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='hour'),
    )

    solvent_ratio = Quantity(type=str, a_eln=dict(component='StringEditQuantity'))

    salts = SubSection(section_def=PubChemPureSubstanceSectionCustom, repeats=True)


class SolutionPreparationMoltenSalt(SolutionPreparation):
    heating_source = Quantity(type=str, a_eln=dict(component='StringEditQuantity'))
    crucible_type = Quantity(type=str, a_eln=dict(component='StringEditQuantity'))

    heating_temperature = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0000146',
            'https://purl.archive.org/tfsco/TFSCO_00002111',
        ],
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'),
    )

    heating_time = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0000165',
            'https://purl.archive.org/tfsco/TFSCO_00005085',
        ],
        type=np.dtype(np.float64),
        unit=('second'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='minute'),
    )

    sample_quantity_after = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0000125',
            'http://purl.obolibrary.org/obo/IAO_0000414',
        ],
        type=np.dtype(np.float64),
        unit=('g'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='g'),
    )

    salt_mixture = SubSection(section_def=MoltenSalt)


class SolutionProperties(ArchiveSection):
    ph_value = Quantity(
        type=np.dtype(np.float64), a_eln=dict(component='NumberEditQuantity')
    )

    final_volume = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0000918',
            'https://purl.archive.org/tfsco/TFSCO_00003000',
        ],
        type=np.dtype(np.float64),
        unit=('ml'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='ml'),
    )

    final_concentration = Quantity(
        links=['http://purl.obolibrary.org/obo/PATO_0000033'],
        type=np.dtype(np.float64),
        unit=('mg/ml'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mg/ml'),
    )


class WaschingSolvents(ArchiveSection):
    m_def = Section(label_quantity='solvent_name')

    solvent_name = Quantity(type=str, a_eln=dict(component='StringEditQuantity'))

    volume = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0000918',
            'https://purl.archive.org/tfsco/TFSCO_00002158',
        ],
        type=np.dtype(np.float64),
        unit=('ml'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='ml'),
    )

    concentration_mol = Quantity(
        links=['http://purl.obolibrary.org/obo/PATO_0000033'],
        type=np.dtype(np.float64),
        unit=('mol/l'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mol/l'),
    )


class SolutionWasching(ArchiveSection):
    washing_technique = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=['Filtration', 'Centrifugation']),
        ),
    )

    number_of_washes = Quantity(
        type=np.dtype(np.int64), a_eln=dict(component='NumberEditQuantity')
    )

    washing_solvent = SubSection(
        links=['https://purl.archive.org/tfsco/TFSCO_00000026'],
        section_def=WaschingSolvents,
        repeats=True,
    )


class SolutionWaschingFiltration(SolutionWasching):
    pass


class SolutionWaschingCentrifuge(SolutionWasching):
    centrifuge_speed = Quantity(
        links=[
            'https://purl.archive.org/tfsco/TFSCO_00002026',
            'https://purl.archive.org/tfsco/TFSCO_00002005',
        ],
        type=np.dtype(np.float64),
        unit=('Hz'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='rpm'),
    )

    centrifuge_time = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0000165',
            'https://purl.archive.org/tfsco/TFSCO_00005085',
        ],
        type=np.dtype(np.float64),
        unit=('second'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='minute'),
    )


class SolutionStorage(ArchiveSection):
    start_date = Quantity(type=Datetime, a_eln=dict(component='DateTimeEditQuantity'))

    end_date = Quantity(type=Datetime, a_eln=dict(component='DateTimeEditQuantity'))

    storage_condition = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'),
    )
    temperature = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0000146',
            'https://purl.archive.org/tfsco/TFSCO_00002111',
        ],
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'),
    )

    atmosphere = Quantity(
        links=['https://purl.archive.org/tfsco/TFSCO_00001012'],
        type=str,
        a_eln=dict(
            component='EnumEditQuantity', props=dict(suggestions=['Ar', 'N2', 'Air'])
        ),
    )

    comments = Quantity(
        type=str,
        a_eln=dict(component='RichTextEditQuantity'),
    )


class Solution(CompositeSystem):
    """Base class for a solution"""

    method = Quantity(
        type=MEnum('Shaker', 'Ultrasoncic', 'Waiting', 'Stirring'),
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
        ),
    )

    solvent_ratio = Quantity(type=str, a_eln=dict(component='StringEditQuantity'))

    temperature = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0000146',
            'https://purl.archive.org/tfsco/TFSCO_00002111',
        ],
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'),
    )

    time = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0000165',
            'https://purl.archive.org/tfsco/TFSCO_00005085',
        ],
        type=np.dtype(np.float64),
        unit=('minute'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='minute'),
    )

    speed = Quantity(
        links=[
            'https://purl.archive.org/tfsco/TFSCO_00002026',
            'https://purl.archive.org/tfsco/TFSCO_00002005',
        ],
        type=np.dtype(np.float64),
        unit=('Hz'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='rpm'),
    )

    solute = SubSection(
        links=['https://purl.archive.org/tfsco/TFSCO_00001078'],
        section_def=SolutionChemical,
        repeats=True,
    )
    additive = SubSection(
        links=['https://purl.archive.org/tfsco/TFSCO_00001056'],
        section_def=SolutionChemical,
        repeats=True,
    )
    solvent = SubSection(
        links=['https://purl.archive.org/tfsco/TFSCO_00000026'],
        section_def=SolutionChemical,
        repeats=True,
    )
    other_solution = SubSection(
        links=['http://purl.obolibrary.org/obo/CHEBI_75958'],
        section_def=OtherSolution,
        repeats=True,
    )
    preparation = SubSection(section_def=SolutionPreparation)
    properties = SubSection(section_def=SolutionProperties)
    storage = SubSection(
        links=['http://purl.obolibrary.org/obo/OBI_0302893'],
        section_def=SolutionStorage,
        repeats=True,
    )
    solution_id = SubSection(section_def=ReadableIdentifiersCustom)

    def normalize(self, archive, logger):
        super().normalize(archive, logger)
        if not self.preparation:
            if (
                self.temperature is not None
                or self.time is not None
                or self.speed is not None
                or self.solvent_ratio is not None
            ):
                self.preparation = SolutionPreparationStandard(
                    temperature=self.temperature,
                    time=self.time,
                    speed=self.speed,
                    solvent_ratio=self.solvent_ratio,
                )


class Ink(Solution):
    pass
