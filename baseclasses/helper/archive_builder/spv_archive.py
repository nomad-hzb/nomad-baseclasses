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
import re


from baseclasses.solar_energy import trSPVVoltage, trSPVData, trSPVProperties


def get_spv_archive(spv_dict, spv_data, main_file, spv_entry):

    measurements = []
    for col in spv_data.columns[1:]:
        measurements.append(trSPVVoltage(
            measurement=spv_data[col],
            laser_energy=float(col)
        ))
    spv_entry.data = trSPVData(
        time=spv_data[spv_data.columns[0]],
        voltages=measurements)

    res = re.search(r'TD[^_]*_', "M01_encapsulatedGlass_front_TD167_withBE_ambient_intens.txt")

    spv_entry.properties = trSPVProperties(
        number_of_transients=spv_dict["Number of Transients"],
        number_of_averages=spv_dict["Number of Averages"],
        points_per_transient=spv_dict["Points per Transients"],
        laser_pulse_intensity=float(res.group()[2:-1])
    )
