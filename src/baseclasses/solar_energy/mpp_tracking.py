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
from nomad.datamodel.data import ArchiveSection
from nomad.datamodel.metainfo.basesections import MeasurementResult
from nomad.datamodel.metainfo.plot import PlotlyFigure, PlotSection
from nomad.metainfo import Quantity, Section, SubSection
from nomad.units import ureg

from .. import BaseMeasurement


class MPPTrackingProperties(ArchiveSection):
    start_voltage_manually = Quantity(
        type=bool,
        shape=[],
        a_eln=dict(
            component='BoolEditQuantity',
        ),
    )

    perturbation_frequency = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='s',
            props=dict(minValue=0),
        ),
    )

    sampling = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity', props=dict(minValue=0)),
    )

    perturbation_voltage = Quantity(
        type=np.dtype(np.float64),
        unit=('V'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='V',
            props=dict(minValue=0),
        ),
    )

    perturbation_delay = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='s',
            props=dict(minValue=0),
        ),
    )

    time = Quantity(
        type=np.dtype(np.float64),
        description='Total time of the measurement',
        unit=('s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='s',
            props=dict(minValue=0),
        ),
    )

    status = Quantity(
        type=str,
        a_eln=dict(
            component='StringEditQuantity',
        ),
    )

    last_pce = Quantity(
        type=np.dtype(np.float64),
        description="""Last power convertion efficiency recorded in the MPP tracking
        measurement""",
        a_eln=dict(
            component='NumberEditQuantity', props=dict(minValue=0, maxValue=100)
        ),
    )

    last_vmpp = Quantity(
        type=np.dtype(np.float64),
        description="""Last voltage at maximum power point recorded in the MPP tracking
        measurement""",
        unit=('V'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='V'),
    )


class StabilityFiguresOfMerit(MeasurementResult):
    """
    Perovskite solar cell stability figures of merit. More information can be found in
    the publication Consensus statement for stability assessment and reporting for
    perovskite photovoltaics based on ISOS procedures published in NAture Energy
    https://www.nature.com/articles/s41560-019-0529-5/.
    """

    T95 = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        shape=[],
        description="""
    The time after which the cell performance has degraded by 5 % with respect to the
    initial performance.
    - If there are uncertainties, only state the best estimate, e.g. write 1000
    and not 950-1050
    - If unknown or not applicable, leave this field empty.
                    """,
        a_eln=dict(component='NumberEditQuantity'),
    )

    Ts95 = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        shape=[],
        description="""
            The time after which the cell performance has degraded by 5 % with respect
            to the reached efficiency after a possbile burn in phase.
        - If there are uncertainties, only state the best estimate, e.g. write
        1000 and not 950-1050
        - If unknown or not applicable, leave this field empty.
        """,
        a_eln=dict(component='NumberEditQuantity'),
    )

    T80 = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        shape=[],
        description="""
           The time after which the cell performance has degraded by 20 %
            with respect to the initial performance.
        - If there are uncertainties, only state the best estimate,
        e.g. write 1000 and not 950-1050
        - If unknown or not applicable, leave this field empty.
        """,
        a_eln=dict(component='NumberEditQuantity'),
    )

    Ts80 = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        shape=[],
        description="""
             The time after which the cell performance has degraded by 20 % with respect
            to the reached efficiency after a possbile burn in phase.
        - If there are uncertainties, only state the best estimate, e.g.
        write 1000 and not 950-1050
        - If unknown or not applicable, leave this field empty.
        """,
        a_eln=dict(component='NumberEditQuantity'),
    )

    PCE_after_1000_h = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description="""
            The efficiency, PCE, of the cell after 1000 hours
        - Give the efficiency in %
        - If there are uncertainties, only state the best estimate, e.g. write
        20.5 and not 19-20
        - If unknown or not applicable, leave this field empty.
        """,
        a_eln=dict(component='NumberEditQuantity'),
    )

    initial_stabilization_time = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        description="""The time that it takes for the cell to stabilize after
        an initial burn-in *(fast peroformance decrease) or a fast increase in
        performance
        to reach a maximun PCE value in the transient. This values is needed to
        report the
        Ts80 and Ts95 values.""",
        a_eln=dict(component='NumberEditQuantity'),
    )


class MPPTracking(BaseMeasurement, PlotSection):
    """
    MPP tracking measurement
    """

    m_def = Section(label_quantity='data_file', validate=False)

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'),
    )

    time = Quantity(
        type=np.dtype(np.float64),
        description='Time array of the MPP tracking measurement',
        shape=['*'],
        unit='s',
    )

    power_density = Quantity(
        type=np.dtype(np.float64),
        description='Power density array of the MPP tracking measurement',
        shape=['*'],
        unit='mW/cm**2',
        a_plot=[
            {
                'label': 'Power Density',
                'x': 'time',
                'y': 'power_density',
                'layout': {
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
                'config': {'editable': True, 'scrollZoom': True},
            }
        ],
    )

    voltage = Quantity(
        type=np.dtype(np.float64),
        description='Voltage array of the MPP tracking measurement',
        shape=['*'],
        unit='V',
        a_plot=[
            {
                'label': 'Voltage',
                'x': 'time',
                'y': 'voltage',
                'layout': {
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
                'config': {'editable': True, 'scrollZoom': True},
            }
        ],
    )

    efficiency = Quantity(
        type=np.dtype(np.float64),
        description='Efficiency array of the MPP tracking measurement',
        shape=['*'],
        a_plot=[
            {
                'label': 'PCE',
                'x': 'time',
                'y': 'efficiency',
                'layout': {
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
                'config': {'editable': True, 'scrollZoom': True},
            }
        ],
    )

    current_density = Quantity(
        type=np.dtype(np.float64),
        description='Current density array of the MPP tracking measurement',
        shape=['*'],
        unit='mA/cm^2',
        a_plot=[
            {
                'label': 'Current Density',
                'x': 'time',
                'y': 'current_density',
                'layout': {
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
                'config': {'editable': True, 'scrollZoom': True},
            }
        ],
    )

    properties = SubSection(section_def=MPPTrackingProperties)
    results = SubSection(section_def=StabilityFiguresOfMerit, repeats=True)

    def make_mppt_figure(
        self,
        T95,
        T80,
        Ts95,
        Ts80,
        t_at_p_max,
        power_density_abs_filtered_rough,
        power_density_abs_filtered_win10,
    ):
        # Base trace
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=self.time.to('hr'),
                y=np.abs(self.power_density),
                mode='lines',
                name='Power density',
            )
        )

        fig.add_trace(
            go.Scatter(
                x=self.time.to('hr'),
                y=power_density_abs_filtered_rough,
                mode='lines',
                name='Power density for threshold (filtered 20% window)',
            )
        )

        fig.add_trace(
            go.Scatter(
                x=self.time.to('hr'),
                y=power_density_abs_filtered_win10,
                mode='lines',
                name='Power density for init power (filtered 10-point window)',
            )
        )

        # Add vertical lines for thresholds
        line_specs = [
            (T95, 'T95'),
            (T80, 'T80'),
            (Ts95, 'Ts95'),
            (Ts80, 'Ts80'),
            (t_at_p_max, 'IST'),
        ]
        for x_val, label in line_specs:
            if x_val is None:
                continue
            fig.add_vline(
                x=x_val.to('hr').magnitude,
                line_dash='dash',
                line_width=1.5,
                annotation_text=label,
                annotation_position='bottom right',
            )

        fig.update_layout(
            title='Power density over time with thresholds',
            xaxis_title='Time (hr)',
            yaxis_title='Power density (mW/cm²)',
            template='plotly_white',
        )
        return fig

    def calculate_performance_parameters(self):
        from scipy.signal import savgol_filter

        time = self.time
        power_density = self.power_density
        if len(time) < 10:
            return None, None, None, None, None, None
        # Initial setup
        t0 = np.min(time)
        power_density_abs = np.abs(power_density)
        window_size = len(power_density) // 5
        power_density_abs_filtered_rough = savgol_filter(
            power_density_abs, window_size, 3
        )
        power_density_abs_filtered_win10 = savgol_filter(power_density_abs, 10, 3)
        # Get reference values
        p_at_t0 = power_density_abs_filtered_win10[np.argmin(time)]
        p_max_idx = np.argmax(power_density_abs_filtered_win10)
        t_at_p_max = time[p_max_idx]
        p_at_max = power_density_abs_filtered_win10[p_max_idx]

        # Helper function to find time when power drops below threshold
        def find_threshold_time(time_ref, power_ref, threshold_fraction):
            """Find the time when power drops below threshold_fraction of power_ref"""
            mask = time > time_ref
            power_below = (
                power_density_abs_filtered_rough[mask] < threshold_fraction * power_ref
            )

            if not np.any(power_below):
                return None

            time_subset = time[mask]
            threshold_time = time_ref + np.min(
                np.abs(
                    time_ref
                    - time_subset[
                        power_density_abs_filtered_rough[mask]
                        < threshold_fraction * power_ref
                    ]
                )
            )
            return threshold_time

        # Calculate all threshold times
        T95 = find_threshold_time(t0, p_at_t0, 0.95)
        T80 = find_threshold_time(t0, p_at_t0, 0.80)
        Ts95 = find_threshold_time(t_at_p_max, p_at_max, 0.95)
        Ts80 = find_threshold_time(t_at_p_max, p_at_max, 0.80)
        return (
            T95,
            T80,
            Ts95,
            Ts80,
            t_at_p_max,
            power_density_abs_filtered_rough,
            power_density_abs_filtered_win10,
        )

    def normalize(self, archive, logger):
        self.method = 'MPP Tracking'
        super().normalize(archive, logger)
        if self.time is not None and self.power_density is not None:
            (
                T95,
                T80,
                Ts95,
                Ts80,
                initial_stabilization_time,
                power_density_abs_filtered_rough,
                power_density_abs_filtered_win10,
            ) = self.calculate_performance_parameters()
            if not self.results:
                self.results = [StabilityFiguresOfMerit()]
            self.results[0].T95 = (
                self.results[0].T95 if self.results and self.results[0].T95 else T95
            )
            self.results[0].T80 = (
                self.results[0].T80 if self.results and self.results[0].T80 else T80
            )
            self.results[0].Ts95 = (
                self.results[0].Ts95 if self.results and self.results[0].Ts95 else Ts95
            )
            self.results[0].Ts80 = (
                self.results[0].Ts80 if self.results and self.results[0].Ts80 else Ts80
            )
            self.results[0].initial_stabilization_time = (
                self.results[0].initial_stabilization_time
                if self.results and self.results[0].initial_stabilization_time
                else initial_stabilization_time
            )

            fig1 = self.make_mppt_figure(
                self.results[0].T95,
                self.results[0].T80,
                self.results[0].Ts95,
                self.results[0].Ts80,
                self.results[0].initial_stabilization_time,
                power_density_abs_filtered_rough,
                power_density_abs_filtered_win10,
            )
            self.figures = [
                PlotlyFigure(
                    label='Figure of Merits for Stability', figure=fig1.to_plotly_json()
                )
            ]
