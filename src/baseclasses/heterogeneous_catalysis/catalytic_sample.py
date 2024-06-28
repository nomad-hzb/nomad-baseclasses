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

from nomad.metainfo import (SubSection, Quantity)
from nomad.datamodel.metainfo.eln import SampleID
from nomad.datamodel.data import ArchiveSection

from baseclasses.chemical_energy import CESample


class Grid(ArchiveSection):

    number_of_cells = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(
            component='NumberEditQuantity',
        ))

    cell_area = Quantity(
        type=np.dtype(np.float64),
        unit=("cm**2"),
        a_eln=dict(
            component='NumberEditQuantity', defaultDisplayUnit='cm**2',
        ))

    width = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(
            component='NumberEditQuantity',
        ))

    height = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(
            component='NumberEditQuantity',
        ))


class CatalyticSample(CESample):

    surface_area = Quantity(
        type=np.dtype(np.float64),
        unit=("cm**2"),
        a_eln=dict(
            component='NumberEditQuantity', defaultDisplayUnit='cm**2',
        ))

    mass = Quantity(
        type=np.dtype(np.float64),
        unit=("mg"),
        a_eln=dict(
            component='NumberEditQuantity', defaultDisplayUnit='mg',
        ))

    sample_id = SubSection(
        section_def=SampleID)

    def normalize(self, archive, logger):
        super(CatalyticSample, self).normalize(archive, logger)


class CatalyticSampleWithGrid(CatalyticSample):

    grid_information = SubSection(
        section_def=Grid)

    def normalize(self, archive, logger):
        super(CatalyticSampleWithGrid, self).normalize(archive, logger)
