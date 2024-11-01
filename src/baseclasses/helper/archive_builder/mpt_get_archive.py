import inspect
from datetime import datetime

import numpy as np
from nomad.units import ureg

import baseclasses
from baseclasses.chemical_energy.cyclicvoltammetry import CVProperties
from baseclasses.chemical_energy.electorchemical_impedance_spectroscopy import (
    EISCycle,
    EISProperties,
)
from baseclasses.chemical_energy.opencircuitvoltage import OCVProperties
from baseclasses.chemical_energy.voltammetry import VoltammetryCycleWithPlot


def get_voltammetry_data(data, cycle_class):
    if data.index.name is not None and 'curve' in data.index.name:
        if cycle_class.cycles is None or len(cycle_class.cycles) == 0:
            c = 0
            cycle_class.cycles = []
            while c in data.index:
                curve = data.loc[[c]]
                cycle = VoltammetryCycleWithPlot()
                cycle.time = np.array(curve['time/s'])
                cycle.current = (
                    np.array(curve['<I>/mA']) if '<I>/mA' in curve.columns else None
                )
                cycle.voltage = (
                    np.array(curve['Ewe/V'])
                    if 'Ewe/V' in curve.columns
                    else np.array(curve['<Ewe>/V'])
                )
                cycle.control = (
                    np.array(curve['control/V'])
                    if 'control/V' in curve.columns
                    else None
                )
                cycle_class.cycles.append(cycle)
                c += 1
    else:
        cycle_class.time = np.array(data['time/s'])
        cycle_class.current = (
            np.array(data['<I>/mA']) if '<I>/mA' in data.columns else None
        )
        cycle_class.voltage = (
            np.array(data['Ewe/V'])
            if 'Ewe/V' in data.columns
            else np.array(data['<Ewe>/V'])
        )
        cycle_class.control = (
            np.array(data['control/V'])
            if 'control/V' in data.columns
            else (np.array(data['<Ece>/V']) if '<Ece>/V' in data.columns else None)
        )


def get_cv_properties(metadata):
    properties = CVProperties()

    properties.initial_potential = metadata.get('Ei (V)')
    properties.initial_potential_measured_against = (
        'Eoc' if metadata.get('Ei (V) vs.') == 'Eoc' else 'Eref'
    )
    properties.limit_potential_1 = metadata.get('E1 (V)')
    properties.limit_potential_1_measured_against = (
        'Eoc' if metadata.get('E1 (V) vs.') == 'Eoc' else 'Eref'
    )
    properties.limit_potential_2 = metadata.get('E2 (V)')
    properties.limit_potential_2_measured_against = (
        'Eoc' if metadata.get('E2 (V) vs.') == 'Eoc' else 'Eref'
    )
    properties.final_potential = metadata.get('Ef (V)')
    properties.final_potential_measured_against = (
        'Eoc' if metadata.get('Ef (V) vs.') == 'Eoc' else 'Eref'
    )
    properties.scan_rate = metadata.get('dE/dt')
    properties.cycles = metadata.get('nc cycles')

    return properties


def get_ocv_properties(metadata):
    properties = OCVProperties()

    # properties.total_time = metadata["TIMEOUT"]
    # properties.sample_period = metadata["SAMPLETIME"]
    # properties.stability = metadata["STABILITY"]
    # properties.sample_area = metadata.get("Electrode surface area")
    return properties


def get_eis_properties(metadata, withdata=False):
    properties = EISProperties()

    properties.dc_voltage = metadata['E (V)']
    properties.dc_voltage_measured_against = (
        'Eoc' if metadata.get('E (V) vs.') == 'Eoc' else 'Eref'
    )
    properties.initial_frequency = metadata['fi'] * ureg(metadata['unit fi'])
    properties.final_frequency = metadata['ff'] * ureg(metadata['unit ff'])
    properties.points_per_decade = metadata['Nd']
    properties.ac_voltage = metadata['Va (mV)']
    # properties.sample_area = metadata["AREA"]
    return properties


def get_eis_data(data, cycle):
    assert (
        baseclasses.chemical_energy.ElectrochemicalImpedanceSpectroscopy
        in inspect.getmro(type(cycle))
        or isinstance(cycle, EISCycle)
    )

    cycle.time = np.array(data['time/s'])
    cycle.frequency = np.array(data['freq/Hz'])
    cycle.z_real = np.array(data['Re(Z)/Ohm'])
    cycle.z_imaginary = np.array(data['-Im(Z)/Ohm'])
    cycle.z_modulus = np.array(data['|Z|/Ohm'])
    cycle.z_angle = np.array(data['Phase(Z)/deg'])


def get_meta_datetime(metadata, entry):
    datetime_str = metadata.get('Acquisition started on')
    datetime_object = datetime.strptime(datetime_str, '%m/%d/%Y %H:%M:%S.%f')
    entry.datetime = datetime_object.strftime('%Y-%m-%d %H:%M:%S.%f')


def get_meta_data(metadata, entry):
    assert (
        baseclasses.chemical_energy.potentiostat_measurement.PotentiostatMeasurement
        in inspect.getmro(type(entry))
    )

    get_meta_datetime(metadata, entry)

    if entry.description is None:
        entry.description = ''
    # entry.description = f"{entry.description} \n{metadata['NOTES']}" \
    #     if metadata['NOTES'] not in entry.description else entry.description


# def get_eis_properties_data(metadata, data, mainfile, properties):
#     assert isinstance(properties, EISPropertiesWithData)

#     curve_data = EISCycle()
#     get_eis_data(data, curve_data)
#     get_eis_properties(metadata, properties)
#     get_meta_datetime(metadata, properties)
#     properties.data_file = mainfile
#     properties.data = curve_data
