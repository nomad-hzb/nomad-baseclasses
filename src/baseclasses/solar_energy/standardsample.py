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

from nomad.metainfo import (
    Quantity,
    Reference
)


from .substrate import Substrate
from .. import StandardSample
from nomad.datamodel.data import ArchiveSection


class SolarCellProperties(ArchiveSection):
    substrate = Quantity(
        type=Reference(Substrate.m_def),
        a_eln=dict(component='ReferenceEditQuantity'))

    architecture = Quantity(
        type=str,
        shape=[],
        description="""
            The cell architecture with respect to the direction of current flow and
            the order in which layers are deposited.
            The two most common are nip (also referred to as normal) and pin (also referred to as inverted)
            but there are also a few others, e.g. Back contacted.
            - *nip* architecture means that the electrons are collected at the substrate side.
            The typical example is in perovskite solar cells when a TiO2 electron selective contact is deposited
            between the perovskite and the substrate (e.g. SLG | FTO | TiO2-c | Perovskite | …)
            - *pin* architecture means that it instead is the holes that are collected at the substrate side. The typical example is when a PEDOT:PSS hole selective contact is deposited between the perovskite and the substrate (e.g. SLG | FTO | PEDOT:PSS |Perovskite | …)
        """,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=[
                    'Unknown',
                    'Pn-Heterojunction',
                    'Front contacted',
                    'Back contacted',
                    'pin',
                    'nip',
                    'Schottky'])))


class StandardSampleSolarCell(StandardSample):

    substrate = Quantity(
        type=Reference(Substrate.m_def),
        a_eln=dict(component='ReferenceEditQuantity'))

    architecture = Quantity(
        type=str,
        shape=[],
        description="""
            The cell architecture with respect to the direction of current flow and
            the order in which layers are deposited.
            The two most common are nip (also referred to as normal) and pin (also referred to as inverted)
            but there are also a few others, e.g. Back contacted.
            - *nip* architecture means that the electrons are collected at the substrate side.
            The typical example is in perovskite solar cells when a TiO2 electron selective contact is deposited
            between the perovskite and the substrate (e.g. SLG | FTO | TiO2-c | Perovskite | …)
            - *pin* architecture means that it instead is the holes that are collected at the substrate side. The typical example is when a PEDOT:PSS hole selective contact is deposited between the perovskite and the substrate (e.g. SLG | FTO | PEDOT:PSS |Perovskite | …)
        """,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=[
                    'Unknown',
                    'Pn-Heterojunction',
                    'Front contacted',
                    'Back contacted',
                    'pin',
                    'nip',
                    'Schottky'])))

    def normalize(self, archive, logger):
        super(StandardSampleSolarCell, self).normalize(archive, logger)
