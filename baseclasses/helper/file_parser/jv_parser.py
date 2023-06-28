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


def get_jv_data(filename, encoding='utf-8'):
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
        df = pd.read_csv(
            f,
            skiprows=8,
            nrows=9,
            sep='\t',
            index_col=0,
            engine='python',
            encoding='unicode_escape')
    with open(filename) as f:
        df_header = pd.read_csv(
            f,
            skiprows=1,
            nrows=6,
            header=None,
            sep=':|\t',
            index_col=0,
            encoding='unicode_escape',
            engine='python')
    with open(filename) as f:
        df_curves = pd.read_csv(
            f,
            header=19,
            skiprows=[20],
            sep='\t',
            encoding='unicode_escape',
            engine='python')
        df_curves = df_curves.dropna(how='all', axis=1)

    df_header.replace([np.inf, -np.inf, np.nan], 0, inplace=True)
    df.replace([np.inf, -np.inf,np.nan], 0, inplace=True)

    jv_dict = {}
    jv_dict['active_area'] = df_header.iloc[0, 1]
    jv_dict['intensity'] = df_header.iloc[1, 1]
    jv_dict['integration_time'] = df_header.iloc[2, 1]
    jv_dict['settling_time'] = df_header.iloc[3, 1]
    jv_dict['averaging'] = df_header.iloc[4, 1]
    jv_dict['compliance'] = df_header.iloc[5, 1]

    jv_dict['J_sc'] = list(abs(df.iloc[0]))[:-1]
    jv_dict['V_oc'] = list(df.iloc[1])[:-1]
    jv_dict['Fill_factor'] = list(df.iloc[2])[:-1]
    jv_dict['Efficiency'] = list(df.iloc[3])[:-1]
    jv_dict['P_MPP'] = list(df.iloc[4])[:-1]
    jv_dict['J_MPP'] = list(abs(df.iloc[5]))[:-1]
    jv_dict['U_MPP'] = list(df.iloc[6])[:-1]
    jv_dict['R_ser'] = list(df.iloc[7])[:-1]
    jv_dict['R_par'] = list(df.iloc[8])[:-1]

    jv_dict['jv_curve'] = []
    for column in range(1, len(df_curves.columns)):
        jv_dict['jv_curve'].append({'name': df_curves.columns[column],
                                    'voltage': df_curves[df_curves.columns[0]].values,
                                    'current_density': df_curves[df_curves.columns[column]].values})

    return jv_dict
