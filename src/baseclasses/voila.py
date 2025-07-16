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
import os

from nomad.datamodel.metainfo.eln import Entity
from nomad.metainfo import Quantity


class VoilaNotebook(Entity):
    notebook_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'),
    )

    tags = Quantity(
        type=str,
        shape=['*'],
        description='Add a tag that can be used for search.',
        a_eln=dict(component='StringEditQuantity'),
    )

    def normalize(self, archive, logger):
        super().normalize(archive, logger)

        if self.notebook_file and os.path.splitext(self.notebook_file)[-1] != '.ipynb':
            logger.error('Please upload a jupyter notebook file (.ipynb).')
