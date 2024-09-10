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

from nomad.metainfo import (
    Quantity,
    Reference,
    Section,
)

from .. import BaseMeasurement
from ..helper.utilities import get_entry_id_from_file_name, update_archive


class GeneralMeasurement(BaseMeasurement):

    m_def = Section()

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    def normalize(self, archive, logger):
        from nomad.search import search

        file_id = get_entry_id_from_file_name(self.data_file, archive)
        query = {
            'entry_id': file_id,
        }
        search_result = search(
            owner='all',
            query=query,
            user_id=archive.metadata.main_author.user_id)
        entry_type = search_result.data[0].get('entry_type') if len(search_result.data) == 1 else None

        if entry_type != 'ParsedGeneralMeasurementFile':
            entry_dict = self.m_to_dict()
            # TODO change the next block when adding new parsers for a set of general measurements
            #if entry_type == 'ParsedTxtFile':
            #    entry_dict['m_def'] = 'nomad_chemical_energy.schema_packages.hzb_general_measurement_package.TxtMeasurement'
            new_entry = self.m_from_dict(entry_dict)
            file_name = f'{self.data_file}.archive.json'
            update_archive(new_entry, archive, file_name)

        super(GeneralMeasurement, self).normalize(archive, logger)

