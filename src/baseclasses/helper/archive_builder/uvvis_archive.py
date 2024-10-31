import numpy as np


def _get_uvvis_data_entry(data_entry, data, datetime_object, data_file):
    if datetime_object is not None:
        data_entry.datetime = datetime_object.strftime(
            "%Y-%m-%d %H:%M:%S.%f")
    data_entry.name = data_file
    data_entry.wavelength = np.array(data[0])
    data_entry.intensity = np.array(data[1])
    return data_entry


def get_uvvis_archive(data, datetime_object, data_file):
     from baseclasses.solar_energy import UVvisData
     data_entry = UVvisData()
     return _get_uvvis_data_entry(data_entry, data, datetime_object, data_file)


def get_uvvis_concentration_archive(data, datetime_object, data_file):
    from baseclasses.chemical_energy import UVvisDataConcentration
    if "nh3" in data_file.lower():
        data_entry = UVvisDataConcentration(chemical_composition_or_formulas='NH3')
    else:
        data_entry = UVvisDataConcentration()
    return _get_uvvis_data_entry(data_entry, data, datetime_object, data_file)
