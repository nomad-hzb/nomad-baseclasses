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

from nomad.metainfo import (Quantity, SubSection, Section, Reference, Datetime)

from nomad.datamodel.results import Results, Material
from nomad.datamodel.data import ArchiveSection

from nomad.datamodel.metainfo.basesections import CompositeSystem, PubChemPureSubstanceSection, CompositeSystemReference, Entity
from .. import ReadableIdentifiersCustom
# from .preparation_protocoll import PreparationProtocol


def get_next_project_sample_number(data, entry_id):
    '''Check the lab ids of a project id for project_sample_number (last digits of lab_id) and returns the next higher one'''
    project_sample_numbers = []
    for entry in data:
        lab_ids = entry["results"]["eln"]["lab_ids"]
        if entry["entry_id"] == entry_id and lab_ids[0].split(
                "_")[-1].isdigit():
            return int(lab_ids[0].split("_")[-1])
        project_sample_numbers.extend([int(lab_id.split(
            "_")[-1]) for lab_id in lab_ids if lab_id.split("_")[-1].isdigit()])
    return max(project_sample_numbers) + 1 if project_sample_numbers else 0


class SampleIDCE(ReadableIdentifiersCustom):
    m_def = Section(
        a_eln=dict(
            hide=["sample_owner", "sample_short_name", "sample_id"]
        ))

    short_name = Quantity(
        type=str,
        description='''A short handle of the Project the sample belongs to.''',
        a_eln=dict(component='StringEditQuantity', label='Project Name'))

    project_sample_number = Quantity(
        type=np.dtype(np.int64),
        a_eln=dict(
            component='NumberEditQuantity'
        ))

    def normalize(self, archive, logger):
        super(SampleIDCE, self).normalize(archive, logger)

        if self.institute and self.short_name and self.owner:
            from unidecode import unidecode
            first_name, last_name = self.owner, ''
            if ' ' in self.owner:
                first_name, last_name = self.owner.split(' ', 1)
            first_name = unidecode(first_name.strip())
            last_name = unidecode(last_name.strip())
            owner = ''.join([first_name[:2], last_name[:2]])
            sample_id_list = [self.institute,
                              self.short_name, owner]
            self.lab_id = '_'.join(sample_id_list)

        from nomad.search import search
        if self.project_sample_number is not None:
            sample_id_tmp = f"{self.lab_id}_{self.project_sample_number:04d}"
        else:
            sample_id_tmp = f"{self.lab_id}_9999"
        query = {'results.eln.lab_ids': sample_id_tmp}
        search_result_1 = search(owner='all', query=query,
                                 user_id=archive.metadata.main_author.user_id)

        if self.project_sample_number is None or (len(search_result_1.data) != 0 and
                                                  archive.metadata.entry_id not in [
                                                      d["entry_id"] for d in search_result_1.data]
                                                  ):
            query = {'results.eln.lab_ids': self.lab_id}
            search_result = search(owner='all', query=query,
                                   user_id=archive.metadata.main_author.user_id)
            self.project_sample_number = get_next_project_sample_number(
                search_result.data, archive.metadata.entry_id)

        if self.lab_id is not None and self.project_sample_number is not None:
            sample_id_old = self.lab_id
            self.lab_id = f"{self.lab_id}_{self.project_sample_number:04d}"
            archive.results.eln.lab_ids = []
            archive.results.eln.lab_ids = [self.lab_id, sample_id_old]
            archive.data.lab_id = self.lab_id


class SubstrateProperties(ArchiveSection):

    substrate_type = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=['glassy carbon', 'ITO on glass', 'Platinum', 'glass', 'silicon wafer'])
        ))

    substrate_dimension = Quantity(
        type=str,
        a_eln=dict(
            component='StringEditQuantity',

        ))


class CESample(CompositeSystem):

    origin = Quantity(
        type=str,
        a_eln=dict(
            component='StringEditQuantity'
        ))

    chemical_composition_or_formulas = Quantity(
        type=str,
        description=(
            'A list of the elements involved'),
        a_eln=dict(component='StringEditQuantity'))

    def normalize(self, archive, logger):
        super(CESample, self).normalize(archive, logger)
        if self.chemical_composition_or_formulas:
            if not archive.results:
                archive.results = Results()
            if not archive.results.material:
                archive.results.material = Material()
            material = archive.results.material
            from ase import Atoms
            from pymatgen.core import Composition

            formulas = [
                Atoms(Composition(formula.strip()
                                  ).get_integer_formula_and_factor()[0])
                for formula in self.chemical_composition_or_formulas.split(",") if formula]
            elements = []
            for f in formulas:
                elements.extend(f.get_chemical_symbols())
            material.elements = []
            material.elements = list(set(elements))
            if len(formulas) == 1:
                formula = formulas[0]
                material.chemical_formula_hill = formula.get_chemical_formula(
                    mode='hill')
                material.chemical_formula_reduced = formula.get_chemical_formula(
                    mode='reduce')
                material.chemical_formula_descriptive = self.chemical_composition_or_formulas


class SampleIDCENOME(SampleIDCE):
    m_def = Section(
        a_eln=dict(
            hide=["sample_owner", "sample_short_name", "sample_id"]
        ))

    institute = Quantity(
        type=str,
        description='Alias/short name of the home institute of the owner, i.e. *HZB*.',
        default='CE-NOME',
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=[
                    'CE-NOME',
                    'CE-NOME Berlin',
                    'CE-NOME Göttingen'])))

    owner = Quantity(
        type=str,
        description='Alias/short name of the home institute of the owner, i.e. *HZB*.',
        default='Marcel Risch',
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=[
                    'Joaquín Morales Santelices',
                    'Denis Antipin',
                    'Giacomo Zuliani',
                    'Omeshwari Bisen',
                    'Patricia Padonou',
                    'Marcel Risch',
                    'Younes Mousazade',
                    'Jia Du'])))

    def normalize(self, archive, logger):
        super(SampleIDCENOME, self).normalize(archive, logger)


class CENSLISample(CESample):

    sample_id = SubSection(
        section_def=SampleIDCE)

    def normalize(self, archive, logger):
        super(CENSLISample, self).normalize(archive, logger)


class CENOMESample(CESample):

    # id_of_preparation_protocol = Quantity(
    #     type=Reference(PreparationProtocol.m_def),
    #     a_eln=dict(component='ReferenceEditQuantity'))

    date_of_disposal = Quantity(
        type=Datetime,
        description='The date where the sample was disposed',
        a_eln=dict(component='DateTimeEditQuantity'))

    component_description = Quantity(
        type=str,
        description=(
            'A description of the components.'),
        a_eln=dict(component='StringEditQuantity'))

    origin = Quantity(
        type=str,
        a_eln=dict(
            component='StringEditQuantity', label="Producer"
        ))

    project_name_long = Quantity(
        type=str,
        description=(
            'A description of the components.'),
        a_eln=dict(component='StringEditQuantity'))

    datetime = Quantity(
        type=Datetime,
        description='The date and time associated with this section.',
        a_eln=dict(
            component='DateTimeEditQuantity',
            label="Date of preparation/purchase"))

    description = Quantity(
        type=str,
        description='Any information that cannot be captured in the other fields.',
        a_eln=dict(
            component='RichTextEditQuantity',
            label="Comment"))

    sample_id = SubSection(
        section_def=SampleIDCENOME)

    substrate = SubSection(
        section_def=SubstrateProperties)

    def normalize(self, archive, logger):
        super(CENOMESample, self).normalize(archive, logger)


class Electrode(CESample):
    location = Quantity(
        type=str,
        a_eln=dict(
            component='StringEditQuantity'
        ))

    producer = Quantity(
        type=str,
        a_eln=dict(
            component='StringEditQuantity'
        ))


class Equipment(Entity):
    location = Quantity(
        type=str,
        a_eln=dict(
            component='StringEditQuantity'
        ))

    producer = Quantity(
        type=str,
        a_eln=dict(
            component='StringEditQuantity'
        ))


class SubstanceWithConcentration(ArchiveSection):
    m_def = Section(label_quantity='name')
    substance = SubSection(
        section_def=PubChemPureSubstanceSection)

    name = Quantity(type=str)

    concentration_mmol_per_l = Quantity(
        type=np.dtype(
            np.float64),
        unit=("mmol/l"),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit="mol/l"))

    concentration_g_per_l = Quantity(
        type=np.dtype(np.float64), unit=("g/l"),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit="g/l"))

    # concentration_perw_w = Quantity(
    #     type=np.dtype(np.float64), unit=("g/g"),
    #     a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit="g/g"))

    # concentration_perv_v = Quantity(
    #     type=np.dtype(np.float64), unit=("l/l"),
    #     a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit="l/l"))

    def normalize(self, archive, logger):

        if self.substance and self.substance.name:
            self.name = self.substance.name


class Electrolyte(CESample):
    ph_value = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity', label="pH Value"))

    solvent = SubSection(
        section_def=PubChemPureSubstanceSection)

    substances = SubSection(
        section_def=SubstanceWithConcentration, repeats=True)

    def normalize(self, archive, logger):

        formulas = []
        if self.solvent is not None and self.solvent.molecular_formula:
            formulas.append(
                self.solvent.molecular_formula.strip().replace(
                    ".", ""))
        if self.substances is not None:
            formulas.extend([subs.substance.molecular_formula.strip().replace(
                ".", "") for subs in self.substances if subs.substance is not None and subs.substance.molecular_formula is not None])
        self.chemical_composition_or_formulas = ','.join(formulas)
        super(Electrolyte, self).normalize(archive, logger)


class Purging(ArchiveSection):
    gas = SubSection(
        section_def=PubChemPureSubstanceSection)

    temperature = Quantity(
        type=np.dtype(np.float64),
        unit="°C",
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'))

    time = Quantity(
        type=np.dtype(np.float64),
        unit="minute",
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='minute'))


class EnvironmentReference(CompositeSystemReference):
    volume = Quantity(
        type=np.dtype(np.float64),
        unit="ml",
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='ml'))


class Environment(Electrolyte):

    purging = SubSection(
        section_def=Purging)

    other_environments = SubSection(
        section_def=EnvironmentReference, repeats=True)


class ElectroChemicalCell(CESample):
    working_electrode = Quantity(
        type=Reference(CESample.m_def),
        a_eln=dict(component='ReferenceEditQuantity'))

    reference_electrode = Quantity(
        type=Reference(Electrode.m_def),
        a_eln=dict(component='ReferenceEditQuantity'))

    counter_electrode = Quantity(
        type=Reference(Electrode.m_def),
        a_eln=dict(component='ReferenceEditQuantity'))

    electrolyte = Quantity(
        type=Reference(Electrolyte.m_def),
        a_eln=dict(component='ReferenceEditQuantity'))

    def normalize(self, archive, logger):

        self.chemical_composition_or_formulas = ''

        if self.working_electrode is not None:
            if self.working_electrode.chemical_composition_or_formulas is not None:
                elements_formula = [
                    self.chemical_composition_or_formulas,
                    self.working_electrode.chemical_composition_or_formulas]
                self.chemical_composition_or_formulas = ','.join(
                    elements_formula)

        if self.reference_electrode is not None:
            if self.reference_electrode.chemical_composition_or_formulas is not None:
                elements_formula = [
                    self.chemical_composition_or_formulas,
                    self.reference_electrode.chemical_composition_or_formulas]
                self.chemical_composition_or_formulas = ','.join(
                    elements_formula)

        if self.counter_electrode is not None:
            if self.counter_electrode.chemical_composition_or_formulas is not None:
                elements_formula = [
                    self.chemical_composition_or_formulas,
                    self.counter_electrode.chemical_composition_or_formulas]
                self.chemical_composition_or_formulas = ','.join(
                    elements_formula)

        if self.electrolyte is not None:
            if self.electrolyte.chemical_composition_or_formulas is not None:
                elements_formula = [
                    self.chemical_composition_or_formulas,
                    self.electrolyte.chemical_composition_or_formulas]
                self.chemical_composition_or_formulas = ','.join(
                    elements_formula)

        if self.chemical_composition_or_formulas.startswith(","):
            self.chemical_composition_or_formulas = self.chemical_composition_or_formulas[1:]

        super(ElectroChemicalCell, self).normalize(archive, logger)


class ElectroChemicalSetup(CESample):

    setup = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=['Beaker', 'RDE', 'RRDE', 'flowcell XAS', 'flowcell FED', 'flowcell UVvis'])
        ))

    reference_electrode = Quantity(
        type=Reference(Electrode.m_def),
        a_eln=dict(component='ReferenceEditQuantity'))

    counter_electrode = Quantity(
        type=Reference(Electrode.m_def),
        a_eln=dict(component='ReferenceEditQuantity'))

    equipment = Quantity(
        type=Reference(Equipment.m_def),
        shape=['*'],
        a_eln=dict(component='ReferenceEditQuantity'))

    def normalize(self, archive, logger):

        self.chemical_composition_or_formulas = ''

        if self.reference_electrode is not None:
            if self.reference_electrode.chemical_composition_or_formulas is not None:
                elements_formula = [
                    self.chemical_composition_or_formulas,
                    self.reference_electrode.chemical_composition_or_formulas]
                self.chemical_composition_or_formulas = ','.join(
                    elements_formula)

        if self.counter_electrode is not None:
            if self.counter_electrode.chemical_composition_or_formulas is not None:
                elements_formula = [
                    self.chemical_composition_or_formulas,
                    self.counter_electrode.chemical_composition_or_formulas]
                self.chemical_composition_or_formulas = ','.join(
                    elements_formula)

        if self.chemical_composition_or_formulas.startswith(","):
            self.chemical_composition_or_formulas = self.chemical_composition_or_formulas[1:]

        super(ElectroChemicalSetup, self).normalize(archive, logger)
