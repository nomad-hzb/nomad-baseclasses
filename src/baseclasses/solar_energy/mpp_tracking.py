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
        links=["https://purl.archive.org/tfsco/TFSCO_00001063"],
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


class StabilityFiguresOfMerit(ArchiveSection):
    """
    Perovskite solar cell stability figures of merit. More information can be found in
    the publication Consensus statement for stability assessment and reporting for
    perovskite photovoltaics based on ISOS procedures published in NAture Energy
    https://www.nature.com/articles/s41560-019-0529-5/.
    """

    T95 = Quantity(
        links=["https://purl.archive.org/tfsco/TFSCO_00007004"],
        type=np.dtype(np.float64),
        unit=('hour'),
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
        unit=('hour'),
        shape=[],
        description="""
            The time after which the cell performance has degraded by 5 % with respect
            to the performance after any initial burn in phase.
        - If there are uncertainties, only state the best estimate, e.g. write
        1000 and not 950-1050
        - If unknown or not applicable, leave this field empty.
        """,
        a_eln=dict(component='NumberEditQuantity'),
    )

    T80 = Quantity(
        links=["https://purl.archive.org/tfsco/TFSCO/TFSCO_00003503"],
        type=np.dtype(np.float64),
        unit=('hour'),
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
        unit=('hour'),
        shape=[],
        description="""
            The time after which the cell performance has degraded by 20 %
            with respect to the performance after any initial burn in phase.
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
        unit=('hour'),
        description="""The time that it takes for the cell to stabilize after
        an initial burn-in *(fast peroformance decrease) or a fast increase in
        performance
        to reach a maximun PCE value in the transient. This values is needed to
        report the
        Ts80 and Ts95 values.""",
        a_eln=dict(component='NumberEditQuantity'),
    )


class MPPTracking(BaseMeasurement):
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

    def normalize(self, archive, logger):
        super().normalize(archive, logger)
        self.method = 'MPP Tracking'
