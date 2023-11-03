
import inspect
from datetime import datetime


import numpy as np
import os

from nomad.units import ureg
import baseclasses
from baseclasses.chemical_energy.chronoamperometry import CAProperties
from baseclasses.chemical_energy.chronopotentiometry import CPProperties
from baseclasses.chemical_energy.chronocoulometry import CCProperties
from baseclasses.chemical_energy.cyclicvoltammetry import CVProperties
from baseclasses.chemical_energy.opencircuitvoltage import OCVProperties
from baseclasses.chemical_energy.electorchemical_impedance_spectroscopy import EISProperties, EISCycle
from baseclasses.chemical_energy.voltammetry import VoltammetryCycle, VoltammetryCycleWithPlot
from baseclasses.atmosphere import Atmosphere


def get_eis_properties(metadata):
    properties = EISProperties()

    properties.dc_voltage = metadata["VDC"][0]
    properties.dc_voltage_measured_against = "Eoc" if metadata["VDC"][1] else "Eref"
    properties.initial_frequency = metadata.get("FREQINIT")
    properties.final_frequency = metadata.get("FREQFINAL")
    properties.points_per_decade = metadata.get("PTSPERDEC")
    properties.ac_voltage = metadata.get("VAC")
    properties.sample_area = metadata.get("AREA")
    return properties


def get_ocv_properties(metadata):
    properties = OCVProperties()

    properties.total_time = metadata.get("TIMEOUT")
    properties.sample_period = metadata.get("SAMPLETIME")
    properties.stability = metadata.get("STABILITY")
    properties.sample_area = metadata.get("AREA")
    return properties


def get_cv_properties(metadata):
    properties = CVProperties()

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
    return properties


def get_ca_properties(metadata, cc=False):
    properties = CAProperties()
    if cc:
        properties = CCProperties()

    vprestep = metadata.get("VPRESTEP")
    if vprestep is not None:
        properties.pre_step_potential = vprestep[0]
        properties.pre_step_potential_measured_against = "Eoc" if vprestep[1] else "Eref"
    properties.pre_step_delay_time = metadata.get("TPRESTEP")

    vstep1 = metadata.get("VSTEP1")
    if vstep1 is not None:
        properties.step_1_potential = vstep1[0]
        properties.step_1_potential_measured_against = "Eoc" if vstep1[1] else "Eref"
    properties.step_1_time = metadata.get("TSTEP1")

    vstep2 = metadata.get("VSTEP2")
    if vstep2 is not None:
        properties.step_2_potential = vstep2[0]
        properties.step_2_potential_measured_against = "Eoc" if vstep2[1] else "Eref"
    properties.step_2_time = metadata.get("TSTEP2")

    properties.sample_period = metadata.get("SAMPLETIME")
    properties.sample_area = metadata.get("AREA")
    return properties


def get_cp_properties(metadata, cc=False):
    properties = CPProperties()

    properties.pre_step_current = metadata.get("IPRESTEP")
    properties.pre_step_delay_time = metadata.get("TPRESTEP")

    properties.step_1_current = metadata.get("ISTEP1")
    properties.step_1_time = metadata.get("TSTEP1")

    properties.step_2_current = metadata.get("ISTEP2")
    properties.step_2_time = metadata.get("TSTEP2")

    properties.lower_limit_potential = metadata.get("VLIMITLOWER")
    properties.upper_limit_potential = metadata.get("VLIMITUPPER")

    properties.sample_period = metadata.get("SAMPLETIME")
    properties.sample_area = metadata.get("AREA")
    return properties


def get_cc_properties(metadata):
    properties = get_ca_properties(metadata, True)
    properties.charge_limit = metadata["QLIMIT"][0]
    return properties


def get_atmosphere_data(metadata):
    properties = Atmosphere()
    properties.ambient_pressure = metadata.get("AIRPRESSURE")
    if not (properties.ambient_pressure is None):
        properties.ambient_pressure /= 1000
    properties.temperature = metadata.get("AIRTEMPERATURE")
    properties.relative_humidity = metadata.get("AIRHUMIDITY")
    return properties


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

    if not entry.description:
        entry.description = metadata.get('NOTES') if metadata.get('NOTES') is not None else None

    entry.station = metadata.get('PSTAT')
    entry.atmosphere = [get_atmosphere_data(metadata)]


# def get_cam_properties_data(metadata, data, mainfile, properties):
#     assert isinstance(properties, CAPropertiesWithData)

#     curve_data = VoltammetryCycle()
#     get_voltammetry_data(data, curve_data)
#     get_ca_properties(metadata, properties)
#     get_meta_datetime(metadata, properties)
#     properties.data_file = mainfile
#     properties.data = curve_data


# def get_eis_properties_data(metadata, data, mainfile, properties):
#     assert isinstance(properties, EISPropertiesWithData)

#     curve_data = EISCycle()
#     get_eis_data(data, curve_data)
#     get_eis_properties(metadata, properties)
#     get_meta_datetime(metadata, properties)
#     properties.data_file = mainfile
#     properties.data = curve_data


def get_voltammetry_archive(data, metadata, entry_class, multiple=False):
    if len(data) > 1 or multiple:
        if entry_class.cycles is None or len(entry_class.cycles) == 0:
            entry_class.cycles = []
            for curve in data:
                cycle = VoltammetryCycleWithPlot()
                get_voltammetry_data(
                    curve, cycle)
                entry_class.cycles.append(cycle)

    if len(data) == 1 and not multiple:
        get_voltammetry_data(
            data[0], entry_class)

    if "OCVCURVE" in metadata and entry_class.pretreatment is None:
        cycle = VoltammetryCycle()
        get_voltammetry_data(
            metadata["OCVCURVE"], cycle)
        entry_class.pretreatment = cycle

    get_meta_data(metadata, entry_class)
