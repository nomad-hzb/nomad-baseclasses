
import inspect
from datetime import datetime


import numpy as np
import os

from nomad.units import ureg
import baseclasses
from baseclasses.chemical_energy.chronoamperometry import CAPropertiesWithData, CAProperties
from baseclasses.chemical_energy.chronocoulometry import CCProperties
from baseclasses.chemical_energy.cyclicvoltammetry import CVProperties
from baseclasses.chemical_energy.opencircuitvoltage import OCVProperties
from baseclasses.chemical_energy.electorchemical_impedance_spectroscopy import EISProperties, EISPropertiesWithData, EISCycle
from baseclasses.chemical_energy.voltammetry import VoltammetryCycle


def get_eis_properties(metadata, properties):
    assert isinstance(properties, EISProperties)

    properties.dc_voltage = metadata["VDC"][0]
    properties.dc_voltage_measured_against = "Eoc" if metadata["VDC"][1] else "Eref"
    properties.initial_frequency = metadata.get("FREQINIT")
    properties.final_frequency = metadata.get("FREQFINAL")
    properties.points_per_decade = metadata.get("PTSPERDEC")
    properties.ac_voltage = metadata.get("VAC")
    properties.sample_area = metadata.get("AREA")


def get_ocv_properties(metadata, properties):
    assert isinstance(properties, OCVProperties)

    properties.total_time = metadata.get("TIMEOUT")
    properties.sample_period = metadata.get("SAMPLETIME")
    properties.stability = metadata.get("STABILITY")
    properties.sample_area = metadata.get("AREA")


def get_cv_properties(metadata, properties):
    assert isinstance(properties, CVProperties)

    properties.initial_potential = metadata["VINIT"][0]
    properties.initial_potential_measured_against = "Eoc" if metadata["VINIT"][1] else "Eref"
    properties.limit_potential_1 = metadata["VLIMIT1"][0]
    properties.limit_potential_1_measured_against = "Eoc" if metadata["VLIMIT1"][1] else "Eref"
    properties.limit_potential_2 = metadata["VLIMIT2"][0]
    properties.limit_potential_2_measured_against = "Eoc" if metadata["VLIMIT2"][1] else "Eref"
    properties.final_potential = metadata["VFINAL"][0]
    properties.final_potential_measured_against = "Eoc" if metadata["VFINAL"][1] else "Eref"
    properties.scan_rate = metadata.get("SCANRATE")
    properties.step_size = metadata.get("STEPSIZE")
    properties.cycles = metadata.get("CYCLES")
    properties.sample_area = metadata.get("AREA")


def get_ca_properties(metadata, properties):
    assert isinstance(properties, CAPropertiesWithData) or isinstance(
        properties, CAProperties) or isinstance(properties, CCProperties)

    properties.pre_step_potential = metadata["VPRESTEP"][0]
    properties.pre_step_potential_measured_against = "Eoc" if metadata[
        "VPRESTEP"][1] else "Eref"
    properties.pre_step_delay_time = metadata.get("TPRESTEP")
    properties.step_1_potential = metadata["VSTEP1"][0]
    properties.step_1_potential_measured_against = "Eoc" if metadata["VSTEP1"][1] else "Eref"
    properties.step_1_time = metadata.get("TSTEP1")
    properties.step_2_potential = metadata["VSTEP2"][0]
    properties.step_2_potential_measured_against = "Eoc" if metadata["VSTEP2"][1] else "Eref"
    properties.step_2_time = metadata.get("TSTEP2")
    properties.sample_period = metadata.get("SAMPLETIME")
    properties.sample_area = metadata.get("AREA")


def get_cc_properties(metadata, properties):
    assert isinstance(properties, CCProperties)

    get_ca_properties(metadata, properties)
    properties.charge_limit = metadata["QLIMIT"][0]


def get_voltammetry_data(data, cycle):
    assert isinstance(cycle, VoltammetryCycle) or \
        baseclasses.chemical_energy.voltammetry.Voltammetry \
        in inspect.getmro(type(cycle))

    cycle.time = np.array(
        data["T"])
    cycle.current = np.array(
        data["Im"]) * ureg('A') if "Im" in data.columns else None
    cycle.voltage = np.array(
        data["Vf"]) if "Vf" in data.columns else None
    cycle.charge = np.array(
        data["Q"]) * ureg('C') if "Q" in data.columns else None


def get_eis_data(data, cycle):
    assert baseclasses.chemical_energy.ElectrochemicalImpedanceSpectroscopy \
        in inspect.getmro(type(cycle)) or isinstance(cycle, EISCycle)

    cycle.time = np.array(data["Time"])
    cycle.frequency = np.array(data["Freq"])
    cycle.z_real = np.array(data["Zreal"])
    cycle.z_imaginary = (-1.0) * np.array(data["Zimag"])
    cycle.z_modulus = np.array(data["Zmod"])
    cycle.z_angle = np.array(data["Zphz"])


def get_meta_datetime(metadata, entry):
    datetime_str = f"{metadata['DATE']} {metadata['TIME']}"
    try:
        datetime_object = datetime.strptime(
            datetime_str, '%d/%m/%Y %H:%M:%S')
    except:
        datetime_object = datetime.strptime(
            datetime_str, '%d.%m.%Y %H:%M:%S')
    entry.datetime = datetime_object.strftime(
        "%Y-%m-%d %H:%M:%S.%f")


def get_meta_data(metadata, entry):
    assert baseclasses.chemical_energy.potentiostat_measurement.PotentiostatMeasurement \
        in inspect.getmro(type(entry))

    if entry.name is None:
        entry.name = metadata.get("TITLE")

    if not entry.name and entry.data_file is not None:
        entry.name = os.path.splitext(entry.data_file)[0]

    get_meta_datetime(metadata, entry)

    if entry.description is None:
        entry.description = ''
    entry.description = f"{entry.description} \n{metadata['NOTES']}" \
        if metadata.get('NOTES') not in entry.description else entry.description

    entry.station = metadata.get('PSTAT')


def get_cam_properties_data(metadata, data, mainfile, properties):
    assert isinstance(properties, CAPropertiesWithData)

    curve_data = VoltammetryCycle()
    get_voltammetry_data(data, curve_data)
    get_ca_properties(metadata, properties)
    get_meta_datetime(metadata, properties)
    properties.data_file = mainfile
    properties.data = curve_data


def get_eis_properties_data(metadata, data, mainfile, properties):
    assert isinstance(properties, EISPropertiesWithData)

    curve_data = EISCycle()
    get_eis_data(data, curve_data)
    get_eis_properties(metadata, properties)
    get_meta_datetime(metadata, properties)
    properties.data_file = mainfile
    properties.data = curve_data
