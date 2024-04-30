# from xarray import Dataset
# from scipy.signal import savgol_filter
import numpy as np
import pandas as pd
import os
from datetime import datetime


def read_conductivity(file_path: str):
    with open(file_path, 'r+') as file_handle:
        header = {}
        line_split = file_handle.readline().split(";")
        while len(line_split) == 2:
            key = line_split[0].strip().strip('"')
            value = line_split[1].strip().strip('"')
            header[key] = value
            line_split = file_handle.readline().split(";")
        wavelengths = np.array(line_split[-1].strip().split(","))
        columns = ["x", "y", "z", "resistance"]
        df = pd.read_csv(file_handle, names=columns, delimiter=';|,', engine='python')
    return header, df.dropna(axis=1)


# file = "/home/a2853/Documents/Projects/nomad/thomas/HZB_FaAk_20240426_4025-12#Resistance2024_04_25_0941.csv"
# h, df = read_conductivity(file)
# df
