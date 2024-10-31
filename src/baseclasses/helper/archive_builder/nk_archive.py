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
from nomad.units import ureg

from baseclasses.data_transformations.data_baseclasses import DataWithStatistics
from baseclasses.data_transformations.nkdata_analysis import NKDataResult


def get_nk_archive(nk_data):
    energy_unit = nk_data.columns[0].strip()
    energy_data = np.array(nk_data[energy_unit])
    if energy_unit.lower() == 'ev':
        energy_data = 1239.84193 / energy_data
        energy_unit = "nm"
    energy_data = energy_data * ureg(energy_unit)

    k_data_format = nk_data.columns[2].strip()
    k_data = np.array(nk_data[k_data_format])
    if k_data_format.lower() == "alpha":
        k_data = 1e-4 / (4*np.pi) * energy_data * (k_data*ureg("1/um"))

    return NKDataResult(
        wavelength=energy_data,
        n_data=DataWithStatistics(data=nk_data['n']),
        k_data=DataWithStatistics(data=k_data)
    )
