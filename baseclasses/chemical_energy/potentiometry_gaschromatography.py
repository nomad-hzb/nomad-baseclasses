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


class ExperimentalProperties(ArchiveSection):

    experimental_setup_id = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity', label='Experimental Setup id'))

    experiment_id = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity', label='Experiment id'))

    user_id = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity', label='User id'))

    # TODO find possible values
    cell_type = Quantity(
        type=MEnum('', 'x'),
        shape=[],
        a_eln=dict(component='EnumEditQuantity'))

    has_reference_electrode = Quantity(
        type=bool,
        default=True,
        a_eln=dict(component='BoolEditQuantity')
    )

    # TODO find possible values
    reference_electrode_type = Quantity(
        type=MEnum('', 'x'),
        shape=[],
        a_eln=dict(component='EnumEditQuantity'))

    cathode_geometric_area = Quantity(
        type=np.dtype(np.float64),
        unit=('cm^2'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='cm^2'))

    cathode_id = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity', label='Cathode id'))

    anode_id = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity', label='Anode id'))

    # TODO find possible values
    membrane_type = Quantity(
        type=MEnum('', 'x'),
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

    # TODO find possible values
    anolyte_type = Quantity(
        type=MEnum('', 'x'),
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
        unit=('°C'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'))

    water_trap_volume = Quantity(
        type=np.dtype(np.float64),
        unit=('ml'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='ml'))

    # TODO find possible values
    feed_gas = Quantity(
        type=MEnum('', 'x'),
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
        a_eln=dict(component='StringEditQuantity'))

    chronoanalysis_method = Quantity(
        type=MEnum('Chronoamperometry (CA)', 'Chronopotentiometry (CP)'),
        shape=[],
        a_eln=dict(component='EnumEditQuantity'))

class GasChromatographyOutput(ArchiveSection):
    # TODO i decided to combine FID (Flame ionization detector) and TCD (thermal conductivity detector). Is this ok?
    # TODO also i wonder if i can model it like this in general since one experiment name includes data for up to 4 gas types

    experiment_name = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'))

    # TODO can i combine two columns to datetime?
    datetime = Quantity(
        type=Datetime,
        shape=['*'])

    gas_type = Quantity(
        type=MEnum('CO', 'CH4', 'C2H4', 'C2H6', 'H2', 'N2'),
        shape=[],
        a_eln=dict(component='EnumEditQuantity',))

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
                "label": "Working Electrode Potential (Ewe)", 'x': 'time', 'y': 'working_electrode_potential', 'layout': {
                'yaxis': {
                    "fixedrange": False}, 'xaxis': {
                    "fixedrange": False}}, "config": {
                "editable": True, "scrollZoom": True}}])

class ThermocoupleOutput(ArchiveSection):
    # TODO is sample rate 100 important here? maybe add time in s?
    time = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        unit='s')

    # TODO can i combine two columns in datetime?
    datetime = Quantity(
        type=Datetime,
        shape=['*'])

    # TODO unit is barg but barg is not defined in pint
    pressure = Quantity(
        type=np.dtype(
            np.float64), shape=['*'], unit='bar', a_plot=[
            {
                "label": "Pressure", 'x': 'time', 'y': 'pressure', 'layout': {
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

class GasFeResults(ArchiveSection):
    # TODO class name

    # names = co, ch4, c2h4, h2

    ppm = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        description='Specified in ppm')
    # TODO reference to GasChromatographyOutput?

    i = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        unit='mA')

    fe = Quantity(
        type=np.dtype(np.float64),
        description='Specified in %',
        shape=['*'])
    # TODO unit? seems to be always negative...



class Results(ArchiveSection):

    total_flow_rate = Quantity(
        type=np.dtype(
            np.float64),
        unit=('ml/minute'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='ml/minute',
            props=dict(minValue=0)
        ))

    gas_results = SubSection(
        section_def=GasFeResults, repeats=True)

    total_fe = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        description='Specified in %')
    # TODO unit? seems to be always negative...


class PotentiometryGasChromatographyMeasurement(BaseMeasurement):

    properties = SubSection(
        section_def=ExperimentalProperties)

    gaschromatographies = SubSection(
        section_def=GasChromatographyOutput, repeats=True)

    potentiometry = SubSection(
        section_def=PotentiostatOutput)

    thermocouple = SubSection(
        section_def=ThermocoupleOutput)

    results = SubSection(
        section_def=Results)

    def normalize(self, archive, logger):
        super(PotentiometryGasChromatographyMeasurement, self).normalize(archive, logger)
