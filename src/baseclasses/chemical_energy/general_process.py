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
    Section,
)

from .. import BaseMeasurement
from ..helper.utilities import set_sample_reference


class GeneralProcess(BaseMeasurement):

    m_def = Section()

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    search_sample_in_same_upload = Quantity(
        type=bool,
        shape=[],
        default=True,
        description="""
            TRUE if the the linked sample must be in the same upload. 
            FALSE if the linked sample might be stored in other uploads.
        """,
        a_eln=dict(component='BoolEditQuantity'),
    )


    def normalize(self, archive, logger):
        if not self.samples:
            sample_id = self.data_file.split(".")[0].split("-")[0]
            upload_id = None
            if self.search_sample_in_same_upload:
                upload_id = archive.metadata.upload_id
            set_sample_reference(archive, self, sample_id, upload_id)
        super(GeneralProcess, self).normalize(archive, logger)

