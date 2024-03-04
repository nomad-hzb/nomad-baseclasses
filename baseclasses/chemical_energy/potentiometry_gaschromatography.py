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
        unit=('ppm'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='ppm'))

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
        unit=('minute'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='minute'))

    area = Quantity(
        type=np.dtype(np.float64),
        unit=('pA*minute'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='pA*minute'))

    ppm = Quantity(
        type=np.dtype(np.float64),
        unit=('ppm'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='ppm'))

class PotentiostatOutput(ArchiveSection):
    time = Quantity(
        type=Datetime,
        shape=['*'])

    current = Quantity(
        type=np.dtype(np.float64),
        unit='mA',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mA'))

    working_electrode_potential = Quantity(
        type=np.dtype(np.float64),
        unit='V',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='V'))

class ThermocoupleOutput(ArchiveSection):
    # TODO is sample rate 100 important here?

    # TODO can i combine two columns in datetime?
    datetime = Quantity(
        type=Datetime,
        shape=['*'])

    pressure = Quantity(
        type=np.dtype(np.float64),
        unit=('barg'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='barg'))

    temperature_cathode = Quantity(
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'))

    temperature_anode = Quantity(
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'))

class Results(ArchiveSection):
    #TODO class name?

    # injName ?? / experiment_name TODO

    current = Quantity(
        type=np.dtype(np.float64),
        unit=('mA'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mA'))

    cell_voltage = Quantity(
        type=np.dtype(np.float64),
        unit=('V'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='V'))
        # TODO check unit

    nitrogen = Quantity (
        type=np.dtype(np.float64),
        unit=('ppm'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='ppm'))

    total_flow_rate = Quantity(
        type=np.dtype(
            np.float64),
        unit=('ml/minute'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='ml/minute',
            props=dict(minValue=0)
        ))

    temperature_cathode = Quantity(
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'))

    temperature_anode = Quantity(
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'))

    pressure = Quantity(
        type=np.dtype(np.float64),
        unit=('barg'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='barg'))

    co = Quantity (
        type=np.dtype(np.float64),
        unit=('ppm'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='ppm'))

    co_i = Quantity(
        type=np.dtype(np.float64),
        unit=('mA'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mA'))

    co_fe = Quantity(
        type=np.dtype(np.float64),
        unit=('%'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='%'))
    # TODO unit? seems to be always negative...

    ch4 = Quantity(
        type=np.dtype(np.float64),
        unit=('ppm'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='ppm'))

    ch4_i = Quantity(
        type=np.dtype(np.float64),
        unit=('mA'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mA'))

    ch4_fe = Quantity(
        type=np.dtype(np.float64),
        unit=('%'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='%'))
    # TODO unit? seems to be always negative...

    c2h4 = Quantity(
        type=np.dtype(np.float64),
        unit=('ppm'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='ppm'))

    c2h4_i = Quantity(
        type=np.dtype(np.float64),
        unit=('mA'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mA'))

    c2h4_fe = Quantity(
        type=np.dtype(np.float64),
        unit=('%'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='%'))
    # TODO unit? seems to be always negative...

    h2 = Quantity(
        type=np.dtype(np.float64),
        unit=('ppm'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='ppm'))

    h2_i = Quantity(
        type=np.dtype(np.float64),
        unit=('mA'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mA'))

    h2_fe = Quantity(
        type=np.dtype(np.float64),
        unit=('%'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='%'))
    # TODO unit? seems to be always negative...

    total_fe = Quantity(
        type=np.dtype(np.float64),
        unit=('%'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='%'))
    # TODO unit? seems to be always negative...


class PotentiometryGasChromatographyMeasurement(BaseMeasurement):

    properties = SubSection(
        section_def=ExperimentalProperties)

    gaschromatography = SubSection(
        section_def=GasChromatographyOutput)

    potentiometry = SubSection(
        section_def=PotentiostatOutput)

    thermocouple = SubSection(
        section_def=ThermocoupleOutput)

    results = SubSection(
        section_def=Results)

    def normalize(self, archive, logger):
        super(PotentiometryGasChromatographyMeasurement, self).normalize(archive, logger)
