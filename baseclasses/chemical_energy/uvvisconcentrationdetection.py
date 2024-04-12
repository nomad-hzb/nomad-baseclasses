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

from nomad.metainfo import Quantity, Reference, Section, SubSection, Datetime
from nomad.datamodel.metainfo.basesections import Analysis, SectionReference

from nomad.datamodel.metainfo.plot import PlotSection, PlotlyFigure
import plotly.graph_objects as go

from baseclasses.solar_energy import UVvisMeasurement

class UVvisReference(SectionReference):
    reference = Quantity(
        type=Reference(UVvisMeasurement.m_def),
        a_eln=dict(component='ReferenceEditQuantity', label='UVvis Measurement'))


class UVvisConcentrationDetection(Analysis, PlotSection):
    m_def = Section(label_quantity='name')

    inputs = Analysis.inputs.m_copy()
    inputs.section_def = UVvisReference

    material_name = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'))

    minimum_peak_value = Quantity(
        type=np.dtype(np.float64),
        description='The calibration curve can only be applied to peak intensities that are higher than this value.')

    maximum_peak_value = Quantity(
        type=np.dtype(np.float64),
        description='The calibration curve can only be applied to peak intensities that are lower than this value.')

    slope = Quantity(
        type=np.dtype(np.float64),
        description='The slope of the calibration curve.',
        a_eln=dict(component='NumberEditQuantity'))

    intercept = Quantity(
        type=np.dtype(np.float64),
        description='The intercept of the calibration curve.',
        a_eln=dict(component='NumberEditQuantity'))

    r2 = Quantity(
        type=np.dtype(np.float64),
        description='The R**2 to assess how well the calibration curve reflects the underlying intensity-concentration values.')

    def normalize(self, archive, logger):
        super(UVvisConcentrationDetection, self).normalize(archive, logger)

        peak_values = []
        concentrations = []

        for uvvis_reference in self.inputs:
            for uvvisdata in uvvis_reference.reference.measurements:
                if uvvisdata.concentration is None or uvvisdata.peak_value is None:
                    logger.error('Please provide concentration and area data for each UVvis Measurement.')
                else:
                    concentrations.append(uvvisdata.concentration)
                    peak_values.append(uvvisdata.peak_value)

        if len(peak_values) > 0:
            self.minimum_peak_value = min(peak_values)
            self.maximum_peak_value = max(peak_values)

            try:
                concentration_values = np.array([measure.magnitude for measure in concentrations])
                (self.slope, self.intercept), residuals, _, _, _ = np.polyfit(peak_values, concentration_values, 1,
                                                                              full=True)
                mean_value = np.mean(concentration_values)
                sum_squares_total = sum((measure - mean_value)**2 for measure in concentration_values)
                sum_squares_residuals = residuals[0] if len(residuals > 0) else 0
                self.r2 = 1-(sum_squares_residuals/sum_squares_total)
            except BaseException:
                self.slope = 0
                self.intercept = 0

            fig = go.Figure(data=[go.Scatter(name='Calibration Curve', x=peak_values, y=concentrations, mode='markers')])
            fig.add_traces(go.Scatter(x=[self.minimum_peak_value, self.maximum_peak_value],
                                      y=[self.intercept + self.slope * self.minimum_peak_value,
                                         self.intercept + self.slope * self.maximum_peak_value],
                                      mode='lines'))
            fig.update_layout(xaxis_title='Peak Values',
                              yaxis_title='Concentrations',
                              title_text='Calibration Curve')
            self.figures = [PlotlyFigure(label='figure 1', figure=fig.to_plotly_json())]

