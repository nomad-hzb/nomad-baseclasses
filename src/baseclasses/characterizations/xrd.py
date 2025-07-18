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
from nomad.datamodel.metainfo.basesections import MeasurementResult
from nomad.metainfo import Quantity, Section, SubSection

from .. import BaseMeasurement, LibraryMeasurement


class XRDData(ArchiveSection):
    m_def = Section(
        label_quantity='name',
        a_plot=[
            {
                'x': 'angle',
                'y': 'intensity',
                'layout': {
                    'yaxis': {'fixedrange': False},
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
                    'yaxis': {'fixedrange': False},
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
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
                'config': {'editable': True, 'scrollZoom': True},
            }
        ],
    )


class XRDShiftedData(XRDData):
    m_def = Section(
        label_quantity='model',
        a_plot=[
            {
                'x': 'angle',
                'y': 'intensity',
                'layout': {
                    'yaxis': {'fixedrange': False},
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

    goniometer_radius = Quantity(
        type=np.dtype(np.float64),
        unit=('mm'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mm'),
    )

    displacement = Quantity(
        type=np.dtype(np.float64),
        unit=('mm'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mm'),
    )


class XRDProperties(ArchiveSection):
    sample_temperature = Quantity(
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'),
    )


class XRDResults(MeasurementResult):
    model = Quantity(
        type=str,
        description='The model used for the peak fitting, eg Gaussians, Voigt functions',
        a_eln=dict(component='StringEditQuantity'),
    )

    peak_position = Quantity(
        type=np.dtype(np.float64),
        description='The position of an identified peak in units of the angle.',
        unit=('degree'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='degree'),
    )

    peak_height = Quantity(
        type=np.dtype(np.float64),
        description='The height of an identified peak',
        a_eln=dict(component='NumberEditQuantity'),
    )

    comment = Quantity(
        type=str,
        description='Comment on the XRD Analysis',
        a_eln=dict(component='RichTextEditQuantity', props=dict(height=200)),
    )


class XRD(BaseMeasurement):
    """XRD Measurement"""

    m_def = Section(a_eln=dict(hide=['certified_values', 'certification_institute']))

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'),
    )

    data = SubSection(section_def=XRDData)

    properties = SubSection(section_def=XRDProperties)

    results = SubSection(
        section_def=XRDResults,
        description="""
        The result of the XRD measurement.
        """,
        repeats=True,
    )

    def normalize(self, archive, logger):
        self.method = 'XRD'
        super().normalize(archive, logger)


class XRDLibrary(LibraryMeasurement):
    """XRD Measurement"""

    m_def = Section(a_eln=dict(hide=['certified_values', 'certification_institute']))

    def normalize(self, archive, logger):
        self.method = 'XRD'
        super().normalize(archive, logger)
