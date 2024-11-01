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
from nomad.datamodel.metainfo.basesections import (
    CompositeSystem,
    PubChemPureSubstanceSection,
)
from nomad.datamodel.results import Material, Results
from nomad.metainfo import (
    Quantity,
    Section,
    SubSection,
)

from .solution import (
    SolutionPreparation,
    SolutionProperties,
    SolutionStorage,
    SolutionWasching,
)


class SolutionChemicalNew(ArchiveSection):
    m_def = Section(label_quantity='name',
                    a_eln=dict(
                        hide=[
                            'components', 'elemental_composition'],
                        properties=dict(
                            order=[
                                "origin",
                                "chemical_mass",
                                "chemical_volumne",
                                "concentration_mass", "concentration_mol", "amount_relative"""
                            ],
                        )))

    name = Quantity(type=str)

    chemical = SubSection(
        links=['http://purl.obolibrary.org/obo/CHEBI_59999'],
        section_def=PubChemPureSubstanceSection)

    chemical_volume = Quantity(
        links=['http://purl.obolibrary.org/obo/PATO_0000918','https://purl.archive.org/tfsco/TFSCO_00002158'],
        type=np.dtype(np.float64),
        unit=('ml'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='ml'))

    chemical_mass = Quantity(
        links=['http://purl.obolibrary.org/obo/PATO_0000125','https://purl.archive.org/tfsco/TFSCO_00005020'],
        type=np.dtype(np.float64),
        unit=('mg'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mg'))

    concentration_mass = Quantity(
        links=['http://purl.obolibrary.org/obo/PATO_0000033'],
        type=np.dtype(np.float64),
        unit=('mg/ml'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mg/ml'))

    concentration_mol = Quantity(
        links=['http://purl.obolibrary.org/obo/PATO_0000033'],
        type=np.dtype(np.float64),
        unit=('mol/l'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mol/l'))

    amount_relative = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity'))

    origin = Quantity(
        type=str,
        a_eln=dict(
            component='StringEditQuantity'
        ))

    def normalize(self, archive, logger):

        if self.chemical is not None and self.chemical.name is not None:
            if self.chemical_volume is not None:
                self.name = self.chemical.name + \
                    ' ' + str(self.chemical_volume)
            elif self.chemical_mass is not None:
                self.name = self.chemical.name + ' ' + str(self.chemical_mass)
            else:
                self.name = self.chemical.name


class MAXPhasePrecursor(SolutionChemicalNew):
    m_def = Section(
        a_eln=dict(
            hide=[
                'chemical_volume', 'components', 'elemental_composition', 'amount_relative'],
            properties=dict(
                order=[
                    "origin",
                    "particle_size",
                    "chemical_mass",
                    "concentration_mass", "concentration_mol"
                ],
            )))

    particle_size = Quantity(
        type=np.dtype(np.float64),
        unit=('um'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='um'))


class ConcentrationMXeneSolution(ArchiveSection):
    quantity_of_colloidal_solution = Quantity(
        links=['http://purl.obolibrary.org/obo/PATO_0000918','https://purl.archive.org/tfsco/TFSCO_00002158'],
        type=np.dtype(np.float64),
        unit=('ml'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='ml'))

    centrifuge_speed = Quantity(
        links=['https://purl.archive.org/tfsco/TFSCO_00002026','https://purl.archive.org/tfsco/TFSCO_00002005'],
        type=np.dtype(np.float64),
        unit=('Hz'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='rpm'))

    centrifuge_time = Quantity(
        links=['http://purl.obolibrary.org/obo/PATO_0000165','https://purl.archive.org/tfsco/TFSCO_00005085'],
        type=np.dtype(np.float64),
        unit=('second'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='hr'))

    description = Quantity(
        type=str,
        description='Any information that cannot be captured in the other fields.',
        a_eln=dict(component='RichTextEditQuantity'),
    )


class MXeneSolutionProperties(SolutionProperties):
    mxene_formula = Quantity(
        links=['https://purl.archive.org/tfsco/TFSCO_00001088'],
        type=str,
        a_eln=dict(component='StringEditQuantity'))


class PreparationStep(ArchiveSection):

    description = Quantity(
        type=str,
        description='Any information that cannot be captured in the other fields.',
        a_eln=dict(component='RichTextEditQuantity'),
    )
    preparation = SubSection(section_def=SolutionPreparation)
    washing = SubSection(
        links=['https://purl.archive.org/tfsco/TFSCO_00000068'],
        section_def=SolutionWasching, repeats=True)
    storage = SubSection(
        links=['http://purl.obolibrary.org/obo/OBI_0302893'],
        section_def=SolutionStorage, repeats=True)


class Etching(PreparationStep):
    m_def = Section(
        links=['http://purl.obolibrary.org/obo/CHMO_0001558'],
        a_eln=dict(
            properties=dict(
                order=[
                    "preparation",
                    "etching_agent",
                    "washing",
                    "storage"
                ],
            )))

    etching_agent = SubSection(section_def=SolutionChemicalNew, repeats=True)


class Delamination(PreparationStep):
    m_def = Section(
        a_eln=dict(
            properties=dict(
                order=[
                    "preparation",
                    "solute",
                    "solvent",
                    "washing",
                    "storage"
                ],
            )))

    solute = SubSection(
        links=['https://purl.archive.org/tfsco/TFSCO_00001078'],
        section_def=SolutionChemicalNew, repeats=True)
    solvent = SubSection(
        links=['https://purl.archive.org/tfsco/TFSCO_00000026'],
        section_def=SolutionChemicalNew, repeats=True)


class MXeneSolution(CompositeSystem):
    '''Base class for a solution'''

    MAX_phase = SubSection(section_def=MAXPhasePrecursor)
    etching = SubSection(
        links=['http://purl.obolibrary.org/obo/CHMO_0001558'],
        section_def=Etching)
    delamination = SubSection(section_def=Delamination)
    concentration = SubSection(
        links=['http://purl.obolibrary.org/obo/PATO_0000033'],
        section_def=ConcentrationMXeneSolution)
    properties = SubSection(section_def=MXeneSolutionProperties)

    def normalize(self, archive, logger):
        super().normalize(archive, logger)

        if not archive.results:
            archive.results = Results()
        if not archive.results.material:
            archive.results.material = Material()

        if self.properties and self.properties.mxene_formula:
            try:
                from nomad.atomutils import Formula
                formula = Formula(self.properties.mxene_formula)
                formula.populate(section=archive.results.material)
            except Exception as e:
                logger.warn('could not analyse layer material', exc_info=e)
