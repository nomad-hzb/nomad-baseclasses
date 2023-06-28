import pandas as pd
import os
from datetime import datetime


def get_data_of_uvvis_csv_file(filename, start, end):
    return pd.read_csv(
        filename,
        delimiter="\t",
        on_bad_lines='skip',
        header=None,
        skiprows=start + 1,
        nrows=end - start - 1)


def get_uvvis_measurement_csv(file_obj):
    sections = dict()
    for index, line in enumerate(file_obj.readlines()):
        if line.startswith("["):
            sections.update({line[1:-2]: index})
    metadata = get_data_of_uvvis_csv_file(
        file_obj.name, sections["SpectrumHeader"], sections["Data"])
    data = get_data_of_uvvis_csv_file(
        file_obj.name, sections["Data"], sections["EndOfFile"])
    datetime_str = f"{metadata[metadata[0] == '#Date'][1].iloc[0]}_{metadata[metadata[0] == '#GMTTime'][1].iloc[0]}"
    datetime_object = datetime.strptime(
        datetime_str, '%Y%m%d_%H%M%S%f')
    return data, datetime_object


def get_uvvis_measurement_txt(file_obj):
    data_file = os.path.basename(file_obj.name)
    data = pd.read_csv(
        file_obj.name, delimiter=';', header=None)
    datetime_str = data_file.split(".")[0]
    datetime_object = datetime.strptime(
        datetime_str, '%Y%m%d_%H_%M_%S_%f')
    return data, datetime_object
