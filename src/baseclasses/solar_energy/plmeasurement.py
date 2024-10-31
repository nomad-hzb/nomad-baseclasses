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
import math

import numpy as np
from nomad.datamodel.data import ArchiveSection
from nomad.metainfo import Quantity, Section, SubSection
from nomad.units import ureg

from .. import BaseMeasurement, LibraryMeasurement, SingleLibraryMeasurement


class PLDataSimple(ArchiveSection):
    m_def = Section(label_quantity='name')

    name = Quantity(
        type=str)

    intensity = Quantity(
        type=np.dtype(
            np.float64), shape=['*'])


class PLData(PLDataSimple):
    wavelength = Quantity(
        type=np.dtype(
            np.float64), unit=('nm'), shape=['*'])


class PLProperties(ArchiveSection):

    integration_time = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='s'))

    number_of_averages = Quantity(
        type=np.dtype(np.int64),
        a_eln=dict(component='NumberEditQuantity'))

    spot_size = Quantity(
        type=np.dtype(np.float64),
        unit=('mm'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mm'))

    wavelength_start = Quantity(
        type=np.dtype(np.float64),
        unit=('nm'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='nm'))

    wavelength_stop = Quantity(
        type=np.dtype(np.float64),
        unit=('nm'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='nm'))

    wavelength_step_size = Quantity(
        type=np.dtype(np.float64),
        unit=('nm'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='nm'))

    temperature = Quantity(
        type=np.dtype(np.float64),
        unit=('K'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'))

    lamp = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'))


class PLPropertiesLibrary(ArchiveSection):

    integration_time = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='s'))

    number_of_averages = Quantity(
        type=np.dtype(np.int64),
        a_eln=dict(component='NumberEditQuantity'))

    spot_size = Quantity(
        type=np.dtype(np.float64),
        unit=('mm'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mm'))

    long_pass_filter = Quantity(
        type=np.dtype(np.float64),
        unit=('nm'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='nm'))

    laser_wavelength = Quantity(
        type=np.dtype(np.float64),
        unit=('nm'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='nm'))

    laser_power = Quantity(
        type=np.dtype(np.float64),
        unit=('W'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='W'))

    power_density = Quantity(
        type=np.dtype(np.float64),
        unit=('W/m**2'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='W/m**2'))

    photon_flux = Quantity(
        type=np.dtype(np.float64),
        unit=('1/(m**2*s)'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='1/(m**2*s)'))

    # Function to calculate power density and photon flux

    def calculate_laser_parameters(self):
        # Constants
        h = 6.626e-34 * ureg("J*s")  # Planck's constant in Js
        c = 299_792_458 * ureg("m/s")  # Speed of light in m/s

        # Calculate spot area
        radius = self.spot_size / 2
        area = math.pi * (radius ** 2)

        # Calculate power density
        power_density = self.laser_power / area

        # Calculate energy of a single photon
        photon_energy = (h * c) / self.laser_wavelength

        # Calculate photon flux
        photon_flux = power_density / photon_energy
        return power_density, photon_flux

    def normalize(self, archive, logger):
        super(PLPropertiesLibrary, self).normalize(archive, logger)
        if self.laser_power and self.laser_wavelength and self.spot_size:
            self.power_density, self.photon_flux = self.calculate_laser_parameters()


class PLMeasurement(BaseMeasurement):
    '''PL Measurement'''

    m_def = Section(
        a_eln=dict(hide=['certified_values', 'certification_institute']))

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    properties = SubSection(
        section_def=PLProperties)

    data = SubSection(
        section_def=PLData)

    def normalize(self, archive, logger):
        self.method = "PL Measurement"
        super(PLMeasurement, self).normalize(archive, logger)


class PLSingleLibraryMeasurement(SingleLibraryMeasurement):
    m_def = Section(label_quantity='name',
                    a_eln=dict(properties=dict(
                        order=[
                            "name", "position_x_relative", "position_y_relative", "position_index", "position_x", "position_y"
                        ]))
                    )

    data = SubSection(
        section_def=PLDataSimple)


class PLMeasurementLibrary(LibraryMeasurement):
    '''PL Measurement'''

    m_def = Section(
        a_eln=dict(hide=['certified_values', 'certification_institute']))

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    # reference_file = Quantity(
    #     type=str,
    #     a_eln=dict(component='FileEditQuantity'),
    #     a_browser=dict(adaptor='RawFileAdaptor'))

    wavelength = Quantity(
        type=np.dtype(
            np.float64), unit=('nm'), shape=['*'])

    properties = SubSection(
        section_def=PLPropertiesLibrary)

    measurements = SubSection(
        section_def=PLSingleLibraryMeasurement, repeats=True)

    def normalize(self, archive, logger):
        super(PLMeasurementLibrary, self).normalize(archive, logger)
        self.method = "PL Measurement Mapping"
