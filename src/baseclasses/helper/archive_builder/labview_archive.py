from datetime import datetime

import numpy as np
from nomad.units import ureg

from baseclasses import PubChemPureSubstanceSectionCustom
from baseclasses.chemical_energy.electrolyser_performance import (
    ElectrolyserProperties,
    NESDElectrode,
)


def get_pint_from_string(magnitude_string, unit):
    try:
        magnitude = np.float64(magnitude_string)
    except:
        print(f'Cannot convert {magnitude_string} to pint magnitude.')
        magnitude = np.float64(0)
    return magnitude * ureg(unit)


def get_electrolyser_properties(metadata):
    properties = ElectrolyserProperties()
    torque_magnitude = metadata.get('Torque_Nm')
    properties.torque = get_pint_from_string(torque_magnitude, 'newton * meter')
    properties.cell_name = metadata.get('Cell_Name')
    properties.test_rig = metadata.get('Test_Rig')
    properties.membrane = metadata.get('Membrane')

    anode = NESDElectrode()
    anode.electrolyte = metadata.get('Electrolyte_Anode')
    anode.catalyst = metadata.get('Catalyst_Anode')
    area_anode_magnitude = metadata.get('Electrode_Area_sqmm_Anode')
    anode.electrode_area = get_pint_from_string(area_anode_magnitude, 'mm ** 2')
    anode.gasket_material = PubChemPureSubstanceSectionCustom(
        name=metadata.get('Gasket_Material_Anode'), load_data=False
    )
    gasket_thickness_anode_magnitude = metadata.get('Gasket_Thickness_mm_Anode')
    anode.gasket_thickness = get_pint_from_string(
        gasket_thickness_anode_magnitude, 'mm'
    )
    anode.electrode_material = PubChemPureSubstanceSectionCustom(
        name=metadata.get('Electrode_Material_Anode'), load_data=False
    )

    cathode = NESDElectrode()
    cathode.electrolyte = metadata.get('Electrolyte_Cathode')
    cathode.catalyst = metadata.get('Catalyst_Cathode')
    cathode.gasket_material = PubChemPureSubstanceSectionCustom(
        name=metadata.get('Gasket_Material_Cathode'), load_data=False
    )
    gasket_thickness_cathode_magnitude = metadata.get('Gasket_Thickness_mm_Cathode')
    cathode.gasket_thickness = get_pint_from_string(
        gasket_thickness_cathode_magnitude, 'mm'
    )
    area_cathode_magnitude = metadata.get('Electrode_Area_sqmm_Cathode')
    cathode.electrode_area = get_pint_from_string(area_cathode_magnitude, 'mm ** 2')
    cathode.electrode_material = PubChemPureSubstanceSectionCustom(
        name=metadata.get('Electrode_Material_Cathode'), load_data=False
    )

    properties.anode = anode
    properties.cathode = cathode
    return properties


def get_tdms_archive(data, entry_class):
    # TODO units like mln/minute (is mln normliter? then mln/minute might be slpm or standard liter per minute?)
    entry_class.time = (
        np.array(data['READ_0_Time']) * ureg('s')
        if 'READ_0_Time' in data.columns
        else None
    )
    entry_class.h2_flow = (
        np.array(data['READ_H2_Flow']) * ureg('ml/minute')
        if 'READ_H2_Flow' in data.columns
        else None
    )
    entry_class.o2_flow = (
        np.array(data['READ_O2_Flow']) * ureg('ml/minute')
        if 'READ_O2_Flow' in data.columns
        else None
    )
    entry_class.anode_in = (
        np.array(data['READ_RTD0_A-in']) * ureg('°C')
        if 'READ_RTD0_A-in' in data.columns
        else None
    )
    entry_class.cathode_in = (
        np.array(data['READ_RTD1_C-in']) * ureg('°C')
        if 'READ_RTD1_C-in' in data.columns
        else None
    )
    entry_class.anode_out = (
        np.array(data['READ_RTD2_A-out']) * ureg('°C')
        if 'READ_RTD2_A-out' in data.columns
        else None
    )
    entry_class.cathode_out = (
        np.array(data['READ_RTD3_C-out']) * ureg('°C')
        if 'READ_RTD3_C-out' in data.columns
        else None
    )
    entry_class.ambient = (
        np.array(data['READ_RTD4_amb']) * ureg('°C')
        if 'READ_RTD4_amb' in data.columns
        else None
    )
    entry_class.electrolyser_cell_anode = (
        np.array(data['READ_RTD5_EC-A']) * ureg('°C')
        if 'READ_RTD5_EC-A' in data.columns
        else None
    )
    entry_class.electrolyser_cell_cathode = (
        np.array(data['READ_RTD6_EC-C']) * ureg('°C')
        if 'READ_RTD6_EC-C' in data.columns
        else None
    )
    timestamp_array = (
        np.array(data['READ_Timestamp']) if 'READ_Timestamp' in data.columns else None
    )
    entry_class.timestamp = [
        datetime.fromtimestamp(timestamp) for timestamp in timestamp_array
    ]
