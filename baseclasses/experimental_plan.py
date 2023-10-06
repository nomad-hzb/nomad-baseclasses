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
    Reference, MProxy)

from nomad.datamodel.metainfo.eln import Entity

from . import BaseProcess, StandardSample
from .customreadable_identifier import ReadableIdentifiersCustom
from nomad.datamodel.data import ArchiveSection
from .wet_chemical_deposition import PrecursorSolution


class ParametersVaried(ArchiveSection):
    m_def = Section(label_quantity='parameter_path')

    parameter_path = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'))

    parameter_unit = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'))

    parameter_values = Quantity(
        type=str,
        shape=['*'],
        a_eln=dict(component='StringEditQuantity'))


def get_unit(section, path):
    if isinstance(section, MProxy):
        section.m_resolved()
    path_split = path.split("/")
    next_key = path_split[0]
    if len(path_split) == 1:
        return str(getattr(getattr(type(section), next_key), "unit"))
    elif isinstance(section, list):
        return get_unit(section[np.int64(next_key)], "/".join(path_split[1:]))
    elif isinstance(section, PrecursorSolution):
        section.solution_details = section.solution.m_copy(deep=True)
        return get_unit(section[next_key], "/".join(path_split[1:]))
    else:
        return get_unit(section[next_key], "/".join(path_split[1:]))


class Step(ArchiveSection):
    m_def = Section(label_quantity='name')

    name = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'))

    vary_parameters = Quantity(
        type=bool,
        default=False,
        a_eln=dict(component='BoolEditQuantity')
    )

    batch_processes = SubSection(
        section_def=BaseProcess, repeats=True)

    process_reference = Quantity(
        type=Reference(BaseProcess.m_def),
        a_eln=dict(component='ReferenceEditQuantity')
    )

    parameters = SubSection(
        section_def=ParametersVaried, repeats=True)

    def normalize(self, archive, logger):
        if self.process_reference is None and self.batch_processes:
            self.process_reference = self.batch_processes[0]
        if self.process_reference and self.name is None:
            self.name = self.process_reference.name

        if self.process_reference:
            for p in self.parameters:
                if p.parameter_unit:
                    continue
                p.parameter_unit = get_unit(self.process_reference, p.parameter_path)
            pass


class ExperimentalPlan(Entity):

    batch_plan_pdf = Quantity(
        type=str,
        a_browser=dict(adaptor='RawFileAdaptor')
    )

    load_standard_processes = Quantity(
        type=bool,
        default=False,
        a_eln=dict(component='ButtonEditQuantity')
    )

    create_samples_and_processes = Quantity(
        type=bool,
        default=False,
        a_eln=dict(component='ButtonEditQuantity')
    )

    number_of_substrates = Quantity(
        type=np.dtype(np.int64),
        description='The number of substrates in the batch.',
        default=0,
        a_eln=dict(component='NumberEditQuantity')
    )

    substrates_per_subbatch = Quantity(
        type=np.dtype(np.int64),
        default=1,
        a_eln=dict(component='NumberEditQuantity')
    )

    standard_plan = Quantity(
        type=Reference(StandardSample.m_def),
        a_eln=dict(component='ReferenceEditQuantity')
    )

    batch_id = SubSection(
        section_def=ReadableIdentifiersCustom)

    plan = SubSection(
        section_def=Step, repeats=True)

    # solution_manufacturing = SubSection(
    #     section_def=SolutionManufacturing, repeats=True)

    def normalize(self, archive, logger):
        super(ExperimentalPlan, self).normalize(archive, logger)

        if archive.data == self and self.name:
            archive.metadata.entry_name = self.name

        steps = []
        # solutions = []
        if self.standard_plan and self.standard_plan.processes and not self.plan:
            number_of_entries = len(self.standard_plan.processes)
            if len(self.plan) < number_of_entries:
                for step in self.standard_plan.processes:
                    steps.append(Step(name=step.name, process_reference=step))
                self.plan = steps

        self.method = "Experimental Plan"
