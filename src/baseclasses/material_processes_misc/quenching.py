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
        links = ['https://purl.archive.org/tfsco/TFSCO_00001052'],
        label_quantity='name')
    name = Quantity(type=str)

    anti_solvent = Quantity(
        links = ['https://purl.archive.org/tfsco/TFSCO_00000026'],
        type=Reference(Chemical.m_def),
        a_eln=dict(component='ReferenceEditQuantity'))

    anti_solvent_2 = SubSection(
        section_def=PubChemPureSubstanceSection)

    anti_solvent_volume = Quantity( 
        links = ['http://purl.obolibrary.org/obo/PATO_0000918','https://purl.archive.org/tfsco/TFSCO_00002158'],
        type=np.dtype(
            np.float64),
        unit=('ml'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='ml',
            props=dict(
                minValue=0)))

    anti_solvent_dropping_time = Quantity(
        links = ['https://purl.archive.org/tfsco/TFSCO_00002150','https://purl.archive.org/tfsco/TFSCO_00002151'],
        type=np.dtype(
            np.float64), unit=('s'), a_eln=dict(
            component='NumberEditQuantity', defaultDisplayUnit='s', props=dict(
                minValue=0)))

    anti_solvent_dropping_flow_rate = Quantity(
        links = ['https://purl.archive.org/tfsco/TFSCO_00005091','https://purl.archive.org/tfsco/TFSCO_00005094'],
        type=np.dtype(
            np.float64), unit=('ul/s'), a_eln=dict(
            component='NumberEditQuantity', defaultDisplayUnit='ul/s', props=dict(
                minValue=0)))

    anti_solvent_dropping_height = Quantity(
        links = ['https://purl.archive.org/tfsco/TFSCO_00005092','https://purl.archive.org/tfsco/TFSCO_00005093'],
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
        links = ['https://purl.archive.org/tfsco/TFSCO_00001077']
    )
    gas = Quantity(
        links = ['http://purl.obolibrary.org/obo/CHEBI_59999'],
        type=str,
        a_eln=dict(component='StringEditQuantity'))


class AirKnifeGasQuenching(GasQuenching):
    m_def = Section(
        links = ['https://purl.archive.org/tfsco/TFSCO_00005032'],
    )
    air_knife_pressure = Quantity(
        links = ['https://purl.archive.org/tfsco/TFSCO_00005021','https://purl.archive.org/tfsco/TFSCO_00005027'],
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
        links = ['https://purl.archive.org/tfsco/TFSCO_00005025','https://purl.archive.org/tfsco/TFSCO_00005026'],
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
        links = ['https://purl.archive.org/tfsco/TFSCO_00005024','https://purl.archive.org/tfsco/TFSCO_00005029'],
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
        links = ['https://purl.archive.org/tfsco/TFSCO_00005023','https://purl.archive.org/tfsco/TFSCO_00005028'],
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


class SpinCoatingGasQuenching(GasQuenching):
    pass
