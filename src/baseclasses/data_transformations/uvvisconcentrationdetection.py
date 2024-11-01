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
import plotly.graph_objects as go
from nomad.datamodel.metainfo.basesections import Analysis, SectionReference
from nomad.datamodel.metainfo.plot import PlotlyFigure, PlotSection
from nomad.metainfo import Quantity, Reference, Section
from scipy import stats

from baseclasses.solar_energy import UVvisData, UVvisMeasurement


class UVvisReference(SectionReference):
    reference = Quantity(
        type=Reference(UVvisMeasurement.m_def),
        a_eln=dict(component='ReferenceEditQuantity', label='UVvis Measurement'),
    )


class UVvisConcentrationDetection(Analysis, PlotSection):
    m_def = Section(label_quantity='name')

    inputs = Analysis.inputs.m_copy()
    inputs.section_def = UVvisReference

    material_name = Quantity(type=str, a_eln=dict(component='StringEditQuantity'))

    blank_substraction = Quantity(
        type=Reference(UVvisData.m_def),
        a_eln=dict(component='ReferenceEditQuantity'),
        description='If this calibration is computed with internal blank substraction, the user can provide a blank'
        'which gets substracted of each new measurement when later using this calibration.'
        'Please note that this blank also affects the minimum and maximum peak values of the calibration.',
    )

    blank_substraction_peak_value = Quantity(
        type=np.dtype(np.float64),
        default=0.0,
        description='This value is computed automatically if a blank substraction is given and is 0 otherwise.',
    )

    minimum_peak_value = Quantity(
        type=np.dtype(np.float64),
        description='The calibration curve can only be applied to peak intensities that are higher than this value.',
    )

    maximum_peak_value = Quantity(
        type=np.dtype(np.float64),
        description='The calibration curve can only be applied to peak intensities that are lower than this value.',
    )

    slope = Quantity(
        type=np.dtype(np.float64),
        description='The slope of the calibration curve.',
        a_eln=dict(component='NumberEditQuantity'),
    )

    intercept = Quantity(
        type=np.dtype(np.float64),
        description='The intercept of the calibration curve.',
        a_eln=dict(component='NumberEditQuantity'),
    )

    r2 = Quantity(
        type=np.dtype(np.float64),
        description='The R**2 to assess how well the calibration curve reflects the underlying intensity-concentration values.',
    )

    def normalize(self, archive, logger):
        super().normalize(archive, logger)

        if self.blank_substraction is not None:
            self.blank_substraction_peak_value = self.blank_substraction.peak_value
        else:
            self.blank_substraction_peak_value = 0.0

        peak_values = []
        concentrations = []

        for uvvis_reference in self.inputs:
            for uvvisdata in uvvis_reference.reference.measurements:
                if uvvisdata.concentration is None or uvvisdata.peak_value is None:
                    logger.error(
                        'Please provide concentration and area data for each UVvis Measurement.'
                    )
                else:
                    concentrations.append(uvvisdata.concentration)
                    peak_values.append(uvvisdata.peak_value)

        if len(peak_values) > 0:
            self.minimum_peak_value = min(peak_values)
            self.maximum_peak_value = max(peak_values)
            if self.blank_substraction is not None:
                self.minimum_peak_value = (
                    self.minimum_peak_value + self.blank_substraction.peak_value
                )
                self.maximum_peak_value = (
                    self.maximum_peak_value + self.blank_substraction.peak_value
                )

            try:
                concentration_values = np.array(
                    [measure.magnitude for measure in concentrations]
                )
                linear_regression = stats.linregress(peak_values, concentration_values)
                self.slope = linear_regression.slope
                self.intercept = linear_regression.intercept
                self.r2 = linear_regression.rvalue
            except BaseException as e:
                logger.warn('Could not find a linear regression.', exc_info=e)
                self.slope = 0
                self.intercept = 0

            fig = go.Figure(
                data=[
                    go.Scatter(
                        name='Calibration Curve',
                        x=peak_values,
                        y=concentrations,
                        mode='markers',
                    )
                ]
            )
            fig.add_traces(
                go.Scatter(
                    x=[self.minimum_peak_value, self.maximum_peak_value],
                    y=[
                        self.intercept + self.slope * self.minimum_peak_value,
                        self.intercept + self.slope * self.maximum_peak_value,
                    ],
                    mode='lines',
                )
            )
            fig.update_layout(
                xaxis_title='Peak Values',
                xaxis={'fixedrange': False},
                yaxis_title=f'Concentrations [{concentrations[0].units}]',
                title_text='Calibration Curve',
            )
            self.figures = [PlotlyFigure(label='figure 1', figure=fig.to_plotly_json())]
