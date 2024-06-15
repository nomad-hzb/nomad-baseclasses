#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  7 11:44:19 2023

@author: a2853
"""

import chardet
import pandas as pd


def find_data(file_path, encoding):
    with open(file_path, encoding=encoding) as myFile:
        for num, line in enumerate(myFile, 1):
            if "Time [s]" in line:
                return num-1


def get_environment_data(file_path, encoding='utf-8'):
    nrows = find_data(file_path, encoding)
    if nrows is None:
        return
    data = pd.read_csv(file_path, sep="\t", skiprows=nrows, encoding=encoding)

    return data
