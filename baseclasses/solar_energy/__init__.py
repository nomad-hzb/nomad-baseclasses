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

from nomad.metainfo import (
    Quantity,
    Reference,
    Section,
    SectionProxy)

from nomad.datamodel.metainfo.eln import (
    Process,
    SampleID,
    ElnWithFormulaBaseSection,
    Measurement,
    ElnBaseSection)


from .jvmeasurement import JVMeasurement
from .mpp_tracking import MPPTracking
from .mpp_tracking_hysprint_custom import MPPTrackingHsprintCustom, SampleData, JVData, PixelData
from .plmeasurement import PLMeasurement
from .uvvismeasurement import UVvisMeasurement, UVvisData
from .eqemeasurement import EQEMeasurement
from .time_resolved_photoluminescence import TimeResolvedPhotoluminescence, TRPLProperties
from .standardsample import StandardSampleSolarCell
from .substrate import Substrate
from .solarcellsample import SolcarCellSample, BasicSampleWithID
from .optical_microscope import OpticalMicroscope
