#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 19 11:18:04 2022

@author: a2853
"""
import pandas as pd

encoding = "iso-8859-1"


def headeranddelimiter(file):
    header = 0
    header_found = False
    decimal = "."
    with open(file, "br") as f:
        for i, line in enumerate(f):
            line = line.decode(encoding)
            if line.startswith("mode") or line.startswith("freq/Hz"):
                header = i
                header_found = True
            if header_found:
                if "," in line and "." not in line:
                    decimal = ","
                if "." in line and decimal == ",":
                    raise Exception("decimal delimiter . and , found")

    return header, decimal


def parse_line(line, separator, encoding):

    stripped_line = line.strip()

    if not stripped_line:
        return '', ''

    if separator in stripped_line:
        split = list(filter(None, stripped_line.split(separator)))
        if len(split) < 2:
            return None, None
        key, value = split[0], ':'.join(split[1:])
        return key.strip(), value.strip()

    return None, None


def read_mps_file(datafile, encoding="iso-8859-1"):
    """Reads an MPS file, splits by : and if technique splits by spaces"""
    res = {}
    tmp = res
    separator = ":"

    with open(datafile, 'rb') as file:
        for line in file.readlines():
            key, value = parse_line(line, separator, encoding)

            if key is None and value is None:
                continue

            if key == '' and value == '':
                separator = ":"
                tmp = res
                continue

            if "Technique" in key:
                separator = "  "
                res.update({f"{key} {value}": {}})
                tmp = res[f"{key} {value}"]
                continue

            tmp.update({key: value})

    return res


def read_mpt_file(filename, encoding="iso-8859-1"):
    """Reads an MPS file, splits by : and if technique splits by spaces"""
    metadata = {}
    separator = ":"
    technique = ''
    count = 0
    key = ''
    with open(filename, 'rb') as file:
        for line in file.readlines():
            line = line.decode(encoding)
            if count == 3:
                technique = line.strip()
            count += 1
            if line.startswith("mode"):
                break
            if line.startswith("vs."):
                key_old = key
            if line.strip() == '':
                continue

            if ":" in line:
                separator = ":"
            else:
                separator = "  "

            key, value = parse_line(line, separator, encoding)
            try:
                value = float(value)
            except BaseException:
                pass
            if key is None and value is None:
                continue

            if line.startswith("vs."):
                metadata.update({f"{key_old} {key}": value})
                continue
            metadata.update({key: value})

    header_line, decimal = headeranddelimiter(filename)
    data = pd.read_csv(
        filename,
        sep="\t",
        header=header_line,
        encoding=encoding,
        skip_blank_lines=False,
        decimal=decimal)

    if "Cyclic" in technique and 'nc cycles' in metadata:
        curve = 0
        data["curve"] = 0
        v_value_new = data.iloc[0]["Ewe/V"]
        v_value_start = data.iloc[0]["Ewe/V"]
        for index, row in data[1:].iterrows():
            v_value_old = v_value_new
            v_value_new = row["Ewe/V"]
            if v_value_new < v_value_start and v_value_old > v_value_start:
                curve += 1

            data.at[index, "curve"] = curve
        data = data.set_index("curve")

    return metadata, data, technique


# filename = '/home/a2853/Documents/Projects/nomad/hysprintlab/manuel/HZB_MaVa_20230519_ITO._OCV_C01.mpt'
# r, data, t = read_mpt_file(filename)
