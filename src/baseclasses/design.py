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
from nomad.metainfo import MEnum, Quantity, Section, SubSection

from . import SampleID


class DesignID(SampleID):
    m_def = Section(a_eln=dict(
        hide=['sample_owner', 'certified_values', 'certification_institute']))

    sample_short_name = Quantity(
        type=str,
        default="catlab-wp4-doe",
        a_eln=dict(component='StringEditQuantity', label='Project Name'))

    sample_id = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity', label='Design id'))

    design_number = Quantity(
        type=np.dtype(np.int64),
        a_eln=dict(
            component='NumberEditQuantity'
        ))

    def normalize(self, archive, logger):
        super().normalize(archive, logger)

        if self.sample_short_name is not None and self.design_number is not None:
            self.sample_id = f"{self.sample_short_name}-{self.design_number:04d}"
            archive.results.eln.lab_ids = []
            archive.results.eln.lab_ids = [self.sample_id]


class Factor(ArchiveSection):
    m_def = Section(label_quantity='label')

    label = Quantity(
        type=str,
    )

    name = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'))

    unit = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'))

    step = Quantity(
        type=np.dtype(np.int64),
        a_eln=dict(component='NumberEditQuantity')
    )


class ActiveFactor(Factor):
    m_def = Section(label_quantity='label', a_eln=dict(
        properties=dict(
            order=[
                "name",
                "step",
                "unit",
                "minimum_value",
                "maximum_value",
                "mean"
            ])))

    minimum_value = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(
            component='NumberEditQuantity',
        ))

    maximum_value = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(
            component='NumberEditQuantity',
        ))

    mean = Quantity(
        type=MEnum([
            'linear',
            'log']),
        default='linear',
        a_eln=dict(
            component='EnumEditQuantity'
        ))


class PassiveFactor(Factor):
    m_def = Section(label_quantity='label', a_eln=dict(
        properties=dict(
            order=[
                "name",
                "step",
                "unit",
                "value",
            ])))

    value = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(
            component='NumberEditQuantity',
        ))


class Design(Entity):

    create_design = Quantity(
        type=bool,
        default=False,
        a_eln=dict(component='ActionEditQuantity')
    )

    design_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    chemical_composition_or_formulas = Quantity(
        type=str,
        description=(
            'A list of the elements involved'),
        a_eln=dict(component='StringEditQuantity'))

    normalized_factor_lower = Quantity(
        type=np.dtype(np.int64),
        default=-1,
        description=(
            'The lower value of normalized design.'),
        a_eln=dict(component='NumberEditQuantity'))

    normalized_factor_upper = Quantity(
        type=np.dtype(np.int64),
        default=1,
        description=(
            'The upper value of normalized design.'),
        a_eln=dict(component='NumberEditQuantity'))

    active_factors = SubSection(
        section_def=ActiveFactor, repeats=True)

    passive_factors = SubSection(
        section_def=PassiveFactor, repeats=True)

    design_id = SubSection(
        section_def=DesignID)

    def normalize(self, archive, logger):
        super().normalize(archive, logger)

        if self.active_factors is not None:
            for i, factor in enumerate(self.active_factors):
                factor.label = chr(ord('@') + (i + 1))

        if self.passive_factors is not None:
            start_passive = len(
                self.active_factors) if self.active_factors is not None else 0
            for i, factor in enumerate(self.passive_factors):
                factor.label = chr(ord('@') + (i + 1 + start_passive))

        self.method = "Design"
