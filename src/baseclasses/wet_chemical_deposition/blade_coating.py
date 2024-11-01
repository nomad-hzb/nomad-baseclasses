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


from nomad.metainfo import Section

from .wet_chemical_deposition import WetChemicalDeposition


class BladeCoating(WetChemicalDeposition):
    '''Base class for blade coating of a sample'''
    m_def = Section(
        # links = ['http://purl.obolibrary.org/obo/CHMO_0001471'],
    )

    def normalize(self, archive, logger):
        super().normalize(archive, logger)
        self.method = "Blade Coating"
