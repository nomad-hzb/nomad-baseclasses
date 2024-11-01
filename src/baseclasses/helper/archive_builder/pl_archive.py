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

import numpy as np

from baseclasses.solar_energy.plmeasurement import PLData, PLProperties


def get_pl_archive(pl_dict, mainfile, plm):
    plm.name = pl_dict.get('name')
    plm.file_name = os.path.basename(mainfile)
    plm.properties = PLProperties(
        integration_time=pl_dict.get('integration_time'),
        number_of_averages=pl_dict.get('number_of_averages'),
        spot_size=pl_dict.get('spot_size'),
        wavelength_start=pl_dict.get('wavelength_start'),
        wavelength_stop=pl_dict.get('wavelength_stop'),
        wavelength_step_size=pl_dict.get('wavelength_step_size'),
        lamp=pl_dict.get('lamp'),
        temperature=pl_dict.get('temperature'),
    )

    data = pl_dict.get('data')
    if data is not None:
        plm.data = PLData(
            wavelength=np.array(data.get('wavelength')),
            intensity=np.array(data.get('intensity')),
        )
