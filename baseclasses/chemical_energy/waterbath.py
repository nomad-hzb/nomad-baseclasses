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
    Reference,
    SubSection)
from nomad.datamodel.data import ArchiveSection

from .. import Deposition
from ..chemical import Solvent


class PMMARemoval(ArchiveSection):

    temperature = Quantity(
        type=np.dtype(
            np.float64),
        unit=('°C'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='°C'))

    solvent = Quantity(
        type=Reference(Solvent.m_def),
        shape=['*'],
        a_eln=dict(component='ReferenceEditQuantity'))


class WaterBath(Deposition):

    type_of_graphene = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=[
                    "Graphene on CU",
                    "Graphene on polymer Film"])))

    etching_time = Quantity(
        type=np.dtype(
            np.float64),
        unit=('minute'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='minute'))

    wash_volume = Quantity(
        type=np.dtype(
            np.float64),
        unit=('ml'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='ml'))

    flow_rate = Quantity(
        type=np.dtype(
            np.float64),
        unit=('ml/s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='ml/s'))

    time_in_vaccuum = Quantity(
        type=np.dtype(
            np.float64),
        unit=('minute'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='minute'))

    pmma_removal = SubSection(section_def=PMMARemoval)

    def normalize(self, archive, logger):
        super(WaterBath,
              self).normalize(archive, logger)

        self.method = "Water Bath"
