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
import numpy as np

from nomad.metainfo import (Quantity, SubSection)
from nomad.datamodel.data import ArchiveSection

from .voltammetry import Voltammetry


class OCVProperties(ArchiveSection):

    total_time = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        shape=[],
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='s'))

    sample_period = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        shape=[],
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='s'))

    stability = Quantity(
        type=np.dtype(np.float64),
        unit=('mV/s'),
        shape=[],
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mV/s'))

    sample_area = Quantity(
        type=np.dtype(np.float64),
        unit=('cm^2'),
        shape=[],
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='cm^2'))


class OpenCircuitVoltage(Voltammetry):

    properties = SubSection(
        section_def=OCVProperties)

    def normalize(self, archive, logger):
        super(OpenCircuitVoltage, self).normalize(archive, logger)
        self.method = "Open Circuit Voltage"

        if self.data_file:
            try:
                with archive.m_context.raw_file(self.data_file) as f:
                    if os.path.splitext(self.data_file)[-1] == ".DTA":
                        from nomad.datamodel.metainfo.eln.helper.gamry_parser import get_header_and_data
                        metadata, _ = get_header_and_data(filename=f.name)

                        if "CORPOT" in metadata["TAG"] and self.properties is None:
                            from nomad.datamodel.metainfo.eln.helper.gamry_archive import get_ocv_properties

                            properties = OCVProperties()
                            get_ocv_properties(metadata, properties)

                            self.properties = properties

            except Exception as e:
                logger.error(e)
