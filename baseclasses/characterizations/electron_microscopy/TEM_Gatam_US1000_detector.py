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
    SubSection)
from nomad.datamodel.data import ArchiveSection

from .microscope import TEMMicroscopeTechnique, MicroscopeConfiguration2, Image

from . import get_parameter


class HighLevel(ArchiveSection):
    binning = Quantity(
        type=np.dtype(np.float64),
        shape=[2],
        a_eln=dict(component='NumberEditQuantity'))

    ccd_read_area = Quantity(
        type=np.dtype(np.float64),
        shape=[4],
        a_eln=dict(component='NumberEditQuantity'))

    number_of_frame_shutters = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity'))

    processing = Quantity(
        type=str, a_eln=dict(
            component='EnumEditQuantity', props=dict(
                suggestions=["Gain Normalized"])))


class ReferenceImage(ArchiveSection):
    dark_mean = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity'))

    dark_standard_deviation = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity'))


class GatamScan(Image):

    pixel_size = Quantity(
        type=np.dtype(np.float64),
        unit="um",
        shape=[2],
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='um'))

    bias = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity'))

    dark_current = Quantity(
        type=np.dtype(np.float64),
        unit="1/s",
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='1/s'))

    dark_level = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity'))

    maximum_value = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity'))

    minimum_value = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity'))

    saturation_level = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity'))

    scale = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity'))

    microscope_configuration = SubSection(section_def=MicroscopeConfiguration2)
    high_level = SubSection(section_def=HighLevel)
    reference_image = SubSection(section_def=ReferenceImage)


class TEM_Gatam_US1000(TEMMicroscopeTechnique):

    @staticmethod
    def get_data(file_name):
        if file_name.lower().endswith(".dm3"):

            import hyperspy.api as hs
            try:
                dm3_file = hs.load(file_name)
                high_level = HighLevel(binning=get_parameter(["ImageList",
                                                              "TagGroup0",
                                                              "ImageTags",
                                                              "Acquisition",
                                                              "Parameters",
                                                              "High Level",
                                                              "Binning"],
                                                             dm3_file.original_metadata),
                                       ccd_read_area=get_parameter(["ImageList",
                                                                    "TagGroup0",
                                                                    "ImageTags",
                                                                    "Acquisition",
                                                                    "Parameters",
                                                                    "High Level",
                                                                    "CCD Read Area"],
                                                                   dm3_file.original_metadata),
                                       number_of_frame_shutters=get_parameter(["ImageList",
                                                                               "TagGroup0",
                                                                               "ImageTags",
                                                                               "Acquisition",
                                                                               "Parameters",
                                                                               "High Level",
                                                                               "Number Of Frame Shutters"],
                                                                              dm3_file.original_metadata),
                                       processing=get_parameter(["ImageList",
                                                                 "TagGroup0",
                                                                 "ImageTags",
                                                                 "Acquisition",
                                                                 "Parameters",
                                                                 "High Level",
                                                                 "Processing"],
                                                                dm3_file.original_metadata))

                reference_image = ReferenceImage(
                    dark_mean=get_parameter(
                        [
                            "ImageList",
                            "TagGroup0",
                            "ImageTags",
                            "Acquisition",
                            "Frame",
                            "Reference Images",
                            "Dark",
                            "Mean (counts)"],
                        dm3_file.original_metadata),
                    dark_standard_deviation=get_parameter(
                        [
                            "ImageList",
                            "TagGroup0",
                            "ImageTags",
                            "Acquisition",
                            "Frame",
                            "Reference Images",
                            "Dark",
                            "Standard Deviation (counts)"],
                        dm3_file.original_metadata),
                )

                microscope_configuration = MicroscopeConfiguration2(
                    x_value=get_parameter(["Acquisition_instrument", "SEM", "Stage", "x"], dm3_file.metadata),
                    y_value=get_parameter(["Acquisition_instrument", "SEM", "Stage", "y"], dm3_file.metadata),
                    z_value=get_parameter(["Acquisition_instrument", "SEM", "Stage", "z"], dm3_file.metadata),
                    alpha_tilt=get_parameter(["CZ_SEM", "ap_stage_at_t"], dm3_file.original_metadata, 1),
                    beta_tilt=get_parameter(["CZ_SEM", "ap_stage_at_m"], dm3_file.original_metadata, 1)
                )

                image_section = GatamScan(
                    file_name=os.path.basename(file_name),
                    pixel_size=get_parameter(["ImageList", "TagGroup0", "ImageTags", "Acquisition", "Device", "CCD", "Pixel Size (um)"], dm3_file.original_metadata),
                    bias=get_parameter(["ImageList", "TagGroup0", "ImageTags", "Acquisition", "Frame", "Intensity", "Range", "Bias (counts)"], dm3_file.original_metadata),
                    dark_current=get_parameter(["ImageList", "TagGroup0", "ImageTags", "Acquisition", "Frame", "Intensity", "Range", "Dark Current (counts/s)"], dm3_file.original_metadata),
                    dark_level=get_parameter(["ImageList", "TagGroup0", "ImageTags", "Acquisition", "Frame", "Intensity", "Range", "Dark Level (counts)"], dm3_file.original_metadata),
                    maximum_value=get_parameter(["ImageList", "TagGroup0", "ImageTags", "Acquisition", "Frame", "Intensity", "Range", "Maximum Value (counts)"], dm3_file.original_metadata),
                    minimum_value=get_parameter(["ImageList", "TagGroup0", "ImageTags", "Acquisition", "Frame", "Intensity", "Range", "Minimum Value (counts)"], dm3_file.original_metadata),
                    saturation_level=get_parameter(["ImageList", "TagGroup0", "ImageTags", "Acquisition", "Frame", "Intensity", "Range", "Saturation Level (counts)"], dm3_file.original_metadata),
                    scale=get_parameter(["ImageList", "TagGroup0", "ImageData", "Calibrations", "Brightness", "Scale"], dm3_file.original_metadata),
                    high_level=high_level,
                    microscope_configuration=microscope_configuration,
                    reference_image=reference_image
                )
                return image_section

            except Exception as e:
                print(e)
                return None

    def normalize(self, archive, logger):
        super(TEM_Gatam_US1000, self).normalize(archive, logger)
