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

from nomad.datamodel.metainfo.eln import SolarCellEQE
from .. import MeasurementOnSample


class SolarCellEQECustom(SolarCellEQE):

    header_lines = Quantity(
        type=np.dtype(np.int64),
        description="""
        Number of header lines in the file. Edit in case your file has a header.
        """,
        a_eln=dict(component='NumberEditQuantity'))


class EQEMeasurement(MeasurementOnSample):
    '''Eqe Measurement'''
    eqe_data = SubSection(
        section_def=SolarCellEQECustom,
        repeats=True)

    def normalize(self, archive, logger):
        self.method = "EQE Measurement"
        super(EQEMeasurement, self).normalize(archive, logger)
