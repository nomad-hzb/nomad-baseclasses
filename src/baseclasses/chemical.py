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

from nomad.datamodel.metainfo.eln import Substance
from nomad.metainfo import MEnum, Quantity


class Chemical(Substance):
    state_of_matter = Quantity(
        type=MEnum('Liquid', 'Solid', 'Gas'),
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
        ))

    def normalize(self, archive, logger):
        super(Chemical, self).normalize(archive, logger)
        if self.cas_name is not None:
            archive.metadata.entry_name = self.cas_name
