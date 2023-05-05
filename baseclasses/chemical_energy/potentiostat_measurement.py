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

from nomad.metainfo import (Quantity, Reference)

from .. import MeasurementOnSample
from .cesample import Electrode, Electrolyte, CESample, ElectroChemicalCell


class PotentiostatMeasurement(MeasurementOnSample):

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

    electrochemical_cell = Quantity(
        type=Reference(ElectroChemicalCell.m_def),
        a_eln=dict(component='ReferenceEditQuantity'))

    def normalize(self, archive, logger):
        super(PotentiostatMeasurement, self).normalize(archive, logger)

        if self.electrochemical_cell:
            if self.working_electrode is None:
                self.working_electrode = self.electrochemical_cell.working_electrode

            if self.reference_electrode is None:
                self.reference_electrode = self.electrochemical_cell.reference_electrode

            if self.counter_electrode is None:
                self.counter_electrode = self.electrochemical_cell.counter_electrode

            if self.electrolyte is None:
                self.electrolyte = self.electrochemical_cell.electrolyte
