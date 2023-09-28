# from xarray import Dataset
# from scipy.signal import savgol_filter
from scipy.interpolate import interp1d
import numpy as np
import pandas as pd
import os
from datetime import datetime
from typing import Dict, List, Any, Tuple


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


# Import from UV-Vis mapper in the GloveBox of the Unold-Lab at HZB
# Version 2.0
# by Pascal Becker, Hampus Näsström


ag_calibration = {
    "wavelength_nm": [300.0, 310.0, 320.0, 330.0, 340.0, 350.0, 360.0, 370.0, 380.0, 390.0, 400.0, 410.0, 420.0, 430.0,
                      440.0, 450.0, 460.0, 470.0, 480.0, 490.0, 500.0, 510.0, 520.0, 530.0, 540.0, 550.0, 560.0, 570.0,
                      580.0, 590.0, 600.0, 610.0, 620.0, 630.0, 640.0, 650.0, 660.0, 670.0, 680.0, 690.0, 700.0, 710.0,
                      720.0, 730.0, 740.0, 750.0, 760.0, 770.0, 780.0, 790.0, 800.0, 810.0, 820.0, 830.0, 840.0, 850.0,
                      860.0, 870.0, 880.0, 890.0, 900.0, 910.0, 920.0, 930.0, 940.0, 950.0, 960.0, 970.0, 980.0, 990.0,
                      1000.0, 1010.0, 1020.0, 1030.0, 1040.0, 1050.0, 1060.0, 1070.0, 1080.0, 1090.0, 1100.0, 1110.0,
                      1120.0, 1130.0, 1140.0, 1150.0, 1160.0, 1170.0, 1180.0, 1190.0, 1200.0, 1210.0, 1220.0, 1230.0,
                      1240.0, 1250.0, 1260.0, 1270.0, 1280.0, 1290.0, 1300.0, 1310.0, 1320.0, 1330.0, 1340.0, 1350.0,
                      1360.0, 1370.0, 1380.0, 1390.0, 1400.0, 1410.0, 1420.0, 1430.0, 1440.0, 1450.0, 1460.0, 1470.0,
                      1480.0, 1490.0, 1500.0, 1510.0, 1520.0, 1530.0, 1540.0, 1550.0, 1560.0, 1570.0, 1580.0, 1590.0,
                      1600.0, 1610.0, 1620.0, 1630.0, 1640.0, 1650.0, 1660.0, 1670.0, 1680.0, 1690.0, 1700.0, 1710.0,
                      1720.0, 1730.0, 1740.0, 1750.0, 1760.0, 1770.0, 1780.0, 1790.0, 1800.0, 1810.0, 1820.0, 1830.0,
                      1840.0, 1850.0, 1860.0, 1870.0, 1880.0, 1890.0, 1900.0, 1910.0, 1920.0, 1930.0, 1940.0, 1950.0,
                      1960.0, 1970.0, 1980.0, 1990.0],
    "reflectance": [0.1495514, 0.16728590000000002, 0.12000090000000001, 0.1140352, 0.6119911, 0.82498, 0.8847677,
                    0.8972140000000001, 0.8979546, 0.8984245, 0.9097469, 0.9326443000000001, 0.9558847, 0.972415,
                    0.982024, 0.9876272, 0.9920426000000001, 0.9954109, 0.9967304, 0.9932731, 0.9894966, 0.99185,
                    0.9880747, 0.988199, 0.9908871000000001, 0.9940575, 0.9897537, 0.9889613, 0.9881082999999999,
                    0.9872285, 0.9863379000000001, 0.9892773, 0.9928222, 0.9931481, 0.9914327000000001,
                    0.9908437000000001, 0.9869131, 0.9829128, 0.9811596, 0.9838011000000001, 0.9823487000000001,
                    0.979456, 0.9806511000000001, 0.9802679000000001, 0.9870107, 0.9821165000000001, 0.9816482999999999,
                    0.9823112, 0.9821368, 0.986507, 0.9678582, 0.9678127000000001, 0.9703261999999999, 0.9690085,
                    0.9696701000000001, 0.9675521, 0.9684139, 0.9639724, 0.9569437000000001, 0.9670565999999999,
                    0.967152, 0.9673345000000001, 0.967383, 0.9674643, 0.9677466, 0.9679116999999999, 0.9682785,
                    0.9686901, 0.9690142, 0.969399, 0.9695703000000001, 0.9697849, 0.9700432000000001, 0.9703826,
                    0.9706372000000001, 0.9709087, 0.9714452, 0.9718706, 0.9719876, 0.9721751000000001, 0.9724537,
                    0.9727807, 0.9731379, 0.9734799, 0.9737106, 0.9740802, 0.9745269000000001, 0.9749938, 0.9754668,
                    0.9756252000000001, 0.9757646, 0.9761907, 0.9762917000000001, 0.9765738, 0.9766889000000001,
                    0.9769103, 0.9771169999999999, 0.9773535, 0.9779379, 0.9783181999999999, 0.9783501, 0.9784039,
                    0.9787714, 0.9789696000000001, 0.9790606, 0.9791632, 0.9793227000000001, 0.9794312, 0.9794511,
                    0.9800407, 0.9802339999999999, 0.980472, 0.9806479, 0.9806944000000001, 0.9806107000000001,
                    0.9810411000000001, 0.9813683000000001, 0.9813016000000001, 0.9813973, 0.981823, 0.9818643,
                    0.9817027, 0.981707, 0.9816414000000001, 0.9815759000000001, 0.9817832, 0.9820471000000001,
                    0.9821143, 0.9820838000000001, 0.9822246, 0.98244, 0.9826904999999999, 0.9828986999999999,
                    0.9831618000000001, 0.9831972000000001, 0.9834575, 0.9838116, 0.9838501, 0.9838288000000001,
                    0.9838245000000001, 0.9839669999999999, 0.9839668, 0.9840715, 0.9843636, 0.9843662000000001,
                    0.9844223, 0.984387, 0.9844108, 0.9841678, 0.9841755999999999, 0.9839527, 0.9838171, 0.9838179,
                    0.9835715, 0.9835516, 0.9841274, 0.9843205, 0.9845942, 0.9849114, 0.9852257000000001, 0.9855027,
                    0.9855063000000001, 0.9857393999999999, 0.9855528, 0.9853926000000001, 0.9852763,
                    0.9851662000000001, 0.9852156, 0.985289, 0.9856778]}

ag_interp = interp1d(ag_calibration["wavelength_nm"], ag_calibration["reflectance"])

x_offset = 0
y_offset = 0


def _read_file_uvvis(file_path: str) -> Tuple[dict, pd.DataFrame]:
    with open(file_path, 'r+') as file_handle:
        header = {}
        line = file_handle.readline()
        while line.startswith("#"):
            key_value = line[2:-1].split(": ")
            header[key_value[0]] = key_value[1]
            line = file_handle.readline()
        wavelengths = np.array(line[:-1].split('\t')[1:])
        df = pd.read_csv(file_handle, names=wavelengths, index_col=0, delimiter='\t')
    return header, df.dropna(axis=1)


def read_uvvis(file_paths, spec_key, reference_key, prefix):
    ref_interp = interp1d([0, 2000], [1, 1])
    # Read MeasurementFile
    spectrums = None
    reference = None
    for file_path in file_paths:
        if file_path.endswith(spec_key):
            if spectrums is not None:
                raise
            spectrums = _read_file_uvvis(file_path)
        elif file_path.endswith(reference_key):
            if reference is not None:
                raise
            reference = _read_file_uvvis(file_path)
    if spectrums is None:
        raise
    elif reference is None:
        raise
    wavelength = np.array(reference[1].columns.values, dtype=float)  # Array to hold the wavelengths

    x = []
    y = []  # Lists to hold the measurement positions
    # the index column has a format of "X=3.9;Y=4.0". x and y will be extracted for each line
    for index in spectrums[1].index:
        xy = index.split(';')
        x.append(np.float64(xy[0].split('mm')[0]) + x_offset)
        y.append(np.float64(xy[1].split('mm')[0]) + y_offset)
    x = np.array(x)
    y = np.array(y)  # convert into a numpy array to prepare for usage in DataArray
    # The measurement is conducted by keeping y const and moving x step by step along the sample.
    # Then y moves one step and x starts from the beginning. All these values will be stored in x and y.
    # For the dims of the DataArray we only want the x and y positions once.
    ny = y.argmax() + 1
    nx = x.shape[0] // ny  # number of x and y-positions
    y_pos = y[0:ny]  # x-positions are the first nx values in x
    x_pos = np.array([x[ny * idx] for idx in range(nx)])  # y-positions are every nx-th value in y

    spec_data = np.zeros((nx, ny, wavelength.shape[0]))
    for idx in range(spectrums[1].shape[0]):
        spec_data[idx % nx, idx // nx, :] = spectrums[1].values[idx, :]

    wave_roi = np.where(wavelength > 420)[0][:-6]
    reflection_reduced = spec_data[:, :, wave_roi]
    reflectance = (
        (reflection_reduced - reference[1].loc[f'{prefix}_dark_ref'].values[wave_roi]) /
        ((reference[1].loc[f'{prefix}_bright_ref'].values[wave_roi] - reference[1].loc[f'{prefix}_dark_ref'].values[wave_roi]) /
         ref_interp(wavelength[wave_roi]))
    )

    return spec_data, wavelength, reflectance, wave_roi, x_pos, y_pos, spectrums[0]
