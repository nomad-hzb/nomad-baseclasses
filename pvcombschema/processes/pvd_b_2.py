import numpy as np
import pandas as pd

import os

from ..sample import Sample

from nomad.metainfo import (
    Quantity, Reference, SubSection, Section, MEnum, Datetime, SectionProxy)
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


class MaterialWithProcessValues(ArchiveSection):
    m_def = Section(label_quantity='label')

    name = Quantity(
        type=str,
        a_eln=dict(
            component='StringEditQuantity'))

    comment = Quantity(
        type=str,
        a_eln=dict(
            component='StringEditQuantity'))

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

    label = Quantity(type=str)

    def normalize(self, archive, logger):
        if self.name is not None:
            self.label = self.name
            if self.comment is not None:
                self.label = f'{self.name} {self.comment}'

        if self.current is not None and self.voltage is not None:
            self.power = self.current * self.voltage
            if self.voltage > 0:  # TODO fix!
                self.resistance = self.voltage / self.current


class Stage(ArchiveSection):
    m_def = Section(label_quantity='name')

    name = Quantity(
        type=str,
        a_eln=dict(
            component='StringEditQuantity'))

    start_date = Quantity(
        type=Datetime,
        a_eln=dict(
            component='DateTimeEditQuantity'))

    start_relative = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        a_eln=dict(
            component='NumberEditQuantity', defaultDisplayUnit='s'))

    substrate = SubSection(
        section_def=MaterialWithProcessValues)

    materials = SubSection(
        section_def=MaterialWithProcessValues, repeats=True)

    stages = SubSection(
        section_def=SectionProxy('Stage'), repeats=True)


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


def parse_rga_file(f):
    metadata_started = False
    data_starts_at_line = 0
    metadata = dict()
    while (data_starts_at_line < 20):

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


class PVD_B_2(Process):
    '''Base class for evaporation of a sample'''

    overall = Quantity(
        type=MEnum('Successful', 'Questionable', 'Erroneous'),
        a_eln=dict(
            component='EnumEditQuantity',
        ))

    basis_parameter = SubSection(
        section_def=BasisParameter)

    materials = SubSection(
        section_def=MaterialWithProcessValues, repeats=True)

    stages = SubSection(
        section_def=SectionProxy('Stage'), repeats=True)

    rga = SubSection(
        section_def=RestGasAnalysis)

    objects = SubSection(
        section_def=Object, repeats=True)

    files = SubSection(
        section_def=File, repeats=True)

    data = SubSection(
        section_def=DataPVD_B)

    def normalize(self, archive, logger):
        super(PVD_B_2, self).normalize(archive, logger)

        self.method = "PVD-B alt"

        if self.files is None:
            return

        process_file = ''
        log_file = ''
        rga_file = ''
        for file in self.files:
            # if file.data_file is not None and os.path.splitext(file.data_file)[-1] == ".prozess":
            #     process_file = file.data_file
            if file.data_file is not None and os.path.splitext(file.data_file)[-1] == ".csv":
                log_file = file.data_file
            if file.data_file is not None and os.path.splitext(file.data_file)[-1] == ".txt":
                rga_file = file.data_file

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
