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

def find_row_with_data(file_object):
    # Find the row with the data
    count = 1
    while(True):
        next_line = file_object.readline()
        if next_line.strip() and not next_line.strip().startswith('#'):
            return count
        count += 1
    return -1 # No data found

def get_nk_data(filename, encoding='utf-8'):
    # Block to clean up some bad characters found in the file which gives
    # trouble reading.
    with open(filename, 'r', encoding=encoding) as f:
        first_line = f.readline().strip("#").split(";")
        count = find_row_with_data(f)

    metadata = {"Name": first_line[0].strip() if len(first_line) > 0 else "",
                "Formula": first_line[1].strip() if len(first_line) > 1 else "",
                "Reference": first_line[2].strip() if len(first_line) > 2 else "",
                "Comment": first_line[3].strip() if len(first_line) > 3 else ""
                }
    data = pd.read_csv(filename, sep='\t', encoding=encoding, header=0, skiprows=count)
    return data, metadata

# data, m = get_nk_data('/home/a2853/Documents/Projects/nomad/hysprintlab/klaus/BCP.nk')
# print(data.columns[0])
# print(m)