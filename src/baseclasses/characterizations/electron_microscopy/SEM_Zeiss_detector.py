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
from nomad.metainfo import Datetime, MEnum, Quantity, Section

from baseclasses.helper.utilities import get_parameter

from .microscope import Image, SEMMicroscopeTechnique


class SEMImage_Zeiss_Detector(Image):
    m_def = Section(label_quantity='file_name')

    detector = Quantity(
        type=MEnum([
            'SE2', 'InLens']),
        a_eln=dict(component='EnumEditQuantity'))

    column_mode = Quantity(
        type=str,
        a_eln=dict(component='EnumEditQuantity', props=dict(
            suggestions=[
                'Analytic', 'High Resoultion', 'Fish Eye'])))

    datetime_of_image = Quantity(
        type=Datetime,
        description='The date and time when the image was take.',
        a_eln=dict(component='DateTimeEditQuantity'))

    pixel_size = Quantity(
        type=np.dtype(np.float64),
        unit="nm",
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='nm'))

    store_resolution_x = Quantity(
        type=np.dtype(np.int64),
        unit="px",
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='px'))

    store_resolution_y = Quantity(
        type=np.dtype(np.int64),
        unit="px",
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='px'))

    stage_at_x = Quantity(
        type=np.dtype(np.float64),
        unit="mm",
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mm'))

    stage_at_y = Quantity(
        type=np.dtype(np.float64),
        unit="mm",
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mm'))

    stage_at_z = Quantity(
        type=np.dtype(np.float64),
        unit="mm",
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mm'))

    tilt = Quantity(type=np.dtype(np.float64), unit="degree", a_eln=dict(
        component='NumberEditQuantity', defaultDisplayUnit='degree'))

    rotation = Quantity(
        type=np.dtype(
            np.float64),
        unit="degree",
        a_eln=dict(
            component='NumberEditQuantity',
             defaultDisplayUnit='degree'))

    iprobe = Quantity(
        type=np.dtype(np.float64),
        unit="nA",
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='nA'))

    beam_current = Quantity(
        type=np.dtype(np.float64),
        unit="uA",
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='uA'))

    beam_energy = Quantity(
        type=np.dtype(np.float64),
        unit="kV",
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='kV'))

    magnification = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'))

    working_distance = Quantity(
        type=np.dtype(np.float64),
        unit="mm",
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mm'))

    dwell_time = Quantity(
        type=np.dtype(np.float64),
        unit="s",
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='s'))

    image_preview = Quantity(
        type=str,
        # a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))


class SEM_Microscope_Merlin(SEMMicroscopeTechnique):

    @staticmethod
    def get_data(file_name):
        if file_name.lower().endswith(".tif"):
            from datetime import datetime

            import hyperspy.api as hs
            try:
                tif_file = hs.load(file_name)

                png_file = os.path.splitext(file_name)[0] + '_preview.png'
                tif_file.save(png_file, overwrite=True)

                store_resolution = get_parameter(
                    ["CZ_SEM", "dp_image_store"], tif_file.original_metadata, 1)
                date = get_parameter(
                    ["CZ_SEM", "ap_date"], tif_file.original_metadata, 1)
                time = get_parameter(
                    ["CZ_SEM", "ap_time"], tif_file.original_metadata, 1)

                datetime_str = f"{date} {time}"
                datetime_object = datetime.strptime(
                    datetime_str, '%d %b %Y %H:%M:%S')

                store_resolution_x_val, store_resolution_y_val = store_resolution.split(
                    "*")
                image_section = SEMImage_Zeiss_Detector(
                    file_name=os.path.basename(file_name),
                    detector=get_parameter(
                        ["CZ_SEM", "dp_detector_type"], tif_file.original_metadata, 1),
                    column_mode=get_parameter(
                        ["CZ_SEM", "dp_column_mode"], tif_file.original_metadata, 1),
                    pixel_size=get_parameter(
                        ["CZ_SEM", "ap_pixel_size"], tif_file.original_metadata, 1),
                    datetime_of_image=datetime_object.strftime(
                        "%Y-%m-%d %H:%M:%S.%f"),
                    store_resolution_x=int(store_resolution_x_val.strip()),
                    store_resolution_y=int(store_resolution_y_val.strip()),
                    stage_at_x=get_parameter(
                        ["CZ_SEM", "ap_stage_at_x"], tif_file.original_metadata, 1),
                    stage_at_y=get_parameter(
                        ["CZ_SEM", "ap_stage_at_y"], tif_file.original_metadata, 1),
                    stage_at_z=get_parameter(
                        ["CZ_SEM", "ap_stage_at_z"], tif_file.original_metadata, 1),
                    tilt=get_parameter(
                        ["CZ_SEM", "ap_stage_at_t"], tif_file.original_metadata, 1),
                    rotation=get_parameter(
                        ["CZ_SEM", "ap_stage_at_r"], tif_file.original_metadata, 1),
                    iprobe=get_parameter(
                        ["CZ_SEM", "ap_iprobe"], tif_file.original_metadata, 1),
                    beam_current=get_parameter(
                        ["CZ_SEM", "ap_beam_current"], tif_file.original_metadata, 1),
                    beam_energy=get_parameter(
                        ["CZ_SEM", "ap_actualkv"], tif_file.original_metadata, 1),
                    dwell_time=get_parameter(
                        ["CZ_SEM", "dp_dwell_time"], tif_file.original_metadata, 1),
                    magnification=get_parameter(
                        ["CZ_SEM", "ap_mag"], tif_file.original_metadata, 1),
                    working_distance=get_parameter(
                        ["CZ_SEM", "ap_wd"], tif_file.original_metadata, 1),
                    image_preview=os.path.basename(png_file)
                )
                return image_section

            except Exception as e:
                print(e)
                return None

    def normalize(self, archive, logger):
        super().normalize(archive, logger)
