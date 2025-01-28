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
from nomad.atomutils import Formula
from nomad.datamodel.metainfo.basesections import (
    CompositeSystem,
    CompositeSystemReference,
)
from nomad.datamodel.metainfo.plot import PlotlyFigure, PlotSection
from nomad.datamodel.results import Material, Results
from nomad.metainfo import Datetime, Quantity, Reference, SubSection
from nomad_chemical_energy.schema_packages.hzb_catlab_package import export_lab_id
from unidecode import unidecode

from baseclasses import PubChemPureSubstanceSectionCustom
from baseclasses.helper.utilities import create_short_id

from .. import BaseMeasurement


def make_nesd_id(archive):
    author = archive.metadata.main_author
    first_short, last_short = 'E', ''
    try:
        first_short = unidecode(author.first_name)[:2]
        last_short = unidecode(author.last_name)[:2]
    except Exception:
        pass
    lab_id = create_short_id(
        archive, str(first_short) + str(last_short), 'CE_NESD_Electrolyser'
    )
    export_lab_id(archive, lab_id)
    return lab_id


class NESDElectrode(CompositeSystem):
    electrolyte = Quantity(
        type=str,
        shape=[],
    )

    catalyst = Quantity(
        type=str,
        shape=[],
    )

    electrode_area = Quantity(type=np.dtype(np.float64), unit='mm**2')

    electrode_material = SubSection(section_def=PubChemPureSubstanceSectionCustom)

    gasket_material = SubSection(section_def=PubChemPureSubstanceSectionCustom)

    gasket_thickness = Quantity(type=np.dtype(np.float64), unit='mm')

    def normalize(self, archive, logger):
        super().normalize(archive, logger)


class ElectrolyserProperties(CompositeSystem):
    cell_name = Quantity(type=str, shape=[], a_eln=dict(component='StringEditQuantity'))

    test_rigg = Quantity(
        type=str,
        shape=[],
    )

    membrane = Quantity(
        type=str,
        shape=[],
    )

    torque = Quantity(type=np.dtype(np.float64), unit='newton * meter')

    anode = SubSection(section_def=NESDElectrode)

    cathode = SubSection(section_def=NESDElectrode)

    def is_valid_formula(self, formula, logger):
        try:
            Formula(formula)
            return True
        except Exception as e:
            logger.warn('Could not analyse material', exc_info=e)
            return False

    def normalize(self, archive, logger):
        if not self.lab_id:
            self.lab_id = make_nesd_id(archive)
        elements = ''
        if self.cathode:
            if self.is_valid_formula(self.cathode.catalyst, logger):
                elements += self.cathode.catalyst
            if self.is_valid_formula(self.cathode.electrode_material.name, logger):
                elements += self.cathode.electrode_material.name
        if self.anode:
            if self.is_valid_formula(self.anode.catalyst, logger):
                elements += self.anode.catalyst
            if self.is_valid_formula(self.anode.electrode_material.name, logger):
                elements += self.anode.electrode_material.name
        if elements and not archive.results:
            archive.results = Results()
        archive.results.material = Material()
        try:
            formula = Formula(elements, unknown='remove')
            formula.populate(section=archive.results.material)
        except Exception as e:
            logger.warn('Could not analyse material', exc_info=e)
        super().normalize(archive, logger)


class ElectrolyserPerformanceEvaluation(BaseMeasurement, PlotSection):
    labview_user = Quantity(type=str, a_eln=dict(component='StringEditQuantity'))

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'),
    )

    description = Quantity(
        type=str,
        description='Any information that cannot be captured in the other fields.',
        a_eln=dict(
            component='RichTextEditQuantity', props=dict(height=150), label='Comments'
        ),
    )

    time = Quantity(type=np.dtype(np.float64), shape=['*'], unit='second')

    h2_flow = Quantity(type=np.dtype(np.float64), shape=['*'], unit=('ml/minute'))

    o2_flow = Quantity(type=np.dtype(np.float64), shape=['*'], unit=('ml/minute'))

    anode_in = Quantity(type=np.dtype(np.float64), shape=['*'], unit=('°C'))

    cathode_in = Quantity(type=np.dtype(np.float64), shape=['*'], unit=('°C'))

    anode_out = Quantity(type=np.dtype(np.float64), shape=['*'], unit=('°C'))

    cathode_out = Quantity(type=np.dtype(np.float64), shape=['*'], unit=('°C'))

    ambient = Quantity(type=np.dtype(np.float64), shape=['*'], unit=('°C'))

    electrolyser_cell_anode = Quantity(
        type=np.dtype(np.float64), shape=['*'], unit=('°C')
    )

    electrolyser_cell_cathode = Quantity(
        type=np.dtype(np.float64), shape=['*'], unit='°C'
    )

    timestamp = Quantity(type=Datetime, shape=['*'])

    samples = SubSection(
        section_def=CompositeSystemReference,
        a_eln=dict(label='electrolyser properties'),
    )

    def make_flow_figure(self):
        fig = go.Figure(
            data=[
                go.Scatter(
                    name='H2 Flow',
                    x=self.time,
                    y=self.h2_flow,
                    line=dict(color='green'),
                )
            ]
        )
        fig.add_traces(
            go.Scatter(
                name='O2 Flow',
                x=self.time,
                y=self.o2_flow,
                yaxis='y2',
                line=dict(color='red'),
            )
        )
        fig.update_layout(
            yaxis=dict(
                title=f'H2 Flow [{self.h2_flow[0].units}]',
                titlefont=dict(color='green'),
                tickfont=dict(color='green'),
            ),
            yaxis2=dict(
                title=f'O2 Flow [{self.o2_flow[0].units}]',
                anchor='x',
                overlaying='y',
                side='right',
                titlefont=dict(color='red'),
                tickfont=dict(color='red'),
            ),
        )
        fig.update_layout(
            title_text='H2 and O2 Flow over Time',
            showlegend=True,
            xaxis={'fixedrange': False},
        )
        return fig

    def normalize(self, archive, logger):
        if self.h2_flow is not None:
            fig1 = self.make_flow_figure()
            self.figures = [
                PlotlyFigure(label='H2 O2 Flow Figure', figure=fig1.to_plotly_json()),
            ]
        super().normalize(archive, logger)
