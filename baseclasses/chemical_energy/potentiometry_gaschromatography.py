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

from nomad.metainfo import (Quantity, SubSection, Datetime)

from .. import BaseMeasurement

from nomad.datamodel.data import ArchiveSection


class ExperimentalProperties(ArchiveSection):
    # TODO add tab2 from table

class GasChromatographyOutput(ArchiveSection):
    # TODO FID (Flammenionisationsdetektor) als name nutzen? oder diese info aus tabelle verwerfen?
    # TODO experiment name?

    # TODO can i combine to columns to datetime?
    datetime = Quantity(
        type=Datetime,
        shape=['*'])

    # TODO how to model next 4 entries for CO, CH4, C2H4, C2H6
    gas_type = Quantity(
        type=MEnum('CO', 'CH4', 'C2H4', 'C2H6'),
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
        ))

    # TODO meaning and unit of (Retentionszeit) rt =

    # TODO unit (scheint Peakarea zu sein) area =

    ppm = Quantity (
        type=np.dtype(np.float64),
        unit=('ppm'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='ppm'))

class PotentiostatOutput(ArchiveSection):
    time = Quantity(
        type=Datetime,
        shape=['*'])

    name = Quantity(
        type=np.dtype(np.float64),
        unit='<I>/mA',
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='<I>/mA'
        ))
    # TODO change name and probably also unit

    name2 = Quantity(
        type=np.dtype(np.float64),
        unit='Ewe/V',
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='Ewe/V'
        ))
    # TODO change name and probably also unit

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
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='°C'))

    temperature_anode = Quantity(
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='°C'))

    #TODO chn 1 events?



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
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='V'))
        # TODO check unit

    nitrogen = Quantity (
        type=np.dtype(np.float64),
        unit=('ppm'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='ppm'))

    total_flow_rate = Quantity(
        type = np.dtype(
            np.float64),
        unit = ('ml/minute'),
        a_eln = dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='ml/minute', props=dict(minValue=0)))

    temperature_cathode = Quantity(
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='°C'))

    temperature_anode = Quantity(
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='°C'))

    pressure = Quantity(
        type=np.dtype(np.float64),
        unit=('barg'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='barg'))

    co = Quantity (
        type=np.dtype(np.float64),
        unit=('ppm'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='ppm'))

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
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='ppm'))

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
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='ppm'))

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
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='ppm'))

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


class PotentioGasChromaMeasurement(BaseMeasurement):
# TODO class name?

    properties = SubSection(
        section_def=ExperimentalProperties)

    results = SubSection(
        section_def=Results)

    def normalize(self, archive, logger):
        super(PotentioGasChromaMeasurement, self).normalize(archive, logger)


