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
from nomad.metainfo import MEnum, Quantity, Section, SubSection

from .microscope import MicroscopeConfiguration2, TEMMicroscopeTechnique


class EDXMethod(ArchiveSection):
    pass


class ImagingMethod(EDXMethod):
    resolution = Quantity(
        type=MEnum(
            [
                '64x48',
                '128x96',
                '256x192',
                '512x384',
                '1024x768',
                '2048x1536',
                '4096x3072',
            ]
        ),
        unit='px^2',
        a_eln=dict(component='EnumEditQuantity', defaultDisplayUnit='px^2'),
    )

    frame_time_per_scan = Quantity(
        type=np.dtype(np.float64),
        unit='s',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='s'),
    )

    dwell_time = Quantity(
        type=np.dtype(np.float64),
        unit='us',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='us'),
    )

    number_of_frame = Quantity(
        type=np.dtype(np.float64), a_eln=dict(component='NumberEditQuantity')
    )


class EDXImagingMethod(ImagingMethod):
    pass


class LinescanMethod(EDXMethod):
    number_of_points_in_scan = Quantity(
        type=np.dtype(np.float64), a_eln=dict(component='NumberEditQuantity')
    )

    number_of_scans = Quantity(
        type=np.dtype(np.float64), a_eln=dict(component='NumberEditQuantity')
    )

    dwell_time_per_pixel = Quantity(
        type=np.dtype(np.float64),
        unit='s',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='s'),
    )


class EDXScan(ArchiveSection):
    m_def = Section(label_quantity='file_name')

    file_name = Quantity(type=str, a_eln=dict(component='StringEditQuantity'))

    low_energy_cutoff = Quantity(
        type=np.dtype(np.float64),
        unit='eV',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='eV'),
    )

    max_energy_cutoff = Quantity(
        type=np.dtype(np.float64),
        unit='keV',
        a_eln=dict(component='NumberEditQuantity'),
        defaultDisplayUnit='keV',
    )

    microscope_configuration = SubSection(section_def=MicroscopeConfiguration2)
    method = SubSection(section_def=EDXMethod)


class TEM_EDX(TEMMicroscopeTechnique):
    @staticmethod
    def get_data(file_name):
        if file_name.lower().endswith('.emsa'):
            return None

    images = SubSection(section_def=EDXScan, label_quantity='file_name')

    def normalize(self, archive, logger):
        super().normalize(archive, logger)
