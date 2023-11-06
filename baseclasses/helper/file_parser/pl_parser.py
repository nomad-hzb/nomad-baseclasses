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
import numpy as np
import ast


def get_pl_data_iris(filename, encoding='utf-8'):
    # Block to clean up some bad characters found in the file which gives
    # trouble reading.
    f = open(filename, 'r', encoding=encoding)
    filedata = f.read()
    f.close()

    newdata = filedata.replace("²", "^2")

    f = open(filename, 'w')
    f.write(newdata)
    f.close()

    with open(filename) as f:
        df_header = pd.read_csv(
            f,
            skiprows=0,
            nrows=21,
            header=None,
            sep=',',
            index_col=0,
            encoding='unicode_escape',
            engine='python')

    with open(filename) as f:
        df_data = pd.read_csv(
            f,
            header=None,
            skiprows=22,
            sep=',',
            encoding='unicode_escape',
            engine='python')

    pl_dict = {}
    pl_dict['name'] = df_header.iloc[0, 0]
    pl_dict['wavelength_start'] = float(df_header.iloc[3, 0])
    pl_dict['wavelength_stop'] = float(df_header.iloc[4, 0])
    pl_dict['wavelength_step_size'] = float(df_header.iloc[5, 0])
    pl_dict['integration_time'] = float(df_header.iloc[13, 0])
    pl_dict['temperature'] = float(df_header.iloc[15, 0])
    pl_dict['number_of_averages'] = float(df_header.iloc[12, 0])
    pl_dict['lamp'] = df_header.iloc[14, 0]

    pl_dict['data'] = {"wavelength": df_data[0],  "intensity": df_data[1]}

    return pl_dict


def get_pl_data(filename, encoding='utf-8'):
    # Block to clean up some bad characters found in the file which gives
    # trouble reading.
    f = open(filename, 'r', encoding=encoding)
    filedata = f.read()
    f.close()

    if filedata.startswith("Labels"):
        return get_pl_data_iris(filename, encoding), "IRIS HZBGloveBoxes"
    return None, None
