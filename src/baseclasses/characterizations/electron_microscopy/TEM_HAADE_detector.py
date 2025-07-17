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
from nomad.datamodel.data import ArchiveSection
from nomad.metainfo import Quantity, Section, SubSection

from baseclasses.helper.utilities import get_parameter

from .microscope import Image, MicroscopeConfiguration2, TEMMicroscopeTechnique


class Illumination(ArchiveSection):
    magnification = Quantity(
        type=np.dtype(np.float64), a_eln=dict(component='NumberEditQuantity')
    )

    illumination_index = Quantity(
        type=np.dtype(np.float64), a_eln=dict(component='NumberEditQuantity')
    )

    spot_size = Quantity(
        type=np.dtype(np.float64),
        unit='nm',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='nm'),
    )

    camera_length = Quantity(
        type=np.dtype(np.float64),
        unit='m',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='m'),
    )

    scan_rotation = Quantity(
        type=np.dtype(np.float64),
        unit='deg',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='deg'),
    )


class HAADEScan(Image):
    m_def = Section(label_quantity='file_name')

    file_name = Quantity(type=str, a_eln=dict(component='StringEditQuantity'))

    image_length = Quantity(
        type=np.dtype(np.float64),
        unit='px',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='px'),
    )

    image_width = Quantity(
        type=np.dtype(np.float64),
        unit='px',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='px'),
    )

    samples_per_pixel = Quantity(
        type=np.dtype(np.float64),
        unit='px',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='px'),
    )

    pixel_size = Quantity(
        type=np.dtype(np.float64),
        unit='nm',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='nm'),
    )

    frame_time = Quantity(
        type=np.dtype(np.float64),
        unit='minute',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='minute'),
    )

    noise_reduction = Quantity(
        type=str,
        a_eln=dict(component='EnumEditQuantity', props=dict(suggestions=['Frame Avg'])),
    )

    microscope_configuration = SubSection(
        section_def=MicroscopeConfiguration2, label_quantity='file_name'
    )
    illumination = SubSection(section_def=Illumination, label_quantity='file_name')


class TEM_HAADE(TEMMicroscopeTechnique):
    @staticmethod
    def get_data(file_name, original_file_name=None):
        if file_name.lower().endswith('.tif'):
            import hyperspy.api as hs

            try:
                tif_file = hs.load(file_name)
                illumination = Illumination(
                    magnification=get_parameter(
                        ['Acquisition_instrument', 'SEM', 'magnification'],
                        tif_file.metadata,
                    ),
                    illumination_index=get_parameter(
                        ['CZ_SEM', 'ap_ill_index'], tif_file.original_metadata, 1
                    ),
                    spot_size=get_parameter(
                        ['CZ_SEM', 'ap_spot_size'], tif_file.original_metadata, 1
                    ),
                    camera_length=get_parameter(
                        ['CZ_SEM', 'ap_camera_length'], tif_file.original_metadata, 1
                    ),
                    scan_rotation=get_parameter(
                        ['CZ_SEM', 'ap_scanrotation'], tif_file.original_metadata, 1
                    ),
                )

                microscope_configuration = MicroscopeConfiguration2(
                    x_value=get_parameter(
                        ['Acquisition_instrument', 'SEM', 'Stage', 'x'],
                        tif_file.metadata,
                    ),
                    y_value=get_parameter(
                        ['Acquisition_instrument', 'SEM', 'Stage', 'y'],
                        tif_file.metadata,
                    ),
                    z_value=get_parameter(
                        ['Acquisition_instrument', 'SEM', 'Stage', 'z'],
                        tif_file.metadata,
                    ),
                    alpha_tilt=get_parameter(
                        ['CZ_SEM', 'ap_stage_at_t'], tif_file.original_metadata, 1
                    ),
                    beta_tilt=get_parameter(
                        ['CZ_SEM', 'ap_stage_at_m'], tif_file.original_metadata, 1
                    ),
                )

                image_section = HAADEScan(
                    file_name=os.path.basename(file_name),
                    image_length=get_parameter(
                        ['ImageLength'], tif_file.original_metadata
                    ),
                    image_width=get_parameter(
                        ['ImageWidth'], tif_file.original_metadata
                    ),
                    samples_per_pixel=get_parameter(
                        ['SamplesPerPixel'], tif_file.original_metadata
                    ),
                    pixel_size=get_parameter(
                        ['CZ_SEM', 'ap_pixel_size'], tif_file.original_metadata, 1
                    ),
                    frame_time=get_parameter(
                        ['CZ_SEM', 'ap_frame_time'], tif_file.original_metadata, 1
                    ),
                    noise_reduction=get_parameter(
                        ['CZ_SEM', 'dp_noise_reduction'], tif_file.original_metadata, 1
                    ),
                    microscope_configuration=microscope_configuration,
                    illumination=illumination,
                )
                return image_section

            except Exception as e:
                print(e)
                return None

    def normalize(self, archive, logger):
        super().normalize(archive, logger)
