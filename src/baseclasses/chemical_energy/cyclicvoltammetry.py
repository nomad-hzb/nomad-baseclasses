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
from nomad.metainfo import MEnum, Quantity, Section, SubSection

from .potentiostat_measurement import PotentiostatProperties
from .voltammetry import Voltammetry


class CVProperties(PotentiostatProperties):
    initial_potential = Quantity(
        links=['https://w3id.org/nfdi4cat/voc4cat_0007216'],
        type=np.dtype(np.float64),
        unit=('V'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='V'),
    )

    initial_potential_measured_against = Quantity(
        type=MEnum('Eoc', 'Eref'),
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
        ),
    )

    limit_potential_1 = Quantity(
        links=[
            'https://w3id.org/nfdi4cat/voc4cat_0007214',
            'https://w3id.org/nfdi4cat/voc4cat_0007215',
        ],
        type=np.dtype(np.float64),
        unit=('V'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='V'),
    )

    limit_potential_1_measured_against = Quantity(
        type=MEnum('Eoc', 'Eref'),
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
        ),
    )

    limit_potential_2 = Quantity(
        links=[
            'https://w3id.org/nfdi4cat/voc4cat_0007214',
            'https://w3id.org/nfdi4cat/voc4cat_0007215',
        ],
        type=np.dtype(np.float64),
        unit=('V'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='V'),
    )

    limit_potential_2_measured_against = Quantity(
        type=MEnum('Eoc', 'Eref'),
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
        ),
    )

    final_potential = Quantity(
        links=['https://w3id.org/nfdi4cat/voc4cat_0007217'],
        type=np.dtype(np.float64),
        unit=('V'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='V'),
    )

    final_potential_measured_against = Quantity(
        type=MEnum('Eoc', 'Eref'),
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
        ),
    )

    scan_rate = Quantity(
        links=['https://w3id.org/nfdi4cat/voc4cat_0007213'],
        type=np.dtype(np.float64),
        unit=('mV/s'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mV/s'),
    )

    step_size = Quantity(
        type=np.dtype(np.float64),
        unit=('mV'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mV'),
    )

    cycles = Quantity(
        links=['https://w3id.org/nfdi4cat/voc4cat_0007228'],
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity'),
    )

    open_circuit_potential = Quantity(
        links=['https://w3id.org/nfdi4cat/voc4cat_0007219'],
        type=np.dtype(np.float64),
        unit=('V'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='V'),
    )


class CyclicVoltammetry(Voltammetry):
    m_def = Section(links=['https://w3id.org/nfdi4cat/voc4cat_0000082'])

    properties = SubSection(section_def=CVProperties)

    def get_scan_rate(self):
        if self.cycles is None:
            return None
        if self.cycles[0].get('voltage') is None or self.cycles[0].get('time') is None:
            return None
        v = np.median(np.abs(np.diff(self.cycles[0].voltage)))
        t = np.median(np.abs(np.diff(self.cycles[0].time)))
        return v / t

    def set_calculated_properties(self):
        # This can be called if the parser does not read properties from the file.
        # We should not call this by default because it would break the "if not self.properties" logic of all
        # normalizers/parsers that set information from the raw files.
        if self.properties is None:
            self.properties = CVProperties()
        if self.properties.scan_rate is None:
            self.properties.scan_rate = self.get_scan_rate()

    def normalize(self, archive, logger):
        self.method = 'Cyclic Voltammetry'
        super().normalize(archive, logger)
