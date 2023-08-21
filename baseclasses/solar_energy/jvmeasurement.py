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

from nomad.units import ureg
from nomad.metainfo import (
    Quantity,
    SubSection,
    Section)

from nomad.datamodel.metainfo.eln import SolarCellJVCurve
from .. import BaseMeasurement
from ..helper.add_solar_cell import add_solar_cell


class SolarCellJVCurveCustom(SolarCellJVCurve):
    m_def = Section(
        label_quantity='cell_name',
        a_eln=dict(
            hide=[
                'data_file',
                'certified_values',
                'certification_institute']))


class JVMeasurement(BaseMeasurement):

    m_def = Section(label_quantity='data_file', validate=False)

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    active_area = Quantity(
        type=np.dtype(
            np.float64),
        unit=('cm^2'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='cm^2',
            props=dict(
                minValue=0)))

    intensity = Quantity(
        type=np.dtype(
            np.float64),
        unit=('mW/cm^2'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mW/cm^2', props=dict(minValue=0)))

    integration_time = Quantity(
        type=np.dtype(
            np.float64),
        unit=('ms'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='ms',
            props=dict(
                minValue=0)))

    settling_time = Quantity(
        type=np.dtype(
            np.float64),
        unit=('ms'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='ms',
            props=dict(
                minValue=0)))

    averaging = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        a_eln=dict(component='NumberEditQuantity'))

    compliance = Quantity(
        type=np.dtype(
            np.float64),
        unit=('mA/cm^2'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mA/cm^2', props=dict(minValue=0)))

    jv_curve = SubSection(
        section_def=SolarCellJVCurveCustom,
        repeats=True,
        label_quantity='cell_name')

    def normalize(self, archive, logger):
        self.method = "JV Measurement"
        super(JVMeasurement, self).normalize(archive, logger)

        max_idx = -1
        eff = -1
        for i, curve in enumerate(self.jv_curve):
            if curve.efficiency is not None and curve.efficiency > eff:
                eff = curve.efficiency
                max_idx = i
        if max_idx >= 0:
            add_solar_cell(archive)
            solar_cell = archive.results.properties.optoelectronic.solar_cell
            solar_cell.open_circuit_voltage = self.jv_curve[max_idx].open_circuit_voltage
            solar_cell.short_circuit_current_density = self.jv_curve[
                max_idx].short_circuit_current_density
            solar_cell.fill_factor = self.jv_curve[max_idx].fill_factor
            solar_cell.efficiency = self.jv_curve[max_idx].efficiency
            solar_cell.illumination_intensity = self.jv_curve[max_idx].light_intensity
