import numpy as np
import pandas as pd

import os

from ..sample import Sample

from nomad.metainfo import (
    Quantity, Reference, SubSection, Section, MEnum, Datetime)
from nomad.datamodel.data import ArchiveSection

from nomad.datamodel.metainfo.eln import Process


class BasisParameter(ArchiveSection):

    process_type = Quantity(
        type=str,
        a_eln=dict(
            component='StringEditQuantity'))

    standard_process = Quantity(
        type=bool,
        a_eln=dict(
            component='BoolEditQuantity'))

    process_recipe = Quantity(
        type=str,
        a_eln=dict(
            component='StringEditQuantity'))

    relative_humidity_load = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(
            component='NumberEditQuantity'))

    relative_humidity_process_start = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(
            component='NumberEditQuantity'))

    relative_humidity_unload = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(
            component='NumberEditQuantity'))

    pressure_process_start = Quantity(
        type=np.dtype(np.float64),
        unit=('mbar'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mbar'))

    pressure_start_stage_1a = Quantity(
        type=np.dtype(np.float64),
        unit=('mbar'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mbar'))


class Values(ArchiveSection):
    temperature = Quantity(
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='°C'))

    current = Quantity(
        type=np.dtype(np.float64),
        unit=('A'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='A'))

    voltage = Quantity(
        type=np.dtype(np.float64),
        unit=('V'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='V'))

    power = Quantity(
        type=np.dtype(np.float64),
        unit=('W'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='W'))

    resistance = Quantity(
        type=np.dtype(np.float64),
        unit=('ohm'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='ohm'))

    def normalize(self, archive, logger):

        if self.current is not None and self.voltage is not None:
            self.power = self.current * self.voltage
            if self.current > 0: 
                self.resistance = self.voltage / self.current


class EvaporationWithDualFilament(ArchiveSection):

    temperature_hl_3 = Quantity(
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='°C'))

    temperature_ec_3 = Quantity(
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='°C'))

    period = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='s'))


class Copper(EvaporationWithDualFilament):

    m_def = Section(
        a_eln=dict(
            hide=[
                'temperature_hl_3',
                'temperature_ec_3']))

    period = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='s', label="Period ILR"))
    hl_2 = SubSection(section_def=Values)
    ec_2 = SubSection(section_def=Values)

    def normalize(self, archive, logger):
        self.hl_2.normalize(archive, logger)
        self.ec_2.normalize(archive, logger)


class Indium(EvaporationWithDualFilament):

    hl_1 = SubSection(section_def=Values)
    ec_1 = SubSection(section_def=Values)

    period = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='s', label="Period INSE 1"))

    def normalize(self, archive, logger):
        self.hl_1.normalize(archive, logger)
        self.ec_1.normalize(archive, logger)


class Galium(EvaporationWithDualFilament):

    hl_1 = SubSection(section_def=Values)
    ec_1 = SubSection(section_def=Values)

    period = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='s', label="Period GA SE"))

    def normalize(self, archive, logger):
        self.hl_1.normalize(archive, logger)
        self.ec_1.normalize(archive, logger)


class Substrate(ArchiveSection):

    t_substrate_3 = Quantity(
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='°C'))

    delta_t_substrate_2 = Quantity(
        type=np.dtype(np.float64),
        unit=('K/minute'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='K/minute'))

    delta_t_substrate_3 = Quantity(
        type=np.dtype(np.float64),
        unit=('K/minute'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='K/minute'))

    delta_t_substrate_4 = Quantity(
        type=np.dtype(np.float64),
        unit=('K/minute'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='K/minute'))

    substrate_unload_process = Quantity(
        type=str,
        a_eln=dict(
            component='StringEditQuantity'))

    substrate_1 = SubSection(section_def=Values)
    substrate_2 = SubSection(section_def=Values)

    def normalize(self, archive, logger):
        self.substrate_1.normalize(archive, logger)
        self.substrate_2.normalize(archive, logger)


class ValvedSeleniumCrackerSource(ArchiveSection):
    t_cracker_1a = Quantity(
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='°C'))

    t_cracker_2 = Quantity(
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='°C'))

    t_cracker_3 = Quantity(
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='°C'))

    mass_se_with_pan = Quantity(
        type=np.dtype(np.float64),
        unit=('g'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='g'))

    mass_se_after = Quantity(
        type=np.dtype(np.float64),
        unit=('g'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='g'))

    se_refilled = Quantity(
        type=bool,
        a_eln=dict(
            component='BoolEditQuantity'))

    t_valve_reservoir_1a = Quantity(
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='°C'))

    t_valve_reservoir_2 = Quantity(
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='°C'))

    t_valve_reservoir_3 = Quantity(
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='°C'))

    valve_position_1a = Quantity(
        type=np.dtype(np.float64),
        unit=('mm'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mm'))

    valve_position_1b = Quantity(
        type=np.dtype(np.float64),
        unit=('mm'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mm'))

    valve_position_2 = Quantity(
        type=np.dtype(np.float64),
        unit=('mm'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mm'))

    valve_position_3 = Quantity(
        type=np.dtype(np.float64),
        unit=('mm'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mm'))

    processes_since_se = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(
            component='NumberEditQuantity'))

    cracker_1b = SubSection(section_def=Values)
    valve_reservoir_1b = SubSection(section_def=Values)

    def normalize(self, archive, logger):
        self.cracker_1b.normalize(archive, logger)
        self.valve_reservoir_1b.normalize(archive, logger)


class ProcessTimes(ArchiveSection):

    heating = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='s'))
    presenilization = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='s'))
    time_1a = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='s'))
    time_1b = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='s'))
    time_1c = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='s'))
    time_1d = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='s'))
    time_2 = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='s'))
    time_2a = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='s'))
    time_2b = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='s'))
    time_3a = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='s'))
    time_3b = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='s'))
    time_3c = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='s'))
    time_4 = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='s'))
    overall = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='s'))


class Object(ArchiveSection):
    m_def = Section(label_quantity='name')

    sample = Quantity(
        type=Reference(Sample.m_def),
        a_eln=dict(component='ReferenceEditQuantity'))

    position = Quantity(
        type=np.dtype(np.int64),
        a_eln=dict(component='NumberEditQuantity'))

    name = Quantity(type=str)

    def normalize(self, archive, logger):

        if self.sample is not None and self.sample.lab_id is not None:
            self.name = self.sample.lab_id


class File(ArchiveSection):
    m_def = Section(label_quantity='name')
    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    datetime = Quantity(
        type=Datetime,
        a_eln=dict(component='DateTimeEditQuantity'))

    entered_by = Quantity(
        type=str,
        a_eln=dict(
            component='StringEditQuantity'))

    name = Quantity(type=str)

    def normalize(self, archive, logger):

        if self.data_file is not None:
            self.name = self.data_file


class Alkali(ArchiveSection):
    material = Quantity(
        type=str,
        a_eln=dict(
            component='StringEditQuantity'))

    rate = Quantity(
        type=np.dtype(np.float64),
        unit=('angstrom/s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='angstrom/s'))

    thickness_nominal = Quantity(
        type=np.dtype(np.float64),
        unit=('nm'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='nm'))

    period = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='s'))

    notes = Quantity(
        type=str,
        a_eln=dict(
            component='StringEditQuantity'))

    hl = SubSection(section_def=Values)
    ec = SubSection(section_def=Values)

    def normalize(self, archive, logger):
        self.hl.normalize(archive, logger)
        self.ec.normalize(archive, logger)


class RestGasAnalysis(ArchiveSection):

    m_def = Section(
        a_plot=[
            {
                'label': 'Rest Gas Analysis',
                'x': 'ratio',
                'y': 'current',
                'layout': {
                    'yaxis': {
                        "fixedrange": False},
                    'xaxis': {
                        "fixedrange": False}},
            }])

    noise_floor = Quantity(
        type=np.dtype(np.int64),
        unit=('nm'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='nm'))

    cem_status = Quantity(
        type=bool,
        a_eln=dict(
            component='BoolEditQuantity'))

    points_per_amu = Quantity(
        type=np.dtype(np.int64),
        unit=('nm'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='nm'))

    scan_start_mass = Quantity(
        type=np.dtype(np.int64),
        unit=('nm'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='nm'))

    scan_stop_mass = Quantity(
        type=np.dtype(np.int64),
        unit=('amu'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='amu'))

    focus_voltage = Quantity(
        type=np.dtype(np.float64),
        unit=('V'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='V'))

    ion_energy = Quantity(
        type=str,
        a_eln=dict(
            component='StringEditQuantity'))

    electron_energy = Quantity(
        type=np.dtype(np.float64),
        unit=('eV'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='eV'))

    cem_voltage = Quantity(
        type=np.dtype(np.float64),
        unit=('V'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='V'))

    cem_gain = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(
            component='NumberEditQuantity'))

    sensitivity_factor = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(
            component='NumberEditQuantity'))

    filament_current = Quantity(
        type=np.dtype(np.float64),
        unit=('mA'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mA'))

    ratio = Quantity(
        type=np.dtype(
            np.float64), shape=['*'])

    current = Quantity(
        type=np.dtype(
            np.float64), shape=['*'], unit='A')


def get_rga(metadata, df):
    rga = RestGasAnalysis()
    rga.ratio = df[0]
    rga.current = df[1]
    rga.noise_floor = metadata.get("Noise Floor", None)
    rga.cem_status = metadata.get("CEM Status", None) == "ON"
    rga.points_per_amu = metadata.get("Points Per AMU", None)
    rga.scan_start_mass = metadata.get("Scan Start Mass", None)
    rga.scan_stop_mass = metadata.get("Scan Stop Mass", None)
    rga.focus_voltage = metadata.get("Focus Voltage", None)
    rga.ion_energy = metadata.get("Ion Energy", None)
    rga.electron_energy = metadata.get("Electron Energy", None)
    rga.cem_voltage = metadata.get("CEM Voltage", None)
    rga.cem_gain = metadata.get("CEM Gain", None)
    rga.sensitivity_factor = metadata.get("Sensitivity Factor", None)
    rga.filament_current = metadata.get("Filament Current", None)
    return rga


def get_pd_value(df, column_index_name, row_index_name, typ):
    if row_index_name in df.index:
        # if there is no "nan" in the cell
        if pd.isna(df[column_index_name].loc[row_index_name]) is not True:
            value = df[column_index_name].loc[row_index_name]
            if typ == "float":
                value = float(value)
            else:
                pass
        else:
            return None
    else:
        return None
    return value


def get_process_times(df):
    process_times = ProcessTimes()
    process_times.heating = get_pd_value(
        df, "Phase", "Heating (300°C; closed shutter)", "float")
    process_times.presenilization = get_pd_value(
        df, "Phase", "Preselenization", "float")
    process_times.time_1a = get_pd_value(df, "Phase", "Phase Ia (Ga)", "float")
    process_times.time_1b = get_pd_value(df, "Phase", "Phase Ib (In)", "float")
    process_times.time_1c = get_pd_value(df, "Phase", "Phase Ic (Ga)", "float")
    process_times.time_1d = get_pd_value(df, "Phase", "Phase Id (In)", "float")
    process_times.time_2 = get_pd_value(df, "Phase", "Phase II", "float")
    process_times.time_2a = get_pd_value(df, "Phase", "Phase IIa", "float")
    process_times.time_2b = get_pd_value(df, "Phase", "Phase IIb", "float")
    process_times.time_3a = get_pd_value(
        df, "Phase", "Phase IIIa (In+Ga)", "float")
    process_times.time_3b = get_pd_value(
        df, "Phase", "Phase IIIb (In)", "float")
    process_times.time_3c = get_pd_value(
        df, "Phase", "Phase IIIc (heating)", "float")
    process_times.time_4 = get_pd_value(
        df, "Phase", "Phase IV (alkali PDT + Abkühlen)", "float")

    timelist = [process_times.heating, process_times.presenilization, process_times.time_1a,
                process_times.time_1b, process_times.time_1c,
                process_times.time_1d, process_times.time_2, process_times.time_2a,
                process_times.time_2b, process_times.time_3a, process_times.time_3b,
                process_times.time_3c, process_times.time_4]
    process_times.overall = 0
    for process_time in timelist:
        process_times.overall += process_time

    return process_times


def get_basis_parameter(df):
    basis_parameter = BasisParameter()
    basis_parameter.pressure_process_start = get_pd_value(
        df, "b", "Pressure at beginning of process (mBar)", "float")
    basis_parameter.pressure_start_stage_1a = get_pd_value(
        df, "b", "Pressure at beginning of stage Ia (mBar)", "float")
    basis_parameter.relative_humidity_process_start = get_pd_value(
        df, "b", "Luftfeuchtigkeit (%)", "float")
    # basis_parameter.relative_humidity_process_load = prove_digit_entry(luftfeuchte_ein_field.get(), "Luftfeuchte einschleusen")
    # basis_parameter.relative_humidity_process_unload = prove_digit_entry(luftfeuchte_aus_field.get(), "Luftfeuchte ausschleusen")
    return basis_parameter


def get_substrate(df):
    substrate = Substrate()
    substrate.substrate_1 = get_values(df, "Substrat Phase 1", "Substrat 1")
    substrate.substrate_2 = get_values(df, "Substrat Phase 2", "Substrat 2")
    # v8422 = ausschleuse.get()
    return substrate


def get_values(df, temperature, i_and_v=None):
    values = Values()
    if i_and_v == None:
        i_and_v = temperature
    values.temperature = get_pd_value(
        df, "b", "T {} (°C)".format(temperature), "float")
    values.current = get_pd_value(
        df, "b", "I {} (A)".format(i_and_v), "float")
    values.voltage = get_pd_value(
        df, "b", "U {} (V)".format(i_and_v), "float")
    return values


def get_copper(df):
    copper = Copper()
    copper.period = get_pd_value(df, "b", "Cu-Periode (s)", "float")
    copper.hl_2 = get_values(df, "Cu HL", "Cu HL 1")
    copper.ec_2 = get_values(df, "Cu EC", "Cu EC 1")
    return copper


def get_phase_3_temperature(df, entity, material):
    entity.temperature_hl_3 = get_pd_value(
        df, "b", "T {} HL Phase 3 (°C)".format(material), "float")
    entity.temperature_ec_3 = get_pd_value(
        df, "b", "T {} EC Phase 3 (°C)".format(material), "float")


def get_indium(df):
    indium = Indium()
    indium.period = get_pd_value(df, "b", "In-Periode (s)", "float")
    indium.hl_1 = get_values(df, "In HL", "In HL 1")
    indium.ec_1 = get_values(df, "In EC", "In EC 1")
    get_phase_3_temperature(df, indium, "In")
    return indium


def get_galium(df):
    galium = Galium()
    galium.period = get_pd_value(df, "b", "Ga-Periode (s)", "float")
    galium.hl_1 = get_values(df, "Ga HL", "Ga HL 1")
    galium.ec_1 = get_values(df, "Ga EC", "Ga EC 1")
    get_phase_3_temperature(df, galium, "Ga")
    return galium


def get_valved_selenium_cracker_source(df):
    valved = ValvedSeleniumCrackerSource()
    valved.cracker_1b = get_values(df, "Cracker 1b")
    valved.valve_reservoir_1b = get_values(df, "Valve/Reservoir 1b")
    valved.t_cracker_1a = get_pd_value(df, "b", "T Cracker 1a (°C)", "float")
    valved.t_valve_reservoir_1a = get_pd_value(
        df, "b", "T Valve/Reservoir 1a (°C)", "float")
    valved.valve_position_1a = get_pd_value(
        df, "b", "Ventilstellung 1a (mm)", "float")
    valved.valve_position_1b = get_pd_value(
        df, "b", "Ventilstellung 1b (mm)", "float")
    valved.t_cracker_2 = get_pd_value(df, "b", "T Cracker 2 (°C)", "float")
    valved.t_valve_reservoir_2 = get_pd_value(
        df, "b", "T Valve/Reservoir 2 (°C)", "float")
    valved.valve_position_2 = get_pd_value(
        df, "b", "Ventilstellung 2 (mm)", "float")
    valved.t_cracker_3 = get_pd_value(df, "b", "T Cracker 3 (°C)", "float")
    valved.t_valve_reservoir_3 = get_pd_value(
        df, "b", "T Valve/Reservoir 3 (°C)", "float")
    valved.valve_position_3 = get_pd_value(
        df, "b", "Ventilstellung 3 (mm)", "float")
    return valved


def get_alkali(df, alkali_mat):
    alkali = Alkali()
    alkali.material = alkali_mat
    alkali.hl = get_values(df, f"{alkali_mat} HL")
    alkali.ec = get_values(df, f"{alkali_mat} EC")
    return alkali


def get_objects(df):
    sample_list = []
    sample_list.append(get_pd_value(df, "b", "Substrat 1", "text"))
    sample_list.append(get_pd_value(df, "b", "Substrat 2", "text"))
    sample_list.append(get_pd_value(df, "b", "Substrat 3", "text"))
    sample_list.append(get_pd_value(df, "b", "Substrat 4", "text"))
    sample_list.append(get_pd_value(df, "b", "Substrat 5", "text"))
    sample_list.append(get_pd_value(df, "b", "Substrat 6", "text"))
    sample_list.append(get_pd_value(df, "b", "Substrat 7", "text"))

    sample_list.append(get_pd_value(df, "b", "RFA-Sbstrat 1", "text"))
    sample_list.append(get_pd_value(df, "b", "RFA-Sbstrat 2", "text"))
    sample_list.append(get_pd_value(df, "b", "RFA-Sbstrat 3", "text"))
    sample_list.append(get_pd_value(df, "b", "RFA-Sbstrat 4", "text"))


def get_alkali_materials(df):
    #parse for alkali information
    alkali_dict = {}
    if "T NaF HL (°C)" in df.index:
        # add entry with index as key, alkali as value
        alkali_dict[df.index.get_loc("T NaF HL (°C)")] = "NaF"
    if "T RbF HL (°C)" in df.index:
        # add entry with index as key, alkali as value
        alkali_dict[df.index.get_loc("T RbF HL (°C)")] = "RbF"
    if "T KF HL (°C)" in df.index:
        # add entry with index as key, alkali as value
        alkali_dict[df.index.get_loc("T KF HL (°C)")] = "KF"
    if "T CsF HL (°C)" in df.index:
        # add entry with index as key, alkali as value
        alkali_dict[df.index.get_loc("T CsF HL (°C)")] = "CsF"
    alkali_dict = dict(sorted(alkali_dict.items()))
    return alkali_dict


def parse_rga_file(f):
    metadata_started = False
    data_starts_at_line = 0
    metadata = dict()
    while(data_starts_at_line < 20):

        data_starts_at_line += 1
        line = f.readline()
        if line.strip() == '' and not metadata:
            continue

        if metadata_started:
            line = line.split(",")
            if len(line) >= 2:
                metadata.update({line[0].strip(): line[1].strip()})
            else:
                break

        if not metadata_started and line.strip().startswith("Analog"):
            metadata_started = True
    return metadata, pd.read_csv(f.name, header=None, skiprows=data_starts_at_line+2, skip_blank_lines=False, delimiter=",")[[0, 1]]


class DataPVD_B(ArchiveSection):
    ilr = Quantity(
        type=np.dtype(
            np.float64), shape=['*'], unit='A')

    lls = Quantity(
        type=np.dtype(
            np.float64), shape=['*'], unit='A')

    substrate_temperature = Quantity(
        type=np.dtype(
            np.float64), shape=['*'], unit='°C')

    pyrometer = Quantity(
        type=np.dtype(
            np.float64), shape=['*'], unit='°C')

    heating_power = Quantity(
        type=np.dtype(
            np.float64), shape=['*'])

    se_rate = Quantity(
        type=np.dtype(
            np.float64), shape=['*'], unit='angstrom/s')

    vcsc_valveposition = Quantity(
        type=np.dtype(
            np.float64), shape=['*'], unit='mm')

    pumpchamber_pressure = Quantity(
        type=np.dtype(
            np.float64), shape=['*'], unit='mbar')

    growthchamber_pressure = Quantity(
        type=np.dtype(
            np.float64), shape=['*'], unit='mbar')

    shroud_temperature_mid = Quantity(
        type=np.dtype(
            np.float64), shape=['*'], unit='°C')

    shroud_temperature_up = Quantity(
        type=np.dtype(
            np.float64), shape=['*'], unit='°C')

    shroud_temperature_down = Quantity(
        type=np.dtype(
            np.float64), shape=['*'], unit='°C')

    process_time = Quantity(
        type=np.dtype(
            np.float64), shape=['*'], unit='minute')

class PVD_B(Process):
    '''Base class for evaporation of a sample'''

    overall = Quantity(
        type=MEnum('Successful', 'Questionable', 'Erroneous'),
        a_eln=dict(
            component='EnumEditQuantity',
        ))

   

    basis_parameter = SubSection(
        section_def=BasisParameter)

    substrate = SubSection(
        section_def=Substrate)

    copper = SubSection(
        section_def=Copper)

    indium = SubSection(
        section_def=Indium)

    galium = SubSection(
        section_def=Galium)

    valved_selenium_cracker_source = SubSection(
        section_def=ValvedSeleniumCrackerSource)

    alkali_1 = SubSection(
        section_def=Alkali)

    alkali_2 = SubSection(
        section_def=Alkali)

    rga = SubSection(
        section_def=RestGasAnalysis)

    process_times = SubSection(
        section_def=ProcessTimes)

    objects = SubSection(
        section_def=Object, repeats=True)

    files = SubSection(
        section_def=File, repeats=True)
    
    data = SubSection(
        section_def=DataPVD_B)

    def normalize(self, archive, logger):
        super(PVD_B, self).normalize(archive, logger)

        self.method = "PVD-B"

        if self.files is None:
            return

        process_file = ''
        log_file = ''
        rga_file = ''
        for file in self.files:
            if file.data_file is not None and os.path.splitext(file.data_file)[-1] == ".prozess":
                process_file = file.data_file
            if file.data_file is not None and os.path.splitext(file.data_file)[-1] == ".csv":
                log_file = file.data_file
            if file.data_file is not None and os.path.splitext(file.data_file)[-1] == ".txt":
                rga_file = file.data_file

        if process_file:

            # with archive.m_context.raw_file(process_file, "br") as f:
            #     import chardet
            #     encoding = chardet.detect(f.read())["encoding"]

            with archive.m_context.raw_file(process_file) as f:
                df = pd.read_csv(f.name, header=0, delimiter="\t",
                                 nrows=14, index_col=2, encoding="ISO-8859-1" )
                df["timestamp"] = pd.to_datetime(
                    df["timestamp"], format="%d.%m.%Y %H:%M:%S.%f")

                df2 = pd.read_csv(f.name, header=None, skiprows=16, delimiter=":",
                                  index_col=0, skipinitialspace=True, names=list("abcdef"), encoding="ISO-8859-1" )  # , nrows=68
            
            self.process_times = get_process_times(df)
            self.basis_parameter = get_basis_parameter(df2)
            self.substrate = get_substrate(df2)
            self.substrate.normalize(archive, logger)
            self.copper = get_copper(df2)
            self.copper.normalize(archive, logger)
            self.indium = get_indium(df2)
            self.indium.normalize(archive, logger)
            self.galium = get_galium(df2)
            self.galium.normalize(archive, logger)
            self.valved_selenium_cracker_source = get_valved_selenium_cracker_source(
                df2)
            self.valved_selenium_cracker_source.normalize(archive, logger)

            alkalis = get_alkali_materials(df2)
            if len(alkalis) >= 1:
                self.alkali_1 = get_alkali(df2, list(alkalis.values())[0])
                self.alkali_1.normalize(archive, logger)

            if len(alkalis) == 2:
                self.alkali_2 = get_alkali(df2,  list(alkalis.values())[1])
                self.alkali_2.normalize(archive, logger)

        if log_file:

            # with archive.m_context.raw_file(log_file, "br") as f:
            #     import chardet
            #     encoding = chardet.detect(f.read())["encoding"]

            with archive.m_context.raw_file(log_file) as f:
                df = pd.read_csv(f.name, header=0, encoding="ascii")

            start = 500  # df.d_VSCS.ne(0).idxmax()
            end = df["ILR"].dropna().size

            ts = pd.to_datetime(
                df['Zeit_VSCS'], format="%H:%M:%S").dropna().iloc[start:end]
            td = ts - ts.iloc[0]
            td_sec = td.dt.total_seconds()
            
            
            data_section = DataPVD_B()

            data_section.process_time = td_sec / 60
            

            data_section.ilr = df["ILR"].iloc[start:end]
            data_section.lls = df["LLS"].iloc[start:end]
            data_section.substrate_temperature = df["TSub"].iloc[start:end]
            data_section.pyrometer = df["Temp_Pyro"].iloc[start:end]
            data_section.heating_power = df["pSub"].iloc[start:end]
            data_section.se_rate = df["Rate_A_s_"].iloc[start:end]
            data_section.vcsc_valveposition = df["d_VSCS"].iloc[start:end]
            data_section.pumpchamber_pressure = df["p_Pumpemkammer_mbar"].iloc[start:end]
            data_section.growthchamber_pressure = df["p_Wachstumskammer_mbar"].iloc[start:end]
            data_section.shroud_temperature_mid = df["T_KS_mitte"].iloc[start:end]
            data_section.shroud_temperature_up = df["T_KS_oben"].iloc[start:end]
            data_section.shroud_temperature_down = df["T_KS_unten"].iloc[start:end]
            
            self.data = data_section

        if rga_file:

            with archive.m_context.raw_file(rga_file) as f:
                metadata, data = parse_rga_file(f)
            self.rga = get_rga(metadata, data)
