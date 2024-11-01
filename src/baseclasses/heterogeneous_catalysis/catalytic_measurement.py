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

import os

import numpy as np
from nomad.datamodel.data import ArchiveSection
from nomad.metainfo import Quantity, Section, SubSection

from .. import MeasurementOnSample


class Reactant(ArchiveSection):
    m_def = Section(label_quantity='name')
    name = Quantity(type=str, a_eln=dict(component='StringEditQuantity'))

    amount = Quantity(type=np.dtype(np.float64), shape=['*'])


class Feed(ArchiveSection):
    m_def = Section(
        a_plot=[
            {
                'label': 'Feed',
                'x': 'runs',
                'y': ['reactants/:/amount'],
                'layout': {
                    'showlegend': True,
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
                'config': {'editable': True, 'scrollZoom': True},
            }
        ]
    )
    flow_volume = Quantity(type=np.dtype(np.float64), shape=['*'], unit='ml/minute')
    runs = Quantity(type=np.dtype(np.float64), shape=['*'])

    reactants = SubSection(section_def=Reactant, repeats=True)


class Product(ArchiveSection):
    m_def = Section(label_quantity='name')
    name = Quantity(type=str, a_eln=dict(component='StringEditQuantity'))

    exchange = Quantity(type=np.dtype(np.float64), shape=['*'])
    selectivity = Quantity(type=np.dtype(np.float64), shape=['*'])
    relative_rate = Quantity(type=np.dtype(np.float64), shape=['*'])
    absolute_rate = Quantity(type=np.dtype(np.float64), shape=['*'])


class CatalyticReactionData(ArchiveSection):
    m_def = Section(
        a_plot=[
            {
                'label': 'Relative exchange rate',
                'x': 'runs',
                'y': 'products/:/relative_rate',
                'layout': {
                    'showlegend': True,
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
                'config': {'editable': True, 'scrollZoom': True},
            },
            {
                'label': 'Selectivity',
                'x': 'runs',
                'y': ['c_balance', 'products/:/selectivity'],
                'layout': {
                    'showlegend': True,
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
                'config': {'editable': True, 'scrollZoom': True},
            },
            {
                'label': 'Exchange ',
                'x': 'runs',
                'y': 'products/:/exchange',
                'layout': {
                    'showlegend': True,
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
                'config': {'editable': True, 'scrollZoom': True},
            },
        ]
    )

    temperature = Quantity(type=np.dtype(np.float64), shape=['*'], unit='°C')

    c_balance = Quantity(type=np.dtype(np.float64), shape=['*'])

    runs = Quantity(type=np.dtype(np.float64), shape=['*'])

    products = SubSection(section_def=Product, repeats=True)


class CatalyticReaction(MeasurementOnSample):
    reaction = Quantity(type=str, a_eln=dict(component='StringEditQuantity'))

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'),
    )

    feed = SubSection(section_def=Feed)
    data = SubSection(section_def=CatalyticReactionData)

    def normalize(self, archive, logger):
        super().normalize(archive, logger)
        self.method = 'Catalytic Reaction'

        if not self.data_file or os.path.splitext(self.data_file)[-1] != '.csv':
            return

        with archive.m_context.raw_file(self.data_file) as f:
            import pandas as pd

            data = pd.read_csv(f.name).dropna(axis=1, how='all')
        feed = Feed()
        cat_data = CatalyticReactionData()
        reactants = []
        products = []
        number_of_runs = 0
        for col in data.columns:
            if len(data[col]) < 1:
                continue
            col_split = col.split(' ')
            if len(col_split) < 2:
                continue

            number_of_runs = max(len(data[col]), number_of_runs)

            if col_split[0] == 'x':
                reactant = Reactant(name=col_split[1], amount=data[col])
                reactants.append(reactant)
            if col_split[0] == 'temperature':
                cat_data.temperature = data[col]

            if col_split[0] == 'C-balance':
                cat_data.c_balance = data[col]

            if col_split[0] == 'GHSV':
                feed.flow_volume = data[col]

            if len(col_split) < 3 or col_split[2] != '(%)':
                continue

            product = Product(name=col_split[1])
            for i, p in enumerate(products):
                if p.name == col_split[1]:
                    product = products.pop(i)
                    break

            products.append(product)

            if col_split[0] == 'x_p':
                product.exchange = data[col]

            if col_split[0] == 'S_p':
                product.selectivity = data[col]

            if col_split[0] == 'x_r':
                product.relative_rate = data[col]

            if col_split[0] == 'r':
                product.absolute_rate = data[col]

        for p in products:
            if p.exchange is None or len(p.exchange) == 0:
                p.exchange = number_of_runs * [0]
            if p.selectivity is None or len(p.selectivity) == 0:
                p.selectivity = number_of_runs * [0]
            if p.relative_rate is None or len(p.relative_rate) == 0:
                p.relative_rate = number_of_runs * [0]
            if p.absolute_rate is None or len(p.absolute_rate) == 0:
                p.absolute_rate = number_of_runs * [0]

        feed.reactants = reactants
        feed.runs = np.linspace(0, number_of_runs - 1, number_of_runs)
        cat_data.products = products
        cat_data.runs = np.linspace(0, number_of_runs - 1, number_of_runs)

        self.feed = feed
        self.data = cat_data
