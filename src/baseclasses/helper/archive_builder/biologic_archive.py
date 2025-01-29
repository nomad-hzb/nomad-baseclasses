import inspect
import os
from datetime import datetime

import numpy as np
from nomad.units import ureg

import baseclasses
from baseclasses.chemical_energy.chronoamperometry import CAProperties
from baseclasses.chemical_energy.chronocoulometry import CCProperties
from baseclasses.chemical_energy.chronopotentiometry import CPProperties
from baseclasses.chemical_energy.cyclicvoltammetry import CVProperties
from baseclasses.chemical_energy.electrochemical_impedance_spectroscopy import (
    EISCycle,
    EISProperties,
)
from baseclasses.chemical_energy.linear_sweep_voltammetry import LSVProperties
from baseclasses.chemical_energy.opencircuitvoltage import OCVProperties
from baseclasses.chemical_energy.potentiostat_measurement import BioLogicProperties
from baseclasses.chemical_energy.voltammetry import (
    VoltammetryCycle,
    VoltammetryCycleWithPlot,
)


def get_biologic_properties(metadata):
    properties = BioLogicProperties()
    properties.comments = metadata.get('comments')
    properties.active_material_mass = metadata.get('active_material_mass')
    properties.at_x = metadata.get('at_x')
    properties.molecular_weight = metadata.get('molecular_weight')
    properties.atomic_weight = metadata.get('atomic_weight')
    properties.acquisition_start = metadata.get('acquisition_start')
    properties.e_transferred = metadata.get('e_transferred')
    properties.electrode_material = metadata.get('electrode_material')
    properties.electrolyte = metadata.get('electrolyte')
    properties.electrode_area = metadata.get('electrode_area')
    properties.reference_electrode = metadata.get('reference_electrode')
    properties.characteristic_mass = metadata.get('characteristic_mass')
    battery_capacity_unit = (
        ureg(metadata.get('battery_capacity_unit'))
        if metadata.get('battery_capacity_unit') is not None
        else ureg('Ah')
    )
    properties.battery_capacity = (
        metadata.get('battery_capacity') * battery_capacity_unit
    )
    properties.analog_in_1 = metadata.get('Analog IN 1')
    properties.analog_in_1_max_V = metadata.get('Analog IN 1 max V')
    properties.analog_in_1_min_V = metadata.get('Analog IN 1 min V')
    properties.analog_in_1_max_x = metadata.get('Analog IN 1 max x')
    properties.analog_in_1_min_x = metadata.get('Analog IN 1 min x')
    properties.analog_in_2 = metadata.get('Analog IN 2')
    properties.analog_in_2_max_V = metadata.get('Analog IN 2 max V')
    properties.analog_in_2_min_V = metadata.get('Analog IN 2 min V')
    properties.analog_in_2_max_x = metadata.get('Analog IN 2 max x')
    properties.analog_in_2_min_x = metadata.get('Analog IN 2 min x')
    return properties


def get_ca_properties(metadata, cc=False):
    properties = CAProperties()
    if cc:
        properties = CCProperties()

    properties.pre_step_potential = metadata.get('Ei')
    properties.pre_step_potential_measured_against = metadata.get('Ei_vs')
    properties.pre_step_delay_time = metadata.get('ti')

    # TODO is initial != pre_step?
    # TODO in biologic files step1 and step2 (always?) do not exist so I removed that

    properties.sample_period = metadata.get('dta')
    return properties


def get_cp_properties(metadata, cc=False):
    properties = CPProperties()

    # TODO in biologic files prestep and step2 (always?) do not exist so I removed that

    current_unit = (
        ureg(metadata.get('Is_unit'))
        if metadata.get('Is_unit') is not None
        else ureg('A')
    )
    properties.step_1_current = metadata.get('Is') * current_unit
    properties.step_1_time = metadata.get('ts')

    properties.lower_limit_potential = metadata.get('E_range_min')
    properties.upper_limit_potential = metadata.get('E_range_max')

    properties.sample_period = metadata.get('dts')
    return properties


def get_cv_properties(metadata):
    properties = CVProperties()

    # TODO for all vs change to enum mode "Eoc" if metadata["VDC"][1] else "Eref"

    properties.initial_potential = metadata.get('Ei')
    properties.initial_potential_measured_against = metadata.get(
        'Ei_vs'
    )  #   yadg gives numbers here. check with mps file if they somehow map to Ref and Eoc in mps file
    properties.limit_potential_1 = metadata.get('E1')
    properties.limit_potential_1_measured_against = metadata.get('E1_vs')
    properties.limit_potential_2 = metadata.get('E2')
    properties.limit_potential_2_measured_against = metadata.get('E2_vs')
    properties.final_potential = metadata.get('Ef')
    properties.final_potential_measured_against = metadata.get('Ef_vs')
    scan_rate_unit = metadata.get('dE/dt_unit')  #   yadg gives numbers here. check
    properties.scan_rate = metadata.get('dE/dt') * ureg(scan_rate_unit)
    properties.step_size = metadata.get('STEPSIZE')  #   TODO calculate this?
    properties.cycles = metadata.get('nc_cycles')
    return properties


def get_eis_properties(metadata):
    properties = EISProperties()

    properties.dc_voltage = metadata['VDC'][0]
    properties.dc_voltage_measured_against = 'Eoc' if metadata['VDC'][1] else 'Eref'
    unit_initial_freq = metadata.get('fi_unit')  # yadg gives numbers here. check
    properties.initial_frequency = metadata.get('fi') * ureg(unit_initial_freq)
    unit_final_freq = metadata.get('ff_unit')  # yadg gives numbers here. check
    properties.final_frequency = metadata.get('ff') * ureg(unit_final_freq)
    properties.points_per_decade = metadata.get('Nd')
    # TODO metadata.get('points') sollte "per decade" bzw. 1 in yadg sein, evtl spielt auch 'spacing' "logarithmic" bzw "1" eine rolle?
    properties.ac_voltage = metadata.get('VAC')  # TODO
    return properties


def get_lsv_properties(metadata):
    properties = LSVProperties()

    properties.initial_potential = metadata.get('Ei')
    properties.initial_potential_measured_against = metadata.get(
        'Ei_vs'
    )  # 4=Ref?, 0=None?, 110,123???, 3 and 50=Eoc??
    properties.final_potential = metadata.get('EL')
    properties.final_potential_measured_against = metadata.get('EL_vs')
    scan_rate_unit = metadata.get('dE/dt_unit')  # yadg gives numbers here. check
    properties.scan_rate = metadata.get('dE/dt') * ureg(scan_rate_unit)
    properties.step_size = metadata.get('STEPSIZE')  # TODO calculate this?
    return properties


def get_ocv_properties(metadata):
    properties = OCVProperties()

    properties.total_time = metadata.get('tR')
    properties.sample_period = metadata.get('dtR')
    properties.stability = metadata.get('STABILITY')  # TODO calculate this?
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


def get_eis_data(data, cycle):
    assert (
        baseclasses.chemical_energy.ElectrochemicalImpedanceSpectroscopy
        in inspect.getmro(type(cycle))
        or isinstance(cycle, EISCycle)
    )

    cycle.time = np.array(data.get('time')) * ureg(
        's'
    )  # TODO test if get instead of None stuff works TODO check unit s
    cycle.frequency = np.array(data.get('freq')) * ureg('Hz')
    cycle.z_real = np.array(data.get('Re(Z)')) * ureg('Ohm')
    cycle.z_imaginary = np.array(data.get('-Im(Z)')) * ureg('Ohm')
    cycle.z_modulus = np.array(data.get('|Z|')) * ureg('Ohm')
    cycle.z_angle = np.array(data.get('Phase(Z)')) * ureg('deg')


def get_voltammetry_data(data, cycle):
    assert isinstance(
        cycle, VoltammetryCycle
    ) or baseclasses.chemical_energy.voltammetry.Voltammetry in inspect.getmro(
        type(cycle)
    )
    time = data.get('time')
    current = data.get('<I>')
    voltage = data.get('Ewe') or data.get('<Ewe>')
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
    cycle.charge = (
        np.array(charge.data) * ureg(charge.attrs.get('units'))
        if charge is not None
        else None
    )
    # TODO check if correct columns are used (Ns, time, time_std_err, control_V, control_V_std_err, Ewe, Ewe_std_err,
    #  < I >, < I > _std_err, dQ, dQ_std_err, (Q - Qo), (Q - Qo)_std_err, I Range,
    #  Q charge or discharge, Q charge or discharge_std_err, half cycle, Phase(Z2), Phase(Z2)_std_err,
    #  P, P_std_err, mode, ox or red, error, control changes, Ns changes, counter inc.)


def get_voltammetry_archive(data, metadata, entry_class, multiple=False):
    if len(data.data_vars) == 0:
        return

    data_grouped_by_cycles = data.ds.groupby('cycle number')
    if len(data_grouped_by_cycles) > 1 or multiple:
        if entry_class.cycles is None or len(entry_class.cycles) == 0:
            entry_class.cycles = []
            for cycle_number, cycle_data in data_grouped_by_cycles:
                cycle = VoltammetryCycleWithPlot()
                get_voltammetry_data(cycle_data.data_vars, cycle)
                entry_class.cycles.append(cycle)

    if len(data_grouped_by_cycles) == 1 and not multiple:
        get_voltammetry_data(data_grouped_by_cycles[1], entry_class)

    get_meta_data(metadata, entry_class)
    entry_class.datetime = datetime.fromtimestamp(
        data.get('time')[0]
    )  # TODO check if really first value of time data is selcted like that
