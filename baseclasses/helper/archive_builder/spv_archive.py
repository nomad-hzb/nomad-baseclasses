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
import pandas as pd

from baseclasses.solar_energy import trSPVVoltage, trSPVData, trSPVProperties


filter_to_intensity = {
    3: 10000,
    36: 1000,
    167: 100
}


def get_spv_archive(spv_dict, spv_data, main_file_path, spv_entry):
    capacitance = None
    directory, main_file = os.path.split(main_file_path)
    try:
        lab_id = spv_entry.samples[0].lab_id
        mapping = pd.read_csv(os.path.join(directory, "sample_capacitance.csv"), index_col=0, header=None)
        capacitance = mapping.loc[lab_id]
    except Exception as e:
        print(e)

    measurements = []
    for col in spv_data.columns[1:]:
        measurements.append(trSPVVoltage(
            measurement=spv_data[col],
            laser_energy=float(col)
        ))
    spv_entry.data = trSPVData(
        time=spv_data[spv_data.columns[0]],
        voltages=measurements)

    res = re.search(r'TD[^_]*_', main_file)
    filter_setup = res.group()[2:-1]

    spv_entry.properties = trSPVProperties(
        number_of_transients=spv_dict["Number of Transients"],
        number_of_averages=spv_dict["Number of Averages"],
        points_per_transient=spv_dict["Points per Transients"],
        laser_pulse_intensity=filter_to_intensity.get(int(filter_setup)),
        filter_setup=filter_setup,
        capacitance=capacitance
    )
