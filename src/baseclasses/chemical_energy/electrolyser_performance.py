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

from nomad.metainfo import (Quantity, Datetime)
from nomad.datamodel.data import ArchiveSection
from nomad.datamodel.metainfo.basesections import CompositeSystemReference
from nomad.datamodel.metainfo.plot import PlotSection, PlotlyFigure
import plotly.graph_objects as go

from .. import BaseMeasurement, ReadableIdentifiersCustom
from .cesample import build_initial_id, create_id


#TODO imports cleaning and maybe create quantities for ids if needed

class ElectrolyserPerformanceEvaluation(BaseMeasurement, PlotSection):

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    time = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        unit='second')

    h2_flow = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        unit=('ml/minute'))

    o2_flow = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        unit=('ml/minute'))

    anode_in = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        unit=('°C'))

    cathode_in = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        unit=('°C'))

    anode_out = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        unit=('°C'))

    cathode_out = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        unit=('°C'))

    ambient = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        unit=('°C'))

    electrolyser_cell_anode = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        unit=('°C'))

    electrolyser_cell_cathode = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        unit='°C')

    timestamp = Quantity(
        type=Datetime,
        shape=['*'])

    def make_flow_figure(self):
        fig = go.Figure(data=[go.Scatter(name='H2 Flow', x=self.time, y=self.h2_flow,
                                         line=dict(color='green'))])
        fig.add_traces(go.Scatter(name='O2 Flow', x=self.time, y=self.o2_flow,
                                  yaxis='y2', line=dict(color='red')))
        fig.update_layout(yaxis=dict(title=f'H2 Flow [{self.h2_flow[0].units}]',
                                     titlefont=dict(color='green'),
                                     tickfont=dict(color='green')),
                          yaxis2=dict(title=f'O2 Flow [{self.o2_flow[0].units}]',
                                      anchor='x',
                                      overlaying='y', side='right',
                                      titlefont=dict(color='red'),
                                      tickfont=dict(color='red')))
        fig.update_layout(title_text='H2 and O2 Flow over Time', showlegend=True, xaxis={'fixedrange': False})
        return fig

    def normalize(self, archive, logger):
        fig1 = self.make_flow_figure()
        self.figures = [PlotlyFigure(label='H2 O2 Flow Figure', figure=fig1.to_plotly_json()),]
        super(ElectrolyserPerformanceEvaluation, self).normalize(archive, logger)
