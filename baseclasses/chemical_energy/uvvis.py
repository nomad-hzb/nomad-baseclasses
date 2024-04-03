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

from nomad.metainfo import Quantity, Reference, Section, SubSection
from nomad.datamodel.metainfo.basesections import Analysis

from baseclasses.solar_energy import UVvisData, UVvisMeasurement

class UVvisDataConcentration(UVvisData):

    concentration = Quantity(
        type=np.dtype(np.float64),
        unit=('mg/ml'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mg/ml'))

    area = Quantity(
        type=np.dtype(np.float64),
        unit=('nm'),
        a_eln=dict(component='NumberEditQuantity'))

    def normalize(self, archive, logger):
        #TODO compute area instead of max value (change unit for area quantity)
        if self.wavelength is not None:
            self.area = np.max(self.wavelength)

        super(UVvisDataConcentration, self).normalize(archive, logger)

class UVvisMeasurementConcentration(UVvisMeasurement):
    '''UV vis Measurement associated with concentration'''

    measurements = SubSection(
        section_def=UVvisDataConcentration, repeats=True)

    def normalize(self, archive, logger):
        self.method = "UVvis Measurement"
        super(UVvisMeasurementConcentration, self).normalize(archive, logger)

class UVvisConcentrationDetection(Analysis):

    uvvis_measurements = Quantity(
        type=Reference(UVvisMeasurementConcentration.m_def),
        shape=['*'],
        a_eln=dict(component='ReferenceEditQuantity'))

    material_name = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'))

    minimum_area = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity'))

    maximum_area = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity'))

    slope = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity'))

    intercept = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity'))

    def normalize(self, archive, logger):
        super(UVvisConcentrationDetection, self).normalize(archive, logger)

        areas = []
        concentrations = []
        for measurement in self.uvvis_measurements:
            areas.append(measurement.area)
            concentrations.append(measurement.concentration)

        self.minimum_area = min(areas)
        self.maximum_area = max(areas)
