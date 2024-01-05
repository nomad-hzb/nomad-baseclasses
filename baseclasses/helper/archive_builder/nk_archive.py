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

from baseclasses.data_transformations.data_baseclasses import DataWithStatistics
from baseclasses.data_transformations.nkdata_analysis import nkDataAnalysisResult


def get_nk_archive(nk_data):
    return nkDataAnalysisResult(
        wavelength=nk_data['nm'],
        n_data=DataWithStatistics(data=nk_data['n']),
        k_data=DataWithStatistics(data=nk_data['k']),
    )
