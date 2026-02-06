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

from baseclasses.solar_energy import trSPVData, trSPVProperties, trSPVVoltage

filter_to_intensity = {3: 10000, 36: 1000, 167: 100}


def get_spv_archive(spv_dict, spv_data, main_file_path, spv_entry):
    capacitance = None

    measurements = []
    for col in spv_data.columns[1:]:
        measurements.append(
            trSPVVoltage(measurement=spv_data[col], laser_energy=float(col))
        )
    spv_entry.data = trSPVData(
        time=spv_data[spv_data.columns[0]], voltages=measurements
    )
    if spv_dict:
        spv_entry.properties = trSPVProperties(
            number_of_transients=spv_dict.get('Number of Transients'),
            number_of_averages=spv_dict.get('Number of Averages'),
            points_per_transient=spv_dict.get('Points per Transients'),
            capacitance=capacitance,
        )
