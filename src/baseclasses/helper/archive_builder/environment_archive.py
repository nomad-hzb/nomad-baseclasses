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

import pandas as pd

from baseclasses.assays import EnvironmentData, TemperatureSensors


def get_environment_archive(env_data, env_entry):

    env_entry.data = EnvironmentData(
        time=env_data["Time [s]"],
        datetime=pd.to_datetime(env_data["Date"] + env_data["Time"], format='%b %d %Y%H:%M:%S').to_list(),
        humidity=env_data["Humidity[%]"],
        temperature=env_data['Temperature[°C]'],
        temperature_sensors=[
            TemperatureSensors(temperature=env_data[col], name=col)
            for col in env_data.columns if col.startswith("TH")
        ])
