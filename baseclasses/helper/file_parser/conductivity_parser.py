# from xarray import Dataset
# from scipy.signal import savgol_filter
import numpy as np
import pandas as pd
import os
from datetime import datetime


def read_conductivity(file):
    # Read MeasurementFile
    data = pd.read_csv(file, header=0, skiprows=4, index_col=["X (mm)", "Y (mm)"])

    x_pos = np.array(data.index.get_level_values("X (mm)").unique())
    y_pos = np.array(data.index.get_level_values("Y (mm)").unique())
    nx = len(x_pos)
    ny = len(y_pos)
    conductivity_data = np.zeros((nx, ny))
    for idx in range(data["Resistance (Ohms)"].shape[0]):
        conductivity_data[idx % nx, idx // nx] = data.loc[idx % nx, idx // nx]["Resistance (Ohms)"]

    metadata = pd.read_csv(file, header=None, index_col=[0], nrows=4)

    return conductivity_data, x_pos, y_pos, metadata
