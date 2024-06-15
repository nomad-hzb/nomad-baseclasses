#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  7 11:44:19 2023

@author: a2853
"""

import pandas as pd


def is_float(string):
    try:
        # Return true if float
        float(string)
        return True
    except ValueError:
        # Return False if Error
        return False


def find_footer(file_path, encoding):
    with open(file_path) as myFile:
        for num, line in enumerate(myFile, 1):
            if "BEGIN_METADATA" in line:
                return num-5


def get_spv_data(file_path, encoding='utf-8'):
    nrows = find_footer(file_path, encoding)
    if nrows is None:
        return
    data = pd.read_csv(file_path, sep="\t", nrows=nrows)

    md_dict = {}
    with open(file_path, encoding=encoding) as myFile:
        for num, line in enumerate(myFile, 1):
            if num < nrows or ":" not in line:
                continue
            line_split = line.split(":")
            line_split[0] = line_split[0].replace("#", "")
            value = float(line_split[1].strip()) if is_float(line_split[1].strip()) else line_split[1].strip()
            md_dict.update({line_split[0].strip(): value})
    return md_dict, data


# md, d = get_spv_data(
#     "/home/a2853/Documents/Projects/nomad/hysprintlab/valerio/Zahra/M01/M01_encapsulatedGlass_front_TD167_withBE_ambient_intens.txt")
