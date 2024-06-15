# MIT License

# Copyright (c) 2019

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# -*- coding: utf-8 -*-

import pandas as pd


def get_header_data_corrware(filename):

    _header = dict()
    _working = _header
    with open(file=filename, mode="r", encoding="utf8", errors="ignore") as f:
        line = f.readline()
        count = -1
        _technique = ''
        while "End Comments" not in line:
            count += 1
            line = f.readline()
            if ":" not in line:
                if count == 1:
                    _technique = line.strip()
                continue

            if 'Date:' in line and 'Time:' in line:
                date, time = line.replace(
                    'Date:', '').replace(
                    'Time:', '').split()
                _working.update({"Datetime": f"{date} {time}"})
                continue

            line = line.split(":")

            if "Begin" in line[0]:
                key = line[0].replace("Begin", "").strip()
                _working.update({key: {}})
                _working = _working[key]
                continue

            if "End" in line[0]:
                _working = _header
                continue
            value = line[1].strip()
            try:
                value = float(value)
            except BaseException:
                pass
            _working.update({line[0].strip(): value})

    _data = pd.read_csv(filename,
                        skiprows=[0],
                        header=count - 1,
                        delimiter="\t",
                        skip_blank_lines=False).iloc[1:].astype("float64")

    _data = _data.rename(columns=lambda x: x.strip())

    if "Cyclic" in _technique:
        curve = 0
        v_min = _header["Experiment"]["Potential #2"]
        v_max = _header["Experiment"]["Potential #3"]
        _data["curve"] = 0
        v_value_new = _data.iloc[0]["E(Volts)"]
        v_value_start = _data.iloc[0]["E(Volts)"]
        for index, row in _data[1:].iterrows():
            v_value_old = v_value_new
            v_value_new = row["E(Volts)"]
            if (v_value_new < v_value_start and v_value_old > v_value_start
                    and v_max > v_min) or \
                    (v_value_new > v_value_start
                     and v_value_old < v_value_start and v_max < v_min) or \
                    (v_value_new == v_max and v_value_start == v_max and v_value_new != v_value_old) or \
                    (v_value_new == v_min and v_value_start == v_min and v_value_new != v_value_old):
                curve += 1
            _data.at[index, "curve"] = curve
        _data = _data.set_index("curve")

    return _header, _data, _technique
