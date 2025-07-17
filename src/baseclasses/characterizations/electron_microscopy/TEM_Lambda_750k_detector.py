# pylint: disable=no-member
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
from nomad.metainfo import MEnum, Quantity

from .microscope import Image, TEMMicroscopeTechnique


class Lambda750kImage(Image):
    bit_depth_readout = Quantity(
        type=MEnum(['1', '6', '12', '24']), a_eln=dict(component='EnumEditQuantity')
    )
    counter_mode = Quantity(
        type=MEnum(['SINGLE', 'DUAL']), a_eln=dict(component='EnumEditQuantity')
    )
    charge_summing = Quantity(
        type=MEnum(['OFF', 'ON']), a_eln=dict(component='EnumEditQuantity')
    )
    number_of_frames = Quantity(
        type=np.dtype(np.float64), a_eln=dict(component='NumberEditQuantity')
    )
    shutter_time = Quantity(
        type=np.dtype(np.float64),
        unit='ms',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='ms'),
    )
    thresholds = Quantity(
        type=np.dtype(np.float64),
        unit='keV',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='keV'),
    )
    trigger_mode = Quantity(
        type=MEnum(['SOFTWARE', 'EXT_SEQUENCE', 'EXT_FRAMES']),
        a_eln=dict(component='EnumEditQuantity'),
    )
    saturation_value = Quantity(
        type=np.dtype(np.float64), a_eln=dict(component='NumberEditQuantity')
    )
    sensor_material = Quantity(type=str, default='Si')
    sensor_thickness = Quantity(type=np.dtype(np.float64), default=500.0)
    threshold_energy = Quantity(
        type=np.dtype(np.float64),
        unit='eV',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='eV'),
    )
    trigger_dead_time = Quantity(
        type=np.dtype(np.float64),
        unit='ms',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='ms'),
    )
    trigger_delay_time = Quantity(
        type=np.dtype(np.float64),
        unit='ms',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='ms'),
    )
    type_type = Quantity(type=str, default='Hybrid Pixel')
    x_pixel_size = Quantity(type=np.dtype(np.float64), default=55, unit='um')
    y_pixel_size = Quantity(type=np.dtype(np.float64), default=55, unit='um')

    data_integrated = Quantity(type=np.dtype(np.float64), shape=['*', '*'])


class TEM_lambda750k(TEMMicroscopeTechnique):
    gain_mode = Quantity(
        type=MEnum(['superlow', 'low', 'high', 'superhigh']),
        a_eln=dict(component='EnumEditQuantity'),
    )

    @staticmethod
    def get_data(file_name, original_file_name=None):
        if file_name.lower().endswith('.nxs'):
            import h5py

            try:
                nxs_file = h5py.File(file_name, 'r')

                # data = np.array(nxs_file['/entry/instrument/detector/data'][()])
                # ones = np.ones(data.shape[0])

                # data_integrated = np.einsum('i,ijk->jk',ones,data)

                image_section = Lambda750kImage(
                    file_name=os.path.basename(file_name),
                    bit_depth_readout=str(
                        nxs_file['/entry/instrument/detector/bit_depth_readout'][()]
                    ),
                    counter_mode=nxs_file[
                        '/entry/instrument/detector/collection/counter_mode'
                    ][()].decode('utf-8'),
                    charge_summing=nxs_file[
                        '/entry/instrument/detector/collection/charge_summing'
                    ][()].decode('utf-8'),
                    number_of_frames=nxs_file[
                        '/entry/instrument/detector/collection/number_of_frames'
                    ][()],
                    shutter_time=nxs_file[
                        '/entry/instrument/detector/collection/shutter_time'
                    ][()],
                    thresholds=nxs_file[
                        '/entry/instrument/detector/collection/thresholds'
                    ][()],
                    trigger_mode=nxs_file[
                        '/entry/instrument/detector/collection/trigger_mode'
                    ][()].decode('utf-8'),
                    saturation_value=nxs_file[
                        '/entry/instrument/detector/saturation_value'
                    ][()],
                    sensor_material=nxs_file[
                        '/entry/instrument/detector/sensor_material'
                    ][()].decode('utf-8'),
                    sensor_thickness=nxs_file[
                        '/entry/instrument/detector/sensor_thickness'
                    ][()],
                    threshold_energy=nxs_file[
                        '/entry/instrument/detector/threshold_energy'
                    ][()],
                    trigger_dead_time=nxs_file[
                        '/entry/instrument/detector/trigger_dead_time'
                    ][()],
                    trigger_delay_time=nxs_file[
                        '/entry/instrument/detector/trigger_delay_time'
                    ][()],
                    type_type=nxs_file['/entry/instrument/detector/type'][()].decode(
                        'utf-8'
                    ),
                    x_pixel_size=nxs_file['/entry/instrument/detector/x_pixel_size'][
                        ()
                    ],
                    y_pixel_size=nxs_file['/entry/instrument/detector/y_pixel_size'][
                        ()
                    ],
                    # data_integrated=data_integrated,
                )
                print(type(image_section))
                return image_section
            except Exception as e:
                print(e)
                return None

    def normalize(self, archive, logger):
        super().normalize(archive, logger)
