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
from nomad.metainfo import Quantity, Section

from .. import BaseMeasurement, LibraryMeasurement


class XRRData(ArchiveSection):
    m_def = Section(
        label_quantity='name',
        a_plot=[
            {
                'x': 'angle',
                'y': 'intensity',
                'layout': {
                    'yaxis': {'fixedrange': False, 'type': 'log'},
                    'xaxis': {'fixedrange': False},
                },
                'config': {
                    'scrollZoom': True,
                    'staticPlot': False,
                },
            }
        ],
    )

    name = Quantity(type=str)

    metadata = Quantity(type=str, a_browser=dict(adaptor='RawFileAdaptor'))

    angle_type = Quantity(type=str)

    angle = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        unit='degree',
        a_plot=[
            {
                'x': 'angle',
                'y': 'intensity',
                'layout': {
                    'yaxis': {'fixedrange': False, 'type': 'log'},
                    'xaxis': {'fixedrange': False},
                },
                'config': {'editable': True, 'scrollZoom': True},
            }
        ],
    )

    intensity = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        a_plot=[
            {
                'x': 'angle',
                'y': 'intensity',
                'layout': {
                    'yaxis': {'fixedrange': False, 'type': 'log'},
                    'xaxis': {'fixedrange': False},
                },
                'config': {'editable': True, 'scrollZoom': True},
            }
        ],
    )


class XRRFittedData(XRRData):
    m_def = Section(
        label_quantity='model',
        a_plot=[
            {
                'x': 'angle',
                'y': 'intensity',
                'layout': {
                    'yaxis': {'fixedrange': False, 'type': 'log'},
                    'xaxis': {'fixedrange': False},
                },
                'config': {
                    'scrollZoom': True,
                    'staticPlot': False,
                },
            }
        ],
    )

    model = Quantity(type=str, a_eln=dict(component='StringEditQuantity'))

    critical_angle = Quantity(
        type=np.dtype(np.float64),
        unit=('degree'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='degree'),
    )

    apparent_density = Quantity(
        type=np.dtype(np.float64),
        unit=('g/cm**3'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='g/cm**3'),
    )

    apparent_roughness = Quantity(
        type=np.dtype(np.float64),
        unit=('nm'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='nm'),
    )

    chi_squared = Quantity(
        type=np.dtype(np.float64), a_eln=dict(component='NumberEditQuantity')
    )

    diffuse_scattering = Quantity(
        type=np.dtype(np.float64), a_eln=dict(component='NumberEditQuantity')
    )

    detector_noise = Quantity(
        type=np.dtype(np.float64), a_eln=dict(component='NumberEditQuantity')
    )


class XRR(BaseMeasurement):
    """XRR Measurement"""

    m_def = Section(a_eln=dict(hide=['certified_values', 'certification_institute']))

    data_file = Quantity(
        type=str,
        shape=['*'],
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'),
    )

    # data = SubSection(
    #     section_def=XRRData)

    # fitted_data = SubSection(
    #     section_def=XRRFittedData, repeats=True)

    def normalize(self, archive, logger):
        self.method = 'XRR'
        super().normalize(archive, logger)


class XRRLibrary(LibraryMeasurement):
    """XRR Measurement"""

    m_def = Section(a_eln=dict(hide=['certified_values', 'certification_institute']))

    def normalize(self, archive, logger):
        super().normalize(archive, logger)
        self.method = 'XRR'
