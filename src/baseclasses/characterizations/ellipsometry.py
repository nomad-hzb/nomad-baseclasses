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

from nomad.metainfo import Quantity, Section

# from nomad.datamodel.data import ArchiveSection
from .. import BaseMeasurement, LibraryMeasurement


class Ellipsometry(BaseMeasurement):
    '''Ellipsometry'''

    data_file = Quantity(
        type=str,
        shape=['*'],
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    def normalize(self, archive, logger):
        self.method = "Ellipsometry"
        super().normalize(archive, logger)


class EllipsometryLibrary(LibraryMeasurement):
    '''Ellipsometry Measurement'''

    m_def = Section(
        a_eln=dict(hide=['certified_values', 'certification_institute']))

    def normalize(self, archive, logger):
        super().normalize(archive, logger)
        self.method = "Ellipsometry"
