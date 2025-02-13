import inspect
import os
from datetime import datetime, timedelta

import numpy as np
from nomad.units import ureg

import baseclasses
from baseclasses.chemical_energy.chronoamperometry import CAProperties
from baseclasses.chemical_energy.chronocoulometry import CCProperties
from baseclasses.chemical_energy.chronopotentiometry import CPProperties
from baseclasses.chemical_energy.constantpotential import (
    ConstCProperties,
    ConstVProperties,
)
from baseclasses.chemical_energy.cyclicvoltammetry import CVProperties
from baseclasses.chemical_energy.electrochemical_impedance_spectroscopy import (
    EISCycle,
    EISPropertiesWithData,
)
from baseclasses.chemical_energy.linear_sweep_voltammetry import LSVProperties
from baseclasses.chemical_energy.opencircuitvoltage import OCVProperties
from baseclasses.chemical_energy.potentiostat_measurement import BioLogicSetting
from baseclasses.chemical_energy.voltammetry import (
    VoltammetryCycle,
    VoltammetryCycleWithPlot,
)


def get_nomad_measured_against_enum(biologic_measured_against):
    if biologic_measured_against == ['Ref']:
        return 'Eref'
    elif biologic_measured_against == ['Eoc']:
        return 'Eoc'
    else:
        return None


def get_biologic_properties(metadata):
    settings = BioLogicSetting()
    settings.comments = metadata.get('comments')
    settings.active_material_mass = metadata.get('active_material_mass')
    settings.at_x = metadata.get('at_x')
    settings.molecular_weight = metadata.get('molecular_weight')
    settings.atomic_weight = metadata.get('atomic_weight')
    settings.acquisition_start = metadata.get('acquisition_start')
    settings.e_transferred = metadata.get('e_transferred')
    settings.electrode_material = metadata.get('electrode_material')
    settings.electrolyte = metadata.get('electrolyte')
    settings.sample_area = metadata.get('electrode_area')
    settings.reference_electrode = metadata.get('reference_electrode')
    settings.characteristic_mass = metadata.get('characteristic_mass')
    if (
        metadata.get('battery_capacity_unit') == 0
        or metadata.get('battery_capacity_unit') is None
    ):
        battery_capacity_unit = ureg('A*hour')
    else:
        battery_capacity_unit = ureg(metadata.get('battery_capacity_unit'))
    settings.battery_capacity = metadata.get('battery_capacity') * battery_capacity_unit
    settings.analog_in_1 = metadata.get('Analog IN 1')
    settings.analog_in_1_max_V = metadata.get('Analog IN 1 max V')
    settings.analog_in_1_min_V = metadata.get('Analog IN 1 min V')
    settings.analog_in_1_max_x = metadata.get('Analog IN 1 max x')
    settings.analog_in_1_min_x = metadata.get('Analog IN 1 min x')
    settings.analog_in_2 = metadata.get('Analog IN 2')
    settings.analog_in_2_max_V = metadata.get('Analog IN 2 max V')
    settings.analog_in_2_min_V = metadata.get('Analog IN 2 min V')
    settings.analog_in_2_max_x = metadata.get('Analog IN 2 max x')
    settings.analog_in_2_min_x = metadata.get('Analog IN 2 min x')
    return settings


def get_ca_properties(metadata, cc=False):
    properties = CAProperties()
    if cc:
        properties = CCProperties()

    properties.pre_step_potential = metadata.get('Ei (V)')
    properties.pre_step_potential_measured_against = get_nomad_measured_against_enum(
        metadata.get('Ei (V) vs.')
    )
    properties.pre_step_delay_time = metadata.get('ti (h:m:s)')
    properties.sample_period = metadata.get('dta (s)')
    return properties


def get_const_properties(metadata, constC=False):
    properties = ConstVProperties()
    if constC:
        properties = ConstCProperties()

    properties.total_time = metadata.get('tR (h:m:s)')
    properties.sample_period = metadata.get('dtR (s)')
    properties.lower_limit_potential = metadata.get('E range min (V)')
    properties.upper_limit_potential = metadata.get('E range max (V)')
    properties.cycles = metadata.get('nc cycles')

    if constC:
        current_unit = (
            ureg(metadata.get('unit Is')[0])
            if metadata.get('unit Is') is not None
            else ureg('A')
        )
        properties.step_1_current = metadata.get('Is') * current_unit
        properties.step_1_time = metadata.get('ts (h:m:s)')
    else:
        properties.pre_step_potential = metadata.get('Ei (V)')
        properties.pre_step_potential_measured_against = (
            get_nomad_measured_against_enum(metadata.get('Ei (V) vs.'))
        )
        properties.pre_step_delay_time = metadata.get('ti (h:m:s)')
        properties.sample_period = metadata.get('dta (s)')
    return properties


def get_cp_properties(metadata, cc=False):
    properties = CPProperties()

    current_unit = (
        ureg(metadata.get('unit Is')[0])
        if metadata.get('unit Is') is not None
        else ureg('A')
    )
    properties.step_1_current = metadata.get('Is') * current_unit
    properties.step_1_time = metadata.get('ts (h:m:s)')

    properties.lower_limit_potential = metadata.get('E range min (V)')
    properties.upper_limit_potential = metadata.get('E range max (V)')

    properties.sample_period = metadata.get('dts (s)')
    return properties


def get_cv_properties(metadata):
    properties = CVProperties()

    properties.initial_potential = metadata.get('Ei (V)')
    properties.initial_potential_measured_against = get_nomad_measured_against_enum(
        metadata.get('Ei (V) vs.')
    )
    properties.limit_potential_1 = metadata.get('E1 (V)')
    properties.limit_potential_1_measured_against = get_nomad_measured_against_enum(
        metadata.get('E1 (V) vs.')
    )
    properties.limit_potential_2 = metadata.get('E2 (V)')
    properties.limit_potential_2_measured_against = get_nomad_measured_against_enum(
        metadata.get('E2 (V) vs.')
    )
    properties.final_potential = metadata.get('Ef (V)')
    properties.final_potential_measured_against = get_nomad_measured_against_enum(
        metadata.get('Ef (V) vs.')
    )
    scan_rate_unit = metadata.get('dE/dt unit')
    scan_rate_unit = 'mV/s' if scan_rate_unit == [1] else scan_rate_unit
    properties.scan_rate = metadata.get('dE/dt') * ureg(scan_rate_unit)
    properties.cycles = metadata.get('nc cycles')
    return properties


def get_eis_properties(metadata):
    dc_voltage = metadata.get('E (V)', [])
    unit_initial_freq = metadata.get('unit fi', [])
    unit_final_freq = metadata.get('unit ff', [])
    nd = metadata.get('Nd', [])
    points = metadata.get('Points', [])

    num_cycles = len(metadata.get('nc cycles'))
    property_list = []
    for cycle in range(num_cycles):
        properties = EISPropertiesWithData()
        if dc_voltage:
            properties.dc_voltage = dc_voltage[cycle]
            properties.dc_voltage_measured_against = get_nomad_measured_against_enum(
                metadata.get('E (V) vs.')[cycle]
            )
        if unit_initial_freq:
            properties.initial_frequency = metadata.get('fi')[cycle] * ureg(
                unit_initial_freq[cycle]
            )
        if unit_final_freq:
            properties.final_frequency = metadata.get('ff')[cycle] * ureg(
                unit_final_freq[cycle]
            )
        if nd and points:
            properties.points_per_decade = (
                metadata.get('Nd')[cycle] * metadata.get('Points')[cycle]
            )
        properties.ac_voltage = (
            metadata.get('Va (mV)')[cycle] if metadata.get('Va (mV)', []) else None
        )
        property_list.append(properties)
    return property_list


def get_lsv_properties(metadata):
    properties = LSVProperties()

    properties.initial_potential = metadata.get('Ei (V)')
    properties.initial_potential_measured_against = get_nomad_measured_against_enum(
        metadata.get('Ei (V) vs.')
    )
    properties.final_potential = metadata.get('EL (V)')
    properties.final_potential_measured_against = get_nomad_measured_against_enum(
        metadata.get('EL (V) vs.')
    )
    scan_rate_unit = metadata.get('dE/dt unit')
    scan_rate_unit = 'mV/s' if scan_rate_unit == [1] else scan_rate_unit
    properties.scan_rate = metadata.get('dE/dt') * ureg(scan_rate_unit)
    return properties


def get_ocv_properties(metadata):
    properties = OCVProperties()

    properties.total_time = metadata.get('tR (h:m:s)')
    properties.sample_period = metadata.get('dtR (s)')
    return properties


def get_meta_data(metadata, entry):
    assert (
        baseclasses.chemical_energy.potentiostat_measurement.PotentiostatMeasurement
        in inspect.getmro(type(entry))
    )

    if not entry.name and entry.data_file is not None:
        entry.name = os.path.splitext(entry.data_file)[0]

    if not entry.description:
        entry.description = metadata.get('comments')


def get_eis_data(data, measurement_list):
    cycle_indices = np.array(data.get('Ns', []))
    cycle_start_indices = np.where(np.diff(cycle_indices) != 0)[0] + 1

    # cycle_start_indices does not contain start of first cycle
    if len(cycle_start_indices) + 1 != len(measurement_list):
        return

    time = np.split(data.get('time', []), cycle_start_indices)
    frequency = np.split(data.get('freq', []), cycle_start_indices)
    z_real = np.split(data.get('Re(Z)', []), cycle_start_indices)
    z_imaginary = np.split(data.get('-Im(Z)', []), cycle_start_indices)
    z_modulus = np.split(data.get('|Z|', []), cycle_start_indices)
    z_angle = np.split(data.get('Phase(Z)', []), cycle_start_indices)

    for cycle_idx, measurement in enumerate(measurement_list):
        cycle = EISCycle()
        cycle.time = np.array(time[cycle_idx]) * ureg('s')
        cycle.frequency = np.array(frequency[cycle_idx]) * ureg('Hz')
        cycle.z_real = np.array(z_real[cycle_idx]) * ureg('ohm')
        cycle.z_imaginary = np.array(z_imaginary[cycle_idx]) * ureg('ohm')
        cycle.z_modulus = np.array(z_modulus[cycle_idx]) * ureg('ohm')
        cycle.z_angle = np.array(z_angle[cycle_idx]) * ureg('deg')
        measurement.data = cycle


def get_voltammetry_data(data, cycle):
    assert isinstance(
        cycle, VoltammetryCycle
    ) or baseclasses.chemical_energy.voltammetry.Voltammetry in inspect.getmro(
        type(cycle)
    )
    time = data.get('time')
    current = data.get('<I>')
    voltage = data.get('Ewe') if data.get('Ewe') is not None else data.get('<Ewe>')
    charge = data.get('(Q-Qo)')

    cycle.time = (
        np.array(time.data) * ureg(time.attrs.get('units'))
        if time is not None
        else None
    )
    cycle.current = (
        np.array(current.data) * ureg(current.attrs.get('units'))
        if current is not None
        else None
    )
    cycle.voltage = (
        np.array(voltage.data) * ureg(voltage.attrs.get('units'))
        if voltage is not None
        else None
    )
    ureg.define('h = hour')
    cycle.charge = (
        np.array(charge.data) * ureg(charge.attrs.get('units'))
        if charge is not None
        else None
    )


def get_start_time(ole_timestamp, start_time_offset):
    ole_epoch = datetime(1899, 12, 30)
    return (
        ole_epoch + timedelta(days=ole_timestamp) + timedelta(seconds=start_time_offset)
    )


def get_voltammetry_archive(data, metadata, entry_class, multiple=False):
    if len(data.data_vars) == 0:
        return

    setting_metadata = metadata.get('settings', {})
    get_meta_data(setting_metadata, entry_class)

    ole_timestamp = metadata.get('log', {}).get('ole_timestamp', 0)
    start_time_offset = data.get('time')[0].item()
    entry_class.datetime = get_start_time(ole_timestamp, start_time_offset)

    if data.ds.get('cycle number') is None and not multiple:
        get_voltammetry_data(data, entry_class)
        return

    data_grouped_by_cycles = data.ds.groupby('cycle number')
    if entry_class.cycles is None or len(entry_class.cycles) == 0:
        entry_class.cycles = []
        for cycle_number, cycle_data in data_grouped_by_cycles:
            cycle = VoltammetryCycleWithPlot()
            get_voltammetry_data(cycle_data.data_vars, cycle)
            entry_class.cycles.append(cycle)
