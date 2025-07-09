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
import pandas as pd
from nomad.datamodel.data import ArchiveSection
from nomad.datamodel.metainfo.basesections import (
    CompositeSystemReference,
)
from nomad.metainfo import Quantity, Section, SubSection

from baseclasses import BaseMeasurement


class ProcessedEfficiency(ArchiveSection):
    m_def = Section(
        label_quantity='name',
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

    name = Quantity(type=str, a_eln=dict(component='StringEditQuantity'))

    time = Quantity(
        type=np.dtype(np.float64),
        description='Time array of the MPP tracking measurement',
        shape=['*'],
        unit='hour',
    )

    efficiency = Quantity(
        links=["http://purl.obolibrary.org/obo/PATO_0001029"],
        type=np.dtype(np.float64),
        description='Efficiency array of the MPP tracking measurement',
        shape=['*'],
    )


class JVData(ProcessedEfficiency):
    v_oc = Quantity(
        links=["https://purl.archive.org/tfsco/TFSCO_00001034"],
        type=np.dtype(np.float64), shape=['*'], unit='V')

    j_sc = Quantity(
        links=["https://purl.archive.org/tfsco/TFSCO_00001108"],
        type=np.dtype(np.float64), shape=['*'], unit='mA/cm^2')

    fill_factor = Quantity(
        links=["https://purl.archive.org/tfsco/TFSCO_00001107"],
        type=np.dtype(np.float64), shape=['*'])


class PixelData(ProcessedEfficiency):
    include_for_average = Quantity(
        type=bool, default=True, a_eln=dict(component='BoolEditQuantity')
    )

    best_pixel = Quantity(
        type=bool, default=False, a_eln=dict(component='BoolEditQuantity')
    )

    voltage = Quantity(
        links=["https://purl.archive.org/tfsco/TFSCO_00005005",
               "http://purl.obolibrary.org/obo/PATO_0001464"],
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

    jv_data = SubSection(section_def=JVData, repeats=True)


class SampleData(CompositeSystemReference):
    m_def = Section(
        label_quantity='name',
        a_plot=[
            {
                'x': 'pixels/:/time',
                'y': 'pixels/:/efficiency',
                'layout': {
                    'showlegend': True,
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
            },
            {
                'label': 'JV Data Efficiency',
                'x': 'pixels/:/jv_data/:/time',
                'y': 'pixels/:/jv_data/:/efficiency',
                'layout': {
                    'showlegend': True,
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
            },
            {
                'label': 'JV Data J sc',
                'x': 'pixels/:/jv_data/:/time',
                'y': 'pixels/:/jv_data/:/j_sc',
                'layout': {
                    'showlegend': True,
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
            },
            {
                'label': 'JV Data V oc',
                'x': 'pixels/:/jv_data/:/time',
                'y': 'pixels/:/jv_data/:/v_oc',
                'layout': {
                    'showlegend': True,
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
            },
            {
                'label': 'JV Data Fill Factor',
                'x': 'pixels/:/jv_data/:/time',
                'y': 'pixels/:/jv_data/:/fill_factor',
                'layout': {
                    'showlegend': True,
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
            },
        ],
    )

    # name = Quantity(
    #     type=str,
    #     a_eln=dict(component='StringEditQuantity')
    # )

    parameter = Quantity(type=str, a_eln=dict(component='StringEditQuantity'))

    # samples = Quantity(
    #     type=Reference(CompositeSystem.m_def),
    #     shape=['*'],
    #     a_eln=dict(component='ReferenceEditQuantity'))

    time = Quantity(
        links=["http://purl.obolibrary.org/obo/PATO_0001309"],
        type=np.dtype(np.float64),
        description='Time array of the MPP tracking measurement',
        shape=['*'],
        unit='hour',
    )

    temperature = Quantity(
        type=np.dtype(np.float64),
        description='Temperature of sample during measurement',
        shape=['*'],
        unit='°C',
        a_plot=[
            {
                'label': 'Temperature',
                'x': 'time',
                'y': 'temperature',
                'layout': {
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
                'config': {'editable': True, 'scrollZoom': True},
            }
        ],
    )

    radiation = Quantity(
        type=np.dtype(np.float64),
        description='Radiation of sample during measurement',
        shape=['*'],
        a_plot=[
            {
                'label': 'Radiation',
                'x': 'time',
                'y': 'radiation',
                'layout': {
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
                'config': {'editable': True, 'scrollZoom': True},
            }
        ],
    )

    pixels = SubSection(section_def=PixelData, repeats=True)


class MPPTrackingHsprintCustom(BaseMeasurement):
    """
    MPP tracking measurement
    """

    m_def = Section(label_quantity='data_file', validate=False)

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'),
    )

    load_data_from_file = Quantity(
        type=bool, default=True, a_eln=dict(component='BoolEditQuantity')
    )

    averaging_grouping_minutes = Quantity(
        type=np.dtype(np.int64), default=15, a_eln=dict(component='NumberEditQuantity')
    )

    pixel_area = Quantity(
        type=np.dtype(np.float64),
        unit='cm**2',
        default=0.18,
        shape=[],
        a_eln=dict(component='NumberEditQuantity'),
    )

    samples = SubSection(section_def=SampleData, repeats=True)

    averages = SubSection(section_def=ProcessedEfficiency, repeats=True)

    best_pixels = SubSection(section_def=ProcessedEfficiency, repeats=True)

    def normalize(self, archive, logger):
        self.method = 'MPP Tracking'
        super().normalize(archive, logger)

        # calculate averages and best pixels
        best_pixels = []
        averages = {}
        for i, sample in enumerate(self.samples):
            for pixel in sample.pixels:
                if pixel.best_pixel:
                    pixel_entry = ProcessedEfficiency(
                        name=f'{sample.name} {pixel.name}',
                        time=pixel.time,
                        efficiency=pixel.efficiency,
                    )
                    best_pixels.append(pixel_entry)

            if sample.parameter is None:
                continue
            parameter = sample.parameter
            for j, pixel in enumerate(sample.pixels):
                if pixel.include_for_average:
                    df = pd.DataFrame()
                    df['time'] = pixel.time
                    df[f'efficiency_{i}_{j}'] = pixel.efficiency
                    df.dropna(inplace=True)
                    df.set_index('time')
                    if parameter in averages:
                        averages[parameter] = pd.merge_asof(
                            averages[parameter], df, on='time', direction='nearest'
                        )
                    else:
                        averages.update({parameter: df})

        self.best_pixels = best_pixels

        avgs = []
        for parameter, avg_data in averages.items():
            avg_data['eff_mean'] = avg_data[
                [c for c in avg_data.columns if c != 'time']
            ].mean(axis=1)

            avg = ProcessedEfficiency(
                name=parameter, time=avg_data.time, efficiency=avg_data.eff_mean
            )
            avgs.append(avg)
        self.averages = avgs
