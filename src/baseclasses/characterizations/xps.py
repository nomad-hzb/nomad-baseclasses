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
from nomad.metainfo import Quantity, Section, SubSection

from .. import BaseMeasurement, LibraryMeasurement


class XPSSpecsLabProdigyAnalyzerParameters(ArchiveSection):
    polar_angle = Quantity(type=np.dtype(np.float64), unit='degree')
    azimuth_angle = Quantity(type=np.dtype(np.float64), unit='degree')
    rotation_angle = Quantity(type=np.dtype(np.float64), unit='degree')
    coil_current = Quantity(type=np.dtype(np.float64), unit='A')
    bias_voltage_ions = Quantity(type=np.dtype(np.float64), unit='V')
    bias_voltage_electrons = Quantity(type=np.dtype(np.float64), unit='V')
    detector_voltage = Quantity(type=np.dtype(np.float64), unit='V')
    work_function = Quantity(type=np.dtype(np.float64))
    focus_displacement = Quantity(type=np.dtype(np.float64))
    l1 = Quantity(type=np.dtype(np.float64))


class XPSSpecsLabProdigySourceParameters(ArchiveSection):
    polar_angle = Quantity(type=np.dtype(np.float64), unit='degree')
    azimuth_angle = Quantity(type=np.dtype(np.float64), unit='degree')
    excitation_energy = Quantity(type=np.dtype(np.float64), unit='eV')
    device_state = Quantity(type=str)
    preset_name = Quantity(type=str)
    anode = Quantity(type=str)
    anode_voltage = Quantity(type=np.dtype(np.float64))
    anode_current = Quantity(type=np.dtype(np.float64))
    filament_current = Quantity(type=np.dtype(np.float64))
    filament_voltage = Quantity(type=np.dtype(np.float64))
    power = Quantity(type=np.dtype(np.float64))
    emission = Quantity(type=np.dtype(np.float64))
    arcs = Quantity(type=np.dtype(np.float64))
    lens_voltage = Quantity(type=np.dtype(np.float64))
    lens_current = Quantity(type=np.dtype(np.float64))
    focused = Quantity(type=str)
    settings_summary = Quantity(type=str)


class XPSSpecsLabProdigySettings(ArchiveSection):
    region = Quantity(type=str)
    calibration_file = Quantity(type=str)
    analyzer_lens_mode = Quantity(type=str)
    scan_variable = Quantity(type=str)
    step_size = Quantity(type=np.dtype(np.float64))
    dwell_time = Quantity(type=np.dtype(np.float64))
    excitation_energy = Quantity(type=np.dtype(np.float64))
    kinetic_energy = Quantity(type=np.dtype(np.float64))
    binding_energy = Quantity(type=np.dtype(np.float64))
    pass_energy = Quantity(type=np.dtype(np.float64))
    bias_voltage = Quantity(type=np.dtype(np.float64))
    detector_voltage = Quantity(type=np.dtype(np.float64))
    effective_work_function = Quantity(type=np.dtype(np.float64))
    iris_diameter = Quantity(type=np.dtype(np.float64))
    analyzer_slit = Quantity(type=str)
    analyzer_lens_voltage = Quantity(type=str)
    analyzer_parameters = SubSection(section_def=XPSSpecsLabProdigyAnalyzerParameters)
    source_parameters = SubSection(section_def=XPSSpecsLabProdigySourceParameters)


class XPS(BaseMeasurement):
    """XPS Measurement"""

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'),
    )

    def normalize(self, archive, logger):
        super().normalize(archive, logger)
        self.method = 'X-ray photoelectron spectroscopy'


class XPSLibrary(LibraryMeasurement):
    """XPS Measurement"""

    m_def = Section(a_eln=dict(hide=['certified_values', 'certification_institute']))

    def normalize(self, archive, logger):
        super().normalize(archive, logger)
        self.method = 'XPS'
