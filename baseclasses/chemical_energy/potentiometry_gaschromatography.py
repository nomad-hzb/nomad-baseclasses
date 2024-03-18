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

import numpy as np

from nomad.metainfo import (Quantity, SubSection, Datetime, MEnum)
from nomad.datamodel.data import ArchiveSection

from .. import BaseMeasurement


class NECCExperimentalProperties(ArchiveSection):

    experiment_id = Quantity(
        type=str,
        default='User_Date_Number',
        a_eln=dict(component='StringEditQuantity', label='Experiment id'))

    fill_in_default = Quantity(
        type=bool,
        default=False,
        description='Check this box and press the save button to load default entries.',
        a_eln=dict(component='BoolEditQuantity'))

    cell_type = Quantity(
        type=MEnum('Zero-Gap', 'Catholyte Flow', 'H-Cell'),
        shape=[],
        a_eln=dict(component='EnumEditQuantity'))

    has_reference_electrode = Quantity(
        type=bool,
        default=False,
        a_eln=dict(component='BoolEditQuantity'))

    # TODO how to save N/A; if has_reference_electrode is false reference_electrode_type is N/A
    reference_electrode_type = Quantity(
        type=MEnum('Ag/AgCl', 'Hg/HgO',	'N/A'),
        shape=[],
        a_eln=dict(component='EnumEditQuantity'))

    cathode_geometric_area = Quantity(
        type=np.dtype(np.float64),
        unit=('cm^2'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='cm^2'))

    membrane_type = Quantity(
        type=MEnum('AEM', 'CEM'),
        shape=[],
        a_eln=dict(component='EnumEditQuantity'))

    membrane_name = Quantity(
        type=MEnum('PiperION', 'SustainION', 'Fumasep', 'Nafion'),
        shape=[],
        a_eln=dict(component='EnumEditQuantity'))

    membrane_thickness = Quantity(
        type=np.dtype(np.float64),
        unit=('um'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='um', props=dict(minValue=0)))

    gasket_thickness = Quantity(
        type=np.dtype(np.float64),
        unit=('um'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='um', props=dict(minValue=0)))

    anolyte_type = Quantity(
        type=MEnum('KOH', 'KHCO3'),
        shape=[],
        a_eln=dict(component='EnumEditQuantity'))

    anolyte_concentration = Quantity(
        type=np.dtype(np.float64),
        unit=('mol/L'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mol/L'))

    anolyte_flow_rate = Quantity(
        type=np.dtype(np.float64),
        unit=('ml/minute'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='ml/minute',
            props=dict(minValue=0)
        ))

    anolyte_volume = Quantity(
        type=np.dtype(np.float64),
        unit=('ml'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='ml'))

    has_humidifier = Quantity(
        type=bool,
        default=True,
        a_eln=dict(component='BoolEditQuantity')
    )

    humidifier_temperature = Quantity(
        type=np.dtype(np.float64),
        unit='°C',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'))

    water_trap_volume = Quantity(
        type=np.dtype(np.float64),
        unit=('ml'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='ml'))

    #TODO 2 possible feed gases
    feed_gas = Quantity(
        type=MEnum('CO2', 'CO', 'H2'),
        shape=[],
        a_eln=dict(component='EnumEditQuantity'))

    feed_gas_flow_rate = Quantity(
        type=np.dtype(np.float64),
        unit=('ml/minute'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='ml/minute',
            props=dict(minValue=0)
        ))

    bleedline_flow_rate = Quantity(
        type=np.dtype(np.float64),
        unit=('ml/minute'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='ml/minute',
            props=dict(minValue=0)
        ))

    nitrogen_start_value = Quantity(
        type=np.dtype(np.float64),
        description='Specified in ppm',
        a_eln=dict(component='NumberEditQuantity'))

    remarks = Quantity(
        type=str,
        a_eln=dict(
            component='RichTextEditQuantity',
            label="Remarks"
        ))

    chronoanalysis_method = Quantity(
        type=MEnum('Chronoamperometry (CA)', 'Chronopotentiometry (CP)'),
        shape=[],
        a_eln=dict(component='EnumEditQuantity'))

    # TODO anode and cathode ID

    def normalize(self, archive, logger):

        #TODO only apply defaults to empty fields?
        if self.fill_in_default:
            self.cell_type = 'Zero-Gap'
            self.has_reference_electrode = False
            self.reference_electrode_type = 'N/A'
            self.cathode_geometric_area = 8
            self.membrane_type = 'AEM'
            self.membrane_name = 'PiperION'
            self.membrane_thickness = 40
            self.gasket_thickness = 200
            self.anolyte_type = 'KOH'
            self.anolyte_concentration = 1.0
            self.anolyte_flow_rate = 15
            self.anolyte_volume = 25
            self.has_humidifier = True
            self.humidifier_temperature = 25
            self.water_trap_volume = 10
            self.feed_gas = 'CO2'
            self.feed_gas_flow_rate = 60
            self.bleedline_flow_rate = 20
            self.chronoanalysis_method = 'Chronopotentiometry (CP)'


class GasChromatographyOutput(ArchiveSection):

    experiment_name = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'))

    datetime = Quantity(
        type=Datetime,
        shape=['*'])

    gas_type = Quantity(
        type=MEnum('CO', 'CH4', 'C2H4', 'C2H6', 'H2', 'N2'),
        shape=[],
        a_eln=dict(component='EnumEditQuantity'))

    retention_time = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        unit='minute')

    area = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        unit='pA*minute')

    ppm = Quantity(
        type=np.dtype(np.float64),
        description='Specified in ppm',
        shape=['*'])


class PotentiostatOutput(ArchiveSection):
    datetime = Quantity(
        type=Datetime,
        shape=['*'])
    # TODO maybe remove this because there is also time in s

    time = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        unit='s')

    current = Quantity(
        type=np.dtype(
            np.float64), shape=['*'], unit='mA', a_plot=[
            {
                "label": "Current", 'x': 'time', 'y': 'current', 'layout': {
                'yaxis': {
                    "fixedrange": False}, 'xaxis': {
                    "fixedrange": False}}, "config": {
                "editable": True, "scrollZoom": True}}])

    working_electrode_potential = Quantity(
        type=np.dtype(
            np.float64), shape=['*'], unit='V', a_plot=[
            {
                "label": "Working Electrode Potential (Ewe)", 'x': 'time', 'y': 'working_electrode_potential',
                'layout': {
                    'yaxis': {
                        "fixedrange": False}, 'xaxis': {
                        "fixedrange": False}}, "config": {
                "editable": True, "scrollZoom": True}}])


class ThermocoupleOutput(ArchiveSection):

    time = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        unit='s')

    # TODO can i combine two columns in datetime?
    datetime = Quantity(
        type=Datetime,
        shape=['*'])

    pressure = Quantity(
        type=np.dtype(
            np.float64), shape=['*'], unit='bar', a_plot=[
            {
                "label": "Pressure (in barg)", 'x': 'time', 'y': 'pressure', 'layout': {
                'yaxis': {
                    "fixedrange": False}, 'xaxis': {
                    "fixedrange": False}}, "config": {
                "editable": True, "scrollZoom": True}}])

    temperature_cathode = Quantity(
        type=np.dtype(
            np.float64), shape=['*'], unit='°C', a_plot=[
            {
                "label": "Temperature Cathode", 'x': 'time', 'y': 'temperature_cathode', 'layout': {
                'yaxis': {
                    "fixedrange": False}, 'xaxis': {
                    "fixedrange": False}}, "config": {
                "editable": True, "scrollZoom": True}}])

    temperature_anode = Quantity(
        type=np.dtype(
            np.float64), shape=['*'], unit='°C', a_plot=[
            {
                "label": "Temperature Anode", 'x': 'time', 'y': 'temperature_anode', 'layout': {
                'yaxis': {
                    "fixedrange": False}, 'xaxis': {
                    "fixedrange": False}}, "config": {
                "editable": True, "scrollZoom": True}}])


class GasFEResults(ArchiveSection):
    # TODO model class like this or combine it with gaschromatography class?

    gas_type = Quantity(
        type=MEnum('CO', 'CH4', 'C2H4', 'H2'),
        shape=[],
        a_eln=dict(component='EnumEditQuantity'))

    current = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        unit='mA')

    faradaic_efficiency = Quantity(
        type=np.dtype(np.float64),
        description='Faradaic efficiency specified in %',
        shape=['*'])

    mean_fe = Quantity(
        type=np.dtype(np.float64), a_eln=dict(component='NumberEditQuantity'))

    variance_fe = Quantity(
        type=np.dtype(np.float64), a_eln=dict(component='NumberEditQuantity'))

    minimum_fe = Quantity(
        type=np.dtype(np.float64), a_eln=dict(component='NumberEditQuantity'))

    maximum_fe = Quantity(
        type=np.dtype(np.float64), a_eln=dict(component='NumberEditQuantity'))

    def normalize(self, archive, logger):
        self.mean_fe = np.mean(self.faradaic_efficiency)
        self.minimum_fe = np.min(self.faradaic_efficiency)
        self.maximum_fe = np.max(self.faradaic_efficiency)
        self.variance_fe = np.var(self.faradaic_efficiency)


class PotentiometryGasChromatographyResults(ArchiveSection):

    total_flow_rate = Quantity(
        type=np.dtype(
            np.float64),
        shape=['*'],
        unit=('ml/minute'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='ml/minute',
            props=dict(minValue=0)
        ))

    gas_results = SubSection(
        section_def=GasFEResults, repeats=True)

    total_fe = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        description='Total faradaic efficiency specified in %')


class PotentiometryGasChromatographyMeasurement(BaseMeasurement):

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    properties = SubSection(
        section_def=NECCExperimentalProperties)

    gaschromatographies = SubSection(
        section_def=GasChromatographyOutput, repeats=True)

    potentiometry = SubSection(
        section_def=PotentiostatOutput)

    thermocouple = SubSection(
        section_def=ThermocoupleOutput)

    fe_results = SubSection(
        section_def=PotentiometryGasChromatographyResults)

    def normalize(self, archive, logger):
        super(PotentiometryGasChromatographyMeasurement, self).normalize(archive, logger)
