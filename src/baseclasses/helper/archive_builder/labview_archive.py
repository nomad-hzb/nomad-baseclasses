import inspect
from datetime import datetime

import numpy as np
from nomad.units import ureg

import baseclasses
from baseclasses import PubChemPureSubstanceSectionCustom
from baseclasses.chemical_energy.electrolyser_performance import (
    ElectrolyserProperties,
    NESDElectrode,
)


def get_pint_from_string(magnitude_string, unit):
    if magnitude_string is None:
        return None
    try:
        magnitude = np.float64(magnitude_string)
    except Exception:
        print(f'Cannot convert {magnitude_string} to pint magnitude.')
        return None
    return magnitude * ureg(unit)


def get_electrode(metadata, electrode_type):
    electrode = NESDElectrode()
    electrode.electrolyte = metadata.get(f'Electrolyte_{electrode_type}')
    electrode.catalyst = metadata.get(f'Catalyst_{electrode_type}')
    electrode.gasket_material = PubChemPureSubstanceSectionCustom(
        name=metadata.get(f'Gasket_Material_{electrode_type}'), load_data=False
    )
    gasket_thickness_cathode_magnitude = metadata.get(
        f'Gasket_Thickness_mm_{electrode_type}'
    )
    electrode.gasket_thickness = get_pint_from_string(
        gasket_thickness_cathode_magnitude, 'mm'
    )
    area_cathode_magnitude = metadata.get(f'Electrode_Area_sqmm_{electrode_type}')
    electrode.electrode_area = get_pint_from_string(area_cathode_magnitude, 'mm ** 2')
    electrode.electrode_material = PubChemPureSubstanceSectionCustom(
        name=metadata.get(f'Electrode_Material_{electrode_type}'), load_data=False
    )
    return electrode


def get_electrolyser_properties(metadata, entry_object):
    assert (
        baseclasses.chemical_energy.electrolyser_performance.ElectrolyserProperties
        in inspect.getmro(type(entry_object))
    )
    torque_magnitude = metadata.get('Torque_Nm')
    entry_object.torque = get_pint_from_string(torque_magnitude, 'newton * meter')
    entry_object.cell_name = metadata.get('Cell_Name')
    entry_object.test_rigg = metadata.get('Test_Rig')
    entry_object.membrane = metadata.get('Membrane')

    entry_object.anode = get_electrode(metadata, 'Anode')
    entry_object.cathode = get_electrode(metadata, 'Cathode')

    return entry_object


def get_tdms_archive(data, entry_object):
    entry_object.time = (
        np.array(data['READ_0_Time']) * ureg('s')
        if 'READ_0_Time' in data.columns
        else None
    )
    entry_object.h2_flow = (
        np.array(data['READ_H2_Flow']) * ureg('ml/minute')
        if 'READ_H2_Flow' in data.columns
        else None
    )
    entry_object.o2_flow = (
        np.array(data['READ_O2_Flow']) * ureg('ml/minute')
        if 'READ_O2_Flow' in data.columns
        else None
    )
    entry_object.anode_in = (
        np.array(data['READ_RTD0_A-in']) * ureg('°C')
        if 'READ_RTD0_A-in' in data.columns
        else None
    )
    entry_object.cathode_in = (
        np.array(data['READ_RTD1_C-in']) * ureg('°C')
        if 'READ_RTD1_C-in' in data.columns
        else None
    )
    entry_object.anode_out = (
        np.array(data['READ_RTD2_A-out']) * ureg('°C')
        if 'READ_RTD2_A-out' in data.columns
        else None
    )
    entry_object.cathode_out = (
        np.array(data['READ_RTD3_C-out']) * ureg('°C')
        if 'READ_RTD3_C-out' in data.columns
        else None
    )
    entry_object.ambient = (
        np.array(data['READ_RTD4_amb']) * ureg('°C')
        if 'READ_RTD4_amb' in data.columns
        else None
    )
    entry_object.electrolyser_cell_anode = (
        np.array(data['READ_RTD5_EC-A']) * ureg('°C')
        if 'READ_RTD5_EC-A' in data.columns
        else None
    )
    entry_object.electrolyser_cell_cathode = (
        np.array(data['READ_RTD6_EC-C']) * ureg('°C')
        if 'READ_RTD6_EC-C' in data.columns
        else None
    )
    timestamp_array = (
        np.array(data['READ_Timestamp']) if 'READ_Timestamp' in data.columns else None
    )
    labview_to_unix_offset = (
        datetime(1970, 1, 1) - datetime(1904, 1, 1)
    ).total_seconds()
    entry_object.timestamp = [
        datetime.fromtimestamp(timestamp - labview_to_unix_offset)
        for timestamp in timestamp_array
    ]
