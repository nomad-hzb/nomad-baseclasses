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

import re
import locale
from io import StringIO

import pandas as pd
from pandas.api.types import is_numeric_dtype


def _read_curve_data(fid, curve_length) -> tuple:
    """helper function to process an EXPLAIN Table
    Args:
        fid (int): a file handle pointer to the table position in the data files
    Returns:
        keys (list): column identifier (e.g. Vf)
        units (list): column unit type (e.g. V)
        curve (DataFrame): Table data saved as a pandas Dataframe
    """
    pos = 0
    curve = fid.readline().strip() + "\n"  # grab header data
    if len(curve) <= 1:
        return [], [], pd.DataFrame()

    units = fid.readline().strip().split("\t")
    cur_line = fid.readline().strip()
    line_count = 0
    while not re.search(r"(CURVE|EXPERIMENTABORTED)", cur_line):
        line_count += 1
        curve += cur_line + "\n"
        pos = fid.tell()
        cur_line = fid.readline().strip()
        if fid.tell() == pos or (curve_length is not None and curve_length == line_count):
            break
    try:
        curve = pd.read_csv(StringIO(curve), delimiter="\t",
                            header=0, index_col=0)
    except:
        curve = pd.read_csv(StringIO(curve), delimiter="\t",
                            header=0, index_col=0, decimal=",")

    keys = curve.columns.values.tolist()
    units = units[1:]

    return keys, units, curve


def get_number(value_str):
    if "," in value_str:
        return get_number(value_str.replace(",", "."))
    try:
        return locale.atof(value_str)
    except:
        return value_str


def get_curve(f, _header, _curve_units, curve_length=None):
    curve_keys, curve_units, curve = _read_curve_data(f, curve_length)
    REQUIRED_UNITS: dict = dict(CV=dict(Vf="V vs. Ref.", Im="A"))
    if curve.empty:
        return None

    for key in curve_keys:
        nonnumeric_keys = [
            "Over",
        ]
        if key in nonnumeric_keys:
            continue
        elif key == "Pt":
            if not is_numeric_dtype(curve.index):
                curve.index = curve.index.map(int)
        else:
            if not is_numeric_dtype(curve[key]):
                try:
                    curve[key] = curve[key].map(locale.atof)
                except:
                    curve[key] = curve[key].apply(
                        lambda x: x.replace(",", "."))
                    curve[key] = curve[key].map(locale.atof)
    # print(curve_keys, curve_units)
    # print(_curve_units, curve_units)

    # if not bool(_curve_units.items()):
    #     exp_type = _header["TAG"]
    #     for key, unit in zip(curve_keys, curve_units):
    #         if exp_type in REQUIRED_UNITS.keys():
    #             if key in REQUIRED_UNITS[exp_type].keys():
    #                 assert (
    #                     unit == REQUIRED_UNITS[exp_type][key]
    #                 ), "Unit error for '{}': Expected '{}', found '{}'!".format(
    #                     key, REQUIRED_UNITS[exp_type][key], unit
    #                 )
    #         _curve_units[key] = unit
    # else:
    #     for key, unit in zip(curve_keys, curve_units):
    #         assert _curve_units[key] == unit, "Unit mismatch found!"

    return curve


def get_header_and_data(filename):

    _header = dict()
    _curve_units = dict()
    _curves = []

    pos = 0
    with open(file=filename, mode="r", encoding="utf8", errors="ignore") as f:
        cur_line = f.readline().split("\t")
        while not re.search(r"(^|Z|VFP|EFM|DISK)CURVE", cur_line[0]):
            if f.tell() == pos:
                break

            pos = f.tell()
            cur_line = f.readline().strip().split("\t")
            if len(cur_line[0]) == 0:
                pass

            if len(cur_line) > 1:
                if cur_line[0] in ["OCVCURVE", "RINGCURVE", ] and len(cur_line) > 2:
                    table_length = get_number(cur_line[2])
                    _header[cur_line[0]] = get_curve(
                        f, _header, _curve_units, table_length)
                # data format: key, type, value
                if cur_line[1].strip() in ["LABEL", "PSTAT"]:
                    _header[cur_line[0]] = cur_line[2]
                    if cur_line[0] in ["TITLE"] and len(cur_line) > 3:
                        _header["SAMPLE_ID"] = cur_line[3]
                elif cur_line[1] in ["POTEN"] and len(cur_line) == 5:
                    tmp_value = get_number(cur_line[2])
                    _header[cur_line[0]] = (tmp_value, cur_line[3] == "T")

                elif cur_line[1] in ["QUANT", "IQUANT", "POTEN"]:
                    # locale-friendly alternative to float
                    _header[cur_line[0]] = get_number(cur_line[2])
                elif cur_line[1] in ["IQUANT", "SELECTOR"]:
                    _header[cur_line[0]] = int(cur_line[2])
                elif cur_line[1] in ["TOGGLE"]:
                    _header[cur_line[0]] = cur_line[2] == "T"
                elif cur_line[1] in ["ONEPARAM"]:
                    tmp_value = get_number(cur_line[3])
                    _header[cur_line[0]] = (tmp_value, cur_line[2] == "T")
                elif cur_line[1] == "TWOPARAM":
                    tmp_start = get_number(cur_line[3])
                    tmp_finish = get_number(cur_line[4])
                    _header[cur_line[0]] = {
                        "enable": cur_line[2] == "T",
                        # locale-friendly alternative to float
                        "start": tmp_start,
                        # locale-friendly alternative to float
                        "finish": tmp_finish,
                    }
                elif cur_line[0] == "TAG":
                    _header["TAG"] = cur_line[1]
                elif cur_line[0] == "NOTES":
                    n_notes = int(cur_line[2])
                    note = ""
                    for _ in range(n_notes):
                        note += f.readline().strip() + "\n"
                    _header[cur_line[0]] = note

        header_length = f.tell()

    assert (
        len(_header) > 0
    ), "Must read file header before curves can be extracted."
    curve_count = 0

    with open(file=filename, mode="r", encoding="utf8", errors="ignore") as f:
        f.seek(header_length)  # skip to end of header

        while True:
            curve = get_curve(f, _header, _curve_units)
            if curve is None:
                break
            _curves.append(curve)
            curve_count += 1

    return _header, _curves
