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
import os
from datetime import datetime
import pandas as pd


from nomad.metainfo import (
    Quantity,
    Section,
    SubSection,
    Datetime)
from nomad.datamodel.data import ArchiveSection

from .. import BaseMeasurement, SingleLibraryMeasurement, LibraryMeasurement


class ConductivityProperties(ArchiveSection):
    pass


class ConductivitySingleLibraryMeasurement(SingleLibraryMeasurement):
    m_def = Section(label_quantity='name',
                    a_eln=dict(properties=dict(
                        order=[
                            "name", "position_x_relative", "position_y_relative", "position_index", "position_x", "position_y"
                        ]))
                    )

    conductivity = Quantity(
        type=np.dtype(np.float64),
        unit=('ohm'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='ohm'))


class ConductivityMeasurementLibrary(LibraryMeasurement):
    '''UV vis Measurement'''

    m_def = Section(
        a_eln=dict(hide=['certified_values', 'certification_institute']))

    # properties = SubSection(
    #     section_def=ConductivityProperties)

    measurements = SubSection(
        section_def=ConductivitySingleLibraryMeasurement, repeats=True)

    def normalize(self, archive, logger):
        super(ConductivityMeasurementLibrary, self).normalize(archive, logger)
        self.method = "Conductivity Measurement Mapping"
