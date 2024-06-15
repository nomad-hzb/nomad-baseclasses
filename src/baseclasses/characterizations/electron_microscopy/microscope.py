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

from nomad.metainfo import (
    Quantity,
    SubSection,
    MEnum,
    Reference,
    Section)
from nomad.datamodel.data import ArchiveSection

from .TEM_Session import TEM_Session
from nomad.datamodel.metainfo.eln import Entity
from baseclasses import BaseMeasurement


class TEMMicroscopeConfiguration(Entity):
    zeroloss_filtered = Quantity(
        type=MEnum([
            'True', 'False']),
        a_eln=dict(component='EnumEditQuantity'))
    slit_width = Quantity(
        type=np.dtype(np.float64),
        unit='eV',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='eV'))
    condensor_aperture = Quantity(
        type=MEnum([
            'no', '10 um', '20 um', '200 um']),
        unit='A',
        a_eln=dict(component='EnumEditQuantity'))
    scale = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity'))
    magnification = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity'))
    illumination_index = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity', minValue=0, maxValue=25))


class SEMMicroscopeConfiguration(Entity):
    pass


class MicroscopeConfiguration2(ArchiveSection):

    x_value = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity'))

    y_value = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity'))

    z_value = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity'))

    alpha_tilt = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity'))

    beta_tilt = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity'))


class Image(ArchiveSection):
    m_def = Section(label_quantity='file_name')

    file_name = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'))


class MicroscopeTechnique(BaseMeasurement):

    ''' Any physical process applied to the sample. '''
    name = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'))

    external_sample_url = Quantity(
        type=str,
        a_eln=dict(component='URLEditQuantity'))

    detector_data_folder = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'))

    detector_data = Quantity(
        type=str,
        shape=['*'],
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    description = Quantity(
        type=str,
        a_eln=dict(component='RichTextEditQuantity'))

    images = SubSection(
        section_def=Image,
        label_quantity='file_name',
        repeats=True)

    @staticmethod
    def get_data(file_name):
        pass

    def normalize(self, archive, logger):
        super(MicroscopeTechnique, self).normalize(archive, logger)

        if not self.detector_data and not self.detector_data_folder:
            return
        imgs = []
        if self.detector_data:
            imgs.extend(self.detector_data)

        if self.detector_data_folder:
            # detector_data_folder = self.detector_data_folder
            detector_data_folder = os.path.join(
                "/measurement_data", self.detector_data_folder)
            for file in os.listdir(detector_data_folder):
                file_with_path = os.path.join(detector_data_folder, file)
                dst_path = archive.m_context.upload_files._raw_dir.os_path
                if file not in os.listdir(dst_path):
                    import shutil
                    shutil.copyfile(
                        file_with_path, os.path.join(
                            dst_path, file))

            imgs.extend(os.listdir(detector_data_folder))

        # process images
        # self.detector_data = imgs
        for image in imgs:
            with archive.m_context.raw_file(image) as f:
                processed = False
                for img in self.images:
                    if img.file_name == image:
                        processed = True
                if not processed:
                    image_data = self.get_data(f.name)

                    if image_data:
                        if not self.images:
                            self.images = []
                        self.images.section_def = image_data.m_def
                        self.images.append(image_data)


class TEMMicroscopeTechnique(MicroscopeTechnique):

    session = Quantity(
        type=Reference(TEM_Session.m_def),
        a_eln=dict(component='ReferenceEditQuantity'))

    microscope_configuration = Quantity(
        type=Reference(TEMMicroscopeConfiguration.m_def),
        a_eln=dict(component='ReferenceEditQuantity'))

    def normalize(self, archive, logger):
        super(TEMMicroscopeTechnique, self).normalize(archive, logger)


class SEMMicroscopeTechnique(MicroscopeTechnique):

    # microscope_configuration = Quantity(
    #     type=Reference(SEMMicroscopeConfiguration.m_def),
    #     a_eln=dict(component='ReferenceEditQuantity'))

    def normalize(self, archive, logger):
        super(SEMMicroscopeTechnique, self).normalize(archive, logger)


class OpticalMicroscopeTechnique(MicroscopeTechnique):

    # microscope_configuration = Quantity(
    #     type=Reference(SEMMicroscopeConfiguration.m_def),
    #     a_eln=dict(component='ReferenceEditQuantity'))

    def normalize(self, archive, logger):
        super(OpticalMicroscopeTechnique, self).normalize(archive, logger)
