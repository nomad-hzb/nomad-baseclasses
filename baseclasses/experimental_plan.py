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
    Reference)

from nomad.datamodel.metainfo.eln import Entity

from . import ProcessOnSample, StandardSample, BatchID
from nomad.datamodel.data import ArchiveSection


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
        section_def=ProcessOnSample, repeats=True)


class ExperimentalPlan(Entity):

    batch_plan_pdf = Quantity(
        type=str,
        a_browser=dict(adaptor='RawFileAdaptor')
    )

    load_standard_processes = Quantity(
        type=bool,
        default=False,
        a_eln=dict(component='BoolEditQuantity')
    )

    create_samples_and_processes = Quantity(
        type=bool,
        default=False,
        a_eln=dict(component='BoolEditQuantity')
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
        section_def=BatchID)

    plan = SubSection(
        section_def=Step, repeats=True)

    def normalize(self, archive, logger):
        super(ExperimentalPlan, self).normalize(archive, logger)

        if archive.data == self and self.name:
            archive.metadata.entry_name = self.name

        steps = []
        if self.standard_plan and self.standard_plan.processes:
            number_of_entries = len(self.standard_plan.processes)
            if len(self.plan) < number_of_entries:
                for step in self.standard_plan.processes:
                    steps.append(Step(name=step.name))
                self.plan = steps

        self.method = "Experimental Plan"
