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
from nomad.metainfo import Quantity, Reference, Section, SubSection

from baseclasses.helper.utilities import rewrite_json_recursively

from .. import LayerDeposition
from ..material_processes_misc import Annealing, Quenching, Sintering
from ..solution import Solution


class PrecursorSolution(ArchiveSection):
    m_def = Section(
        links=['https://purl.archive.org/tfsco/TFSCO_00001081'], label_quantity='name'
    )
    name = Quantity(type=str)

    reload_referenced_solution = Quantity(
        type=bool, default=False, a_eln=dict(component='ActionEditQuantity')
    )

    solution = Quantity(
        links=['http://purl.obolibrary.org/obo/CHEBI_75958'],
        type=Reference(Solution.m_def),
        a_eln=dict(component='ReferenceEditQuantity', label='Solution Reference'),
    )

    solution_volume = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0000918',
            'https://purl.archive.org/tfsco/TFSCO_00002158',
        ],
        type=np.dtype(np.float64),
        unit=('ml'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='ml',
            props=dict(minValue=0),
        ),
    )

    solution_viscosity = Quantity(
        links=['http://purl.obolibrary.org/obo/PATO_0000992'],
        type=np.dtype(np.float64),
        unit=('Pa*s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mPa*s',
            props=dict(minValue=0),
        ),
        description='Viscosity of the ink solution, critical for printability in inkjet printing',
    )

    solution_contact_angle = Quantity(
        description=('The angle formed between the solution and the underlying layer.'),
        links=[
            'http://www.ontology-of-units-of-measure.org/resource/om-2/ContactAngle'
        ],
        type=np.dtype(np.float64),
        unit=('deg'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='deg',
            props=dict(minValue=0, maxValue=180),
        ),
    )

    solution_details = SubSection(section_def=Solution)

    def normalize(self, archive, logger):
        if self.reload_referenced_solution and self.solution:
            self.reload_referenced_solution = False
            rewrite_json_recursively(archive, 'reload_referenced_solution', False)
            self.solution_details = self.solution.m_copy(deep=True)
            self.solution = None

        if self.solution and self.solution.name:
            if self.solution_volume:
                self.name = self.solution.name + ' ' + str(self.solution_volume)
            else:
                self.name = self.solution.name

        if self.solution_details and self.solution_details.name:
            if self.solution_volume:
                self.name = self.solution_details.name + ' ' + str(self.solution_volume)
            else:
                self.name = self.solution_details.name


def copy_solutions(sol):
    if not sol.solution:
        return
    if sol.solution_details:
        return

    sol.solution_details = sol.solution.m_copy(deep=True)
    sol.solution = None

    if not sol.solution_details.other_solution:
        return
    for sol_other in sol.solution_details.other_solution:
        copy_solutions(sol_other)


class WetChemicalDeposition(LayerDeposition):
    """Wet Chemical Deposition"""

    m_def = Section(links=['https://purl.archive.org/tfsco/TFSCO_00002051'])

    solution = SubSection(
        links=['http://purl.obolibrary.org/obo/OBI_0000293'],
        section_def=PrecursorSolution,
        repeats=True,
    )

    annealing = SubSection(
        links=['http://purl.obolibrary.org/obo/BFO_0000051'], section_def=Annealing
    )
    quenching = SubSection(
        links=['http://purl.obolibrary.org/obo/BFO_0000051'], section_def=Quenching
    )

    sintering = SubSection(section_def=Sintering, repeats=True)

    def normalize(self, archive, logger):
        if not self.method:
            self.method = 'Wet chemical deposition'
        super().normalize(archive, logger)

        if self.samples and self.solution:
            for wc_sol in self.solution:
                copy_solutions(wc_sol)
