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

from nomad.metainfo import (
    Quantity,
    Section,
    Reference, SubSection)
from nomad.datamodel.data import ArchiveSection

from ..chemical import Chemical
from nomad.datamodel.metainfo.basesections import PubChemPureSubstanceSection


class Quenching(ArchiveSection):
    pass


class AntiSolventQuenching(Quenching):

    m_def = Section(
        links=['https://purl.archive.org/tfsco/TFSCO_00001052'],
        label_quantity='name')
    name = Quantity(type=str)

    anti_solvent = Quantity(
        links=['https://purl.archive.org/tfsco/TFSCO_00000026'],
        type=Reference(Chemical.m_def),
        a_eln=dict(component='ReferenceEditQuantity'))

    anti_solvent_2 = SubSection(
        section_def=PubChemPureSubstanceSection)

    anti_solvent_volume = Quantity(
        links=['http://purl.obolibrary.org/obo/PATO_0000918', 'https://purl.archive.org/tfsco/TFSCO_00002158'],
        type=np.dtype(
            np.float64),
        unit=('ml'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='ml',
            props=dict(
                minValue=0)))

    anti_solvent_dropping_time = Quantity(
        links=['https://purl.archive.org/tfsco/TFSCO_00002150', 'https://purl.archive.org/tfsco/TFSCO_00002151'],
        type=np.dtype(
            np.float64), unit=('s'), a_eln=dict(
            component='NumberEditQuantity', defaultDisplayUnit='s', props=dict(
                minValue=0)))

    anti_solvent_dropping_flow_rate = Quantity(
        links=['https://purl.archive.org/tfsco/TFSCO_00005091', 'https://purl.archive.org/tfsco/TFSCO_00005094'],
        type=np.dtype(
            np.float64), unit=('ul/s'), a_eln=dict(
            component='NumberEditQuantity', defaultDisplayUnit='ul/s', props=dict(
                minValue=0)))

    anti_solvent_dropping_height = Quantity(
        links=['https://purl.archive.org/tfsco/TFSCO_00005092', 'https://purl.archive.org/tfsco/TFSCO_00005093'],
        type=np.dtype(
            np.float64), unit=('mm'), a_eln=dict(
            component='NumberEditQuantity', defaultDisplayUnit='mm', props=dict(
                minValue=0)))

    def normalize(self, archive, logger):

        if self.anti_solvent and self.anti_solvent.name:
            if self.anti_solvent_volume:
                self.name = self.anti_solvent.name + \
                    ' ' + str(self.anti_solvent_volume)
            else:
                self.name = self.anti_solvent.name


class SpinCoatingAntiSolvent(AntiSolventQuenching):
    pass


class GasQuenching(Quenching):
    m_def = Section(
        links=['https://purl.archive.org/tfsco/TFSCO_00001077']
    )
    gas = Quantity(
        links=['http://purl.obolibrary.org/obo/CHEBI_59999'],
        type=str,
        a_eln=dict(component='StringEditQuantity'))


class GasQuenchingWithNozzle(GasQuenching):

    m_def = Section(
        links=['https://purl.archive.org/tfsco/TFSCO/TFSCO_00003300']
    )

    starting_delay = Quantity(
        links=['https://purl.archive.org/tfsco/TFSCO/TFSCO_00003301',
               'https://purl.archive.org/tfsco/TFSCO/TFSCO_00003312'],
        type=np.dtype(np.float64),
        unit=('s'),
        description=('Time Delay between starting the spin and the Gas Quenching.'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='s',
            props=dict(
                minValue=0)))

    flow_rate = Quantity(
        links=['https://purl.archive.org/tfsco/TFSCO_00002114', 'https://purl.archive.org/tfsco/TFSCO_00002108'],
        type=np.dtype(np.float64),
        unit=('ml/s'),
        description=('Volume Flow per time.'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='ml/s',
            props=dict(
                minValue=0)))

    height = Quantity(
        links=['https://purl.archive.org/tfsco/TFSCO/TFSCO_00003302',
               'https://purl.archive.org/tfsco/TFSCO/TFSCO_00003308'],
        type=np.dtype(np.float64),
        description=('Distance Nozzle-Sample.'),
        unit=('mm'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mm',
            props=dict(
                minValue=0)))

    duration = Quantity(
        links=['http://purl.obolibrary.org/obo/PATO_0001309', 'https://purl.archive.org/tfsco/TFSCO_00002006'],
        type=np.dtype(np.float64),
        description=('Time Duration of Quenching'),
        unit=('s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='s',
            props=dict(
                minValue=0)))

    pressure = Quantity(
        links=['http://purl.obolibrary.org/obo/PATO_0001025', 'https://purl.archive.org/tfsco/TFSCO_00005040'],
        type=np.dtype(np.float64),
        description=("Pressure on the line"),
        unit=('bar'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='bar',
            props=dict(
                minValue=0)))

    velocity = Quantity(
        links=['https://purl.archive.org/tfsco/TFSCO/TFSCO_00003313'],
        type=np.dtype(np.float64),
        description=("Speed of gas at the nozzle tip (Calculated from Flow and Nozzle Area)"),
        unit=('m/s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='m/s',
            props=dict(
                minValue=0)))

    nozzle_shape = Quantity(
        links=['https://purl.archive.org/tfsco/TFSCO/TFSCO_00003304'],
        type=str,
        description=('Description of the nozzle shape.'),
        a_eln=dict(
            component='StringEditQuantity'
        ))

    nozzle_size = Quantity(
        type=str,
        description=('Description of the nozzle size.'),
        a_eln=dict(
            component='StringEditQuantity'
        ))


class VacuumQuenching(Quenching):

    pressure = Quantity(
        type=np.dtype(np.float64),
        unit=('mbar'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mbar'))


class AirKnifeGasQuenching(GasQuenching):
    m_def = Section(
        links=['https://purl.archive.org/tfsco/TFSCO_00005032'],
    )
    air_knife_pressure = Quantity(
        links=['https://purl.archive.org/tfsco/TFSCO_00005021', 'https://purl.archive.org/tfsco/TFSCO_00005027'],
        type=np.dtype(
            np.float64),
        unit=('mbar'),
        description=('The pressure of the air knife gas.'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mbar',
            props=dict(
                minValue=0)))

    air_knife_speed = Quantity(
        links=['https://purl.archive.org/tfsco/TFSCO_00005025', 'https://purl.archive.org/tfsco/TFSCO_00005026'],
        type=np.dtype(
            np.float64),
        unit=('mm/s'),
        description=('The speed of the air knife moving over the sample.'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mm/s',
            props=dict(
                minValue=0)))

    air_knife_angle = Quantity(
        links=['https://purl.archive.org/tfsco/TFSCO_00005024', 'https://purl.archive.org/tfsco/TFSCO_00005029'],
        type=np.dtype(
            np.float64),
        unit=('degree'),
        description=('The angle of the air knife with respect to the sample, ie. 90° is straight above the sample.'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='degree',
            props=dict(
                minValue=0)))

    air_knife_distance_to_thin_film = Quantity(
        links=['https://purl.archive.org/tfsco/TFSCO_00005023', 'https://purl.archive.org/tfsco/TFSCO_00005028'],
        type=np.dtype(
            np.float64),
        description=('The distance of the air knife to the thin film.'),
        unit=('um'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='um',
            props=dict(
                minValue=0)))

    air_knife_time = Quantity(
        type=np.dtype(
            np.float64),
        description=('The time the air knife is on.'),
        unit=('s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='s',
            props=dict(
                minValue=0)))

    bead_volume = Quantity(
        type=np.dtype(
            np.float64),
        unit=('mm/s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mm/s',
            props=dict(
                minValue=0)))

    drying_speed = Quantity(
        type=np.dtype(
            np.float64),
        unit=('cm/minute'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='cm/minute',
            props=dict(
                minValue=0)))


class SpinCoatingGasQuenching(GasQuenching):
    pass
