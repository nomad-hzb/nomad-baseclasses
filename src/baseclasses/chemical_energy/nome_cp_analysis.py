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

from datetime import datetime

import numpy as np
from nomad.datamodel.metainfo.basesections import (
    Analysis,
    AnalysisResult,
    CompositeSystemReference,
    SectionReference,
)
from nomad.datamodel.results import Material, Results
from nomad.metainfo import Quantity, Reference, Section, SubSection

from baseclasses.chemical_energy import Chronopotentiometry

from ..helper.utilities import get_reference
from .cesample import export_lab_id


class CPOERReference(SectionReference):
    reference = Quantity(
        type=Reference(Chronopotentiometry.m_def),
        a_eln=dict(
            component='ReferenceEditQuantity',
            label='OER Chronopotentiometry Measurement',
        ),
    )


class CPOERAnalysisResult(AnalysisResult):
    voltage_avg_first5 = Quantity(type=np.dtype(np.float64), unit=('V'))
    voltage_avg_last5 = Quantity(type=np.dtype(np.float64), unit=('V'))
    voltage_difference = Quantity(type=np.dtype(np.float64), unit=('V'))
    j = Quantity(
        type=np.dtype(np.float64), description='current density', unit=('A/cm^2')
    )
    current_density_string = Quantity(
        type=str,
        description='string representation of j (needed for terms in explore view)',
    )
    experiment_duration = Quantity(type=np.dtype(np.float64), unit=('s'))
    reaction_type = Quantity(
        type=str,
        description='At the moment only OER CP is supported. In the future maybe also NRR CP.',
    )
    voltage_shift = Quantity(
        links=['https://w3id.org/nfdi4cat/voc4cat_0007219'],
        type=np.dtype(np.float64),
        unit=('V'),
    )
    resistance = Quantity(
        links=['https://w3id.org/nfdi4cat/voc4cat_0007222'],
        type=np.dtype(np.float64),
        unit=('ohm'),
    )
    samples = SubSection(
        section_def=CompositeSystemReference,
        repeats=True,
    )

    def normalize(self, archive, logger):
        rounded_current_density = round(self.j, 4)
        self.current_density_string = format(rounded_current_density, '~')
        super().normalize(archive, logger)


class CPAnalysis(Analysis):
    m_def = Section(label_quantity='name')

    inputs = Analysis.inputs.m_copy()
    inputs.section_def = CPOERReference

    outputs = Analysis.outputs.m_copy()
    outputs.section_def = CPOERAnalysisResult

    def normalize(self, archive, logger):
        refs = get_all_cp_in_upload(archive, archive.metadata.upload_id)
        self.inputs = [CPOERReference(name=name, reference=ref) for [name, ref] in refs]

        if self.inputs is not None and len(self.inputs) > 0:
            first_oer_run = self.inputs[0].reference
            last_oer_run = self.inputs[-1].reference

            voltage_avg_first5 = np.mean(np.array(first_oer_run.voltage[:5]))
            voltage_avg_last5 = np.mean(np.array(last_oer_run.voltage[-5:]))
            voltage_difference = voltage_avg_first5 - voltage_avg_last5

            current = first_oer_run.properties.step_1_current
            area = first_oer_run.properties.sample_area
            if current is not None and area is not None:
                current_density = current / first_oer_run.properties.sample_area

            cycle_number = len(self.inputs)
            if cycle_number > 1:
                time_one_cycle = (
                    self.inputs[1].reference.datetime - first_oer_run.datetime
                )
                experiment_duration = cycle_number * time_one_cycle.total_seconds()
            else:
                experiment_duration = first_oer_run.time[-1]

            for sample in first_oer_run.samples:
                export_lab_id(archive, sample.lab_id)
                if sample.reference.chemical_composition_or_formulas is not None:
                    if not archive.results:
                        archive.results = Results()
                    if not archive.results.material:
                        archive.results.material = Material()
                    try:
                        from nomad.atomutils import Formula

                        formula = Formula(
                            sample.reference.chemical_composition_or_formulas
                        )
                        formula.populate(section=archive.results.material)
                    except Exception as e:
                        logger.warn('Could not analyse material', exc_info=e)

            self.outputs = [
                CPOERAnalysisResult(
                    name=first_oer_run.name,
                    voltage_avg_first5=voltage_avg_first5,
                    voltage_avg_last5=voltage_avg_last5,
                    voltage_difference=voltage_difference,
                    j=current_density,
                    experiment_duration=experiment_duration,
                    reaction_type=first_oer_run.method,
                    samples=first_oer_run.samples,
                    voltage_shift=first_oer_run.voltage_shift,
                    resistance=first_oer_run.resistance,
                )
            ]
            self.outputs[0].normalize(archive, logger)
        super().normalize(archive, logger)


def get_all_cp_in_upload(data_archive, upload_id):
    from nomad.app.v1.models import MetadataPagination
    from nomad.search import search

    query = {
        'section_defs.definition_qualified_name': 'baseclasses.chemical_energy.chronopotentiometry.Chronopotentiometry',
        'results.eln.methods': 'OER Chronopotentiometry',
        'upload_id': upload_id,
    }
    pagination = MetadataPagination()
    pagination.page_size = 10000
    search_result = search(
        owner='all',
        query=query,
        pagination=pagination,
        user_id=data_archive.metadata.main_author.user_id,
    )

    lst = search_result.data
    lst.sort(
        key=lambda cp_entry: datetime.strptime(
            cp_entry['data']['datetime'], '%Y-%m-%dT%H:%M:%S%z'
        )
    )
    refs = [
        [cp_entry['data']['data_file'], get_reference(upload_id, cp_entry['entry_id'])]
        for cp_entry in lst
    ]
    return refs
