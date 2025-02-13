#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os

import numpy as np
import pandas as pd
from nomad.atomutils import Formula
from nomad.datamodel.data import ArchiveSection
from nomad.datamodel.results import Material, Results
from nomad.metainfo import Quantity, Reference, Section, SectionProxy, SubSection

from .. import BaseMeasurement
from .cesample import ElectroChemicalSetup, Environment


class PotentiostatProperties(ArchiveSection):
    sample_area = Quantity(
        links=['https://w3id.org/nfdi4cat/voc4cat_0000037'],
        type=np.dtype(np.float64),
        unit=('cm^2'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='cm^2'),
    )


class BioLogicSetting(PotentiostatProperties):
    active_material_mass = Quantity(
        type=np.dtype(np.float64),
        unit=('g'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='g'),
    )

    at_x = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity'),
    )

    molecular_weight = Quantity(
        type=np.dtype(np.float64),
        unit=('g/mol'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='g/mol'),
    )

    atomic_weight = Quantity(
        type=np.dtype(np.float64), a_eln=dict(component='NumberEditQuantity')
    )

    acquisition_start = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='s'),
    )

    e_transferred = Quantity(
        type=np.dtype(np.int32),
        a_eln=dict(component='NumberEditQuantity'),
    )

    electrode_material = Quantity(type=str, a_eln=dict(component='StringEditQuantity'))

    electrolyte = Quantity(type=str, a_eln=dict(component='StringEditQuantity'))

    reference_electrode = Quantity(type=str, a_eln=dict(component='StringEditQuantity'))

    characteristic_mass = Quantity(
        type=np.dtype(np.float64),
        unit=('g'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='g'),
    )

    battery_capacity = Quantity(
        type=np.dtype(np.float64),
        unit=('A*hour'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='A*hour'),
    )

    analog_in_1 = Quantity(type=str, a_eln=dict(component='StringEditQuantity'))

    analog_in_1_max_V = Quantity(
        type=np.dtype(np.float64),
        unit=('V'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='V'),
    )

    analog_in_1_min_V = Quantity(
        type=np.dtype(np.float64),
        unit=('V'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='V'),
    )

    analog_in_1_max_x = Quantity(
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'),
    )

    analog_in_1_min_x = Quantity(
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'),
    )

    analog_in_2 = Quantity(type=str, a_eln=dict(component='StringEditQuantity'))

    analog_in_2_max_V = Quantity(
        type=np.dtype(np.float64),
        unit=('V'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='V'),
    )

    analog_in_2_min_V = Quantity(
        type=np.dtype(np.float64),
        unit=('V'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='V'),
    )

    analog_in_2_max_x = Quantity(
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'),
    )

    analog_in_2_min_x = Quantity(
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'),
    )

    def normalize(self, archive, logger):
        if self.electrode_material and not archive.results:
            archive.results = Results()
        archive.results.material = Material()
        try:
            formula = Formula(self.electrode_material, unknown='remove')
            archive.results.material.elements = list(set(formula.elements()))
        except Exception as e:
            logger.warn('Could not analyse material', exc_info=e)
        super().normalize(archive, logger)


class VoltammetryCycle(ArchiveSection):
    time = Quantity(type=np.dtype(np.float64), shape=['*'], unit='s')

    current = Quantity(
        links=['https://w3id.org/nfdi4cat/voc4cat_0007220'],
        type=np.dtype(np.float64),
        shape=['*'],
        unit='mA',
        a_plot=[
            {
                'label': 'Current',
                'x': 'time',
                'y': 'current',
                'layout': {
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
                'config': {'editable': True, 'scrollZoom': True},
            }
        ],
    )

    voltage = Quantity(
        links=['https://w3id.org/nfdi4cat/voc4cat_0007219'],
        type=np.dtype(np.float64),
        shape=['*'],
        unit='V',
        a_plot=[
            {
                'label': 'Voltage',
                'x': 'time',
                'y': 'voltage',
                'layout': {
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
                'config': {'editable': True, 'scrollZoom': True},
            }
        ],
    )

    control = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        unit='V',
        a_plot=[
            {
                'label': 'Control',
                'x': 'time',
                'y': 'control',
                'layout': {
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
                'config': {'editable': True, 'scrollZoom': True},
            }
        ],
    )

    charge = Quantity(
        links=['https://w3id.org/nfdi4cat/voc4cat_0007252'],
        type=np.dtype(np.float64),
        shape=['n_values'],
        unit='mC',
        a_plot=[
            {
                'label': 'Charge',
                'x': 'time',
                'y': 'charge',
                'layout': {
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
                'config': {'editable': True, 'scrollZoom': True},
            }
        ],
    )

    current_density = Quantity(
        links=['https://w3id.org/nfdi4cat/voc4cat_0007221'],
        type=np.dtype(np.float64),
        shape=['n_values'],
        unit='mA/cm^2',
        a_plot=[
            {
                'label': 'Current Density',
                'x': 'time',
                'y': 'current_density',
                'layout': {
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
                'config': {'editable': True, 'scrollZoom': True},
            }
        ],
    )

    voltage_rhe_uncompensated = Quantity(
        links=['https://w3id.org/nfdi4cat/voc4cat_0007219'],
        type=np.dtype(np.float64),
        shape=['n_values'],
        unit='V',
        a_plot=[
            {
                'label': 'Voltage',
                'x': 'time',
                'y': 'voltage_rhe_uncompensated',
                'layout': {
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
                'config': {'editable': True, 'scrollZoom': True},
            }
        ],
    )

    voltage_ref_compensated = Quantity(
        links=['https://w3id.org/nfdi4cat/voc4cat_0007219'],
        type=np.dtype(np.float64),
        shape=['n_values'],
        unit='V',
        a_plot=[
            {
                'label': 'Voltage',
                'x': 'time',
                'y': 'voltage_ref_compensated',
                'layout': {
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
                'config': {'editable': True, 'scrollZoom': True},
            }
        ],
    )

    voltage_rhe_compensated = Quantity(
        links=['https://w3id.org/nfdi4cat/voc4cat_0007219'],
        type=np.dtype(np.float64),
        shape=['n_values'],
        unit='V',
        a_plot=[
            {
                'label': 'Voltage',
                'x': 'time',
                'y': 'voltage_rhe_compensated',
                'layout': {
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
                'config': {'editable': True, 'scrollZoom': True},
            }
        ],
    )

    export_this_cycle_to_csv = Quantity(
        type=bool, default=False, a_eln=dict(component='BoolEditQuantity')
    )

    export_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'),
    )

    def export_cycle(self, archive, name):
        if self.export_this_cycle_to_csv:
            self.export_this_cycle_to_csv = False
            df = pd.DataFrame()
            if self.time is not None:
                df['time'] = self.time
            if self.current is not None:
                df['current'] = self.current
            if self.voltage is not None:
                df['voltage'] = self.voltage
            if self.control is not None:
                df['control'] = self.control
            if self.charge is not None:
                df['charge'] = self.charge
            if self.current_density is not None:
                df['current_density'] = self.current_density
            if self.voltage_rhe_uncompensated is not None:
                df['voltage_rhe_uncompensated'] = self.voltage_rhe_uncompensated
            if self.voltage_ref_compensated is not None:
                df['voltage_ref_compensated'] = self.voltage_ref_compensated
            if self.voltage_rhe_compensated is not None:
                df['voltage_rhe_compensated'] = self.voltage_rhe_compensated
            name = name.replace('#', '')
            export_name = f'{name}.csv'
            with archive.m_context.raw_file(export_name, 'w') as outfile:
                df.to_csv(outfile.name)
            self.export_file = export_name


class PotentiostatSetup(ArchiveSection):
    flow_cell_pump_rate = Quantity(
        type=np.dtype(np.float64),
        unit=('mL/minute'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mL/minute'),
    )

    flow_cell_pressure = Quantity(
        links=['https://w3id.org/nfdi4cat/voc4cat_0000118'],
        type=np.dtype(np.float64),
        unit=('bar'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='bar'),
    )

    rotation_speed = Quantity(
        type=np.dtype(np.float64),
        unit=('rpm'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='rpm'),
    )


class PotentiostatMeasurement(BaseMeasurement):
    m_def = Section(
        links=['https://w3id.org/nfdi4cat/voc4cat_0007206'],
    )

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'),
    )

    station = Quantity(type=str, a_eln=dict(component='StringEditQuantity'))

    function = Quantity(type=str, a_eln=dict(component='StringEditQuantity'))

    environment = Quantity(
        links=['https://w3id.org/nfdi4cat/voc4cat_0007223'],
        type=Reference(Environment.m_def),
        a_eln=dict(component='ReferenceEditQuantity'),
    )

    setup = Quantity(
        links=['https://w3id.org/nfdi4cat/voc4cat_0007230'],
        type=Reference(ElectroChemicalSetup.m_def),
        a_eln=dict(component='ReferenceEditQuantity'),
    )

    connected_experiments = Quantity(
        type=Reference(SectionProxy('PotentiostatMeasurement')),
        shape=['*'],
        a_eln=dict(component='ReferenceEditQuantity'),
    )

    pretreatment = SubSection(section_def=VoltammetryCycle)

    setup_parameters = SubSection(section_def=PotentiostatSetup)

    properties = SubSection(section_def=PotentiostatProperties)

    def normalize(self, archive, logger):
        super().normalize(archive, logger)

        if self.pretreatment is not None:
            self.pretreatment.export_cycle(
                archive, os.path.splitext(self.data_file)[0] + '_pretreatment'
            )
