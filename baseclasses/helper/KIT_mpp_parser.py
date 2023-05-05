import pandas as pd
import numpy as np
from datetime import datetime

# import glob

from baseclasses.solar_energy.mpp_tracking import MPPTrackingProperties


def get_parameter(d, key):
    return d[key] if key in d else None


def get_mpp_data(filename, encoding='utf-8'):

    df = pd.read_csv(
        filename,
        skiprows=0,
        sep='\t',
        # index_col=0,
        encoding=encoding,
        engine='python')
    header_dict = {}
    for i, row in df.iterrows():

        if "Time Difference" in row[0]:
            headerlines = i
            break

        if i == 0:
            header_dict.update({"datetime": f"{row[0]} {row[1]}"})
            continue
        key = row[0].lower().replace(" ", "_")
        try:
            header_dict.update({key: float(row[1])})
        except BaseException:
            header_dict.update({key: row[1]})

    df = pd.read_csv(
        filename,
        skiprows=range(
            headerlines + 2,
            headerlines + 3),
        sep="\t",
        header=headerlines + 1,
        encoding=encoding,
    )

    return header_dict, df


def get_mpp_archive(header_dict, df, mpp_entitiy, mainfile=None):

    mpp_entitiy.time = np.array(df["Time Difference"])
    mpp_entitiy.power_density = np.array(df["Power"])
    mpp_entitiy.voltage = np.array(df["Voltage"])
    mpp_entitiy.current_density = np.array(df["Current Density"])
    mpp_entitiy.efficiency = np.array(df["PCE"])
    if mainfile is not None:
        mpp_entitiy.data_file = mainfile

    datetime_str = get_parameter(header_dict, "datetime")
    datetime_object = datetime.strptime(
        datetime_str, '%Y-%m-%d %H:%M PM')
    mpp_entitiy.datetime = datetime_object.strftime(
        "%Y-%m-%d %H:%M:%S.%f")

    properties = MPPTrackingProperties()
    properties.start_voltage_manually = get_parameter(
        header_dict, "start_voltage_manually") == "true"
    properties.perturbation_frequency = get_parameter(
        header_dict, "perturbation_frequency_[s]")
    properties.sampling = get_parameter(header_dict, "sampling")
    properties.perturbation_voltage = get_parameter(
        header_dict, "perturbation_voltage_[v]")
    properties.perturbation_delay = get_parameter(
        header_dict, "perturbation_delay_[s]")
    properties.time = get_parameter(header_dict, "time_[s]")
    properties.status = get_parameter(header_dict, "status")
    properties.last_pce = get_parameter(header_dict, "last_pce_[%]")
    properties.last_vmpp = get_parameter(header_dict, "last_vmpp_[v]")

    mpp_entitiy.properties = properties
