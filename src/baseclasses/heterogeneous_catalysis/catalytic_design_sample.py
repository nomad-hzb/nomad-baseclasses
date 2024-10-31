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
from nomad.datamodel.metainfo.eln import SampleID
from nomad.datamodel.results import ELN, Material, Results
from nomad.metainfo import Quantity, Reference, Section, SectionProxy, SubSection

from .. import BasicSample
from ..design import ActiveFactor, Design, PassiveFactor


class DesignSampleID(SampleID):
    m_def = Section(a_eln=dict(
        hide=['sample_owner']))

    sample_short_name = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity', label='Design id'))

    sample_number = Quantity(
        type=np.dtype(np.int64),
        a_eln=dict(
            component='NumberEditQuantity'
        ))

    def normalize(self, archive, logger):
        # super(DesignSampleID, self).normalize(archive, logger)

        if self.sample_short_name is not None and self.sample_number is not None:
            self.sample_id = f"{self.sample_short_name}-{self.sample_number:06d}"

            if not archive.results:
                archive.results = Results(eln=ELN())
            if not archive.results.eln:
                archive.results.eln = ELN()

            archive.results.eln.lab_ids = []
            archive.results.eln.lab_ids = [self.sample_id]


class ActiveDesignParameter(ArchiveSection):
    m_def = Section(label_quantity='name')

    factor = Quantity(
        type=Reference(ActiveFactor.m_def),
        a_eln=dict(component='ReferenceEditQuantity'))

    value = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(
            component='NumberEditQuantity',
        ))

    set_value = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(
            component='NumberEditQuantity',
        ))

    measured_values = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
    )

    name = Quantity(
        type=str)

    def normalize(self, archive, logger):

        if self.factor is not None:
            self.name = f"{self.factor.label}: Step {self.factor.step} - {self.factor.name}"


class PassiveDesignParameter(ArchiveSection):
    m_def = Section(label_quantity='name')

    factor = Quantity(
        type=Reference(PassiveFactor.m_def),
        a_eln=dict(component='ReferenceEditQuantity'))

    value = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(
            component='NumberEditQuantity',
        ))

    name = Quantity(
        type=str)

    def normalize(self, archive, logger):

        if self.factor is not None:
            self.name = f"{self.factor.label}: Step {self.factor.step} - {self.factor.name}"


class FurtherDesignParameter(ArchiveSection):
    m_def = Section(label_quantity='name')

    name = Quantity(
        type=str,
        a_eln=dict(
            component='StringEditQuantity',
        ))

    value = Quantity(
        type=str,
        a_eln=dict(
            component='StringEditQuantity',
        ))


class DesignSample(BasicSample):

    chemical_composition_or_formulas = Quantity(
        type=str,
        description=(
            'A list of the elements involved'),
        a_eln=dict(component='StringEditQuantity'))

    parent = Quantity(
        type=Reference(SectionProxy("DesignSample")),
        a_eln=dict(component='ReferenceEditQuantity'))

    design = Quantity(
        type=Reference(Design),
        a_eln=dict(component='ReferenceEditQuantity'))

    design_row = Quantity(
        type=np.dtype(np.int64),
        a_eln=dict(component='NumberEditQuantity'))

    data_files = Quantity(
        type=str,
        shape=["*"],
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    active_parameters = SubSection(
        section_def=ActiveDesignParameter, repeats=True)

    passive_parameters = SubSection(
        section_def=PassiveDesignParameter, repeats=True)

    further_parameters = SubSection(
        section_def=FurtherDesignParameter, repeats=True)

    sample_id = SubSection(
        section_def=DesignSampleID)

    def normalize(self, archive, logger):
        super(DesignSample, self).normalize(archive, logger)

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
                for formula in self.chemical_composition_or_formulas.split(",")]
            elements = []
            for f in formulas:
                elements.extend(f.get_chemical_symbols())
            material.elements = list(set(elements))
            if len(formulas) == 1:
                formula = formulas[0]
                material.chemical_formula_hill = formula.get_chemical_formula(
                    mode='hill')
                material.chemical_formula_reduced = formula.get_chemical_formula(
                    mode='reduce')
                material.chemical_formula_descriptive = self.chemical_composition_or_formulas
