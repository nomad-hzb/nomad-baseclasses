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
from nomad.datamodel.data import ArchiveSection
from nomad.datamodel.metainfo.basesections import MeasurementResult
from nomad.metainfo import Quantity, Section, SubSection

from .. import BaseMeasurement, LibraryMeasurement


class NMRData(ArchiveSection):
    m_def = Section(label_quantity='name')

    name = Quantity(type=str)

    chemical_shift = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        description='This axis represents the frequency of the absorbed radiofrequency radiation by the atomic nuclei in the sample. The chemical shift value indicates the electronic environment of the nucleus within the molecule, providing information about the types of chemical bonds and functional groups present. The scale is typically expressed in parts per million (ppm) relative to a reference compound (often tetramethylsilane or TMS).',
    )

    intensity = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        description="This axis represents the intensity or strength of the NMR signal. The area under each peak on this axis is proportional to the number of nuclei contributing to that signal, which can be used to determine the relative abundance of different types of nuclei in the molecule. The y-axis can also be labeled as 'intensity' or 'signal intensity'",
    )


class NMR(BaseMeasurement):
    """Simple NMR Measurement"""

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'),
    )

    data = SubSection(section_def=NMRData)

    def normalize(self, archive, logger):
        self.method = 'NMR'
        super().normalize(archive, logger)
