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

from nomad.metainfo import Quantity, Reference, Section, SubSection, Datetime
from nomad.datamodel.metainfo.basesections import Analysis, SectionReference, AnalysisResult, CompositeSystemReference
from nomad.datamodel.results import Results, Material

from baseclasses.chemical_energy import Chronopotentiometry
from ..helper.utilities import get_reference


class CPOERReference(SectionReference):
    reference = Quantity(
        type=Reference(Chronopotentiometry.m_def),
        a_eln=dict(component='ReferenceEditQuantity', label='OER Chronopotentiometry Measurement'))


class CPOERAnalysisResult(AnalysisResult):
    voltage_avg_first5 = Quantity(
        type=np.dtype(np.float64),
        unit=('V'))
    voltage_avg_last5 = Quantity(
        type=np.dtype(np.float64),
        unit=('V'))
    voltage_difference = Quantity(
        type=np.dtype(np.float64),
        unit=('V'))
    j = Quantity(
        type=np.dtype(np.float64),
        description='current density',
        unit=('A/cm^2'))
    current_density_string = Quantity(
        type=str,
        description='string representation of j (needed for terms in explore view)',)
    experiment_duration = Quantity(
        type=np.dtype(np.float64),
        unit=('hr'))
    reaction_type = Quantity(
        type=str,
        description='At the moment only OER CP is supported. In the future maybe also NRR CP.')
    samples = SubSection(
        section_def=CompositeSystemReference,
        repeats=True,)

    def normalize(self, archive, logger):
        self.current_density_string = format(self.j, '~')
        super(CPOERAnalysisResult, self).normalize(archive, logger)


class CPAnalysis(Analysis):
    m_def = Section(label_quantity='name')

    inputs = Analysis.inputs.m_copy()
    inputs.section_def = CPOERReference

    outputs = Analysis.outputs.m_copy()
    outputs.section_def = CPOERAnalysisResult

    def normalize(self, archive, logger):
        refs = find_all_cp_in_upload(archive, archive.metadata.upload_id)
        self.inputs = [CPOERReference(reference=ref) for ref in refs]

        if self.inputs is not None and len(self.inputs) >= 2:
            first_oer_run = self.inputs[0].reference
            last_oer_run = self.inputs[-1].reference

            for cp_entry in self.inputs:
                cp_entry.name = cp_entry.reference.data_file
                if cp_entry.reference.datetime < first_oer_run.datetime:
                    first_oer_run = cp_entry.reference
                if cp_entry.reference.datetime > last_oer_run.datetime:
                    last_oer_run = cp_entry.reference

            voltage_avg_first5 = np.mean(np.array(first_oer_run.voltage[:5]))
            voltage_avg_last5 = np.mean(np.array(last_oer_run.voltage[-5:]))
            voltage_difference = voltage_avg_first5 - voltage_avg_last5

            current_ma = first_oer_run.properties.step_1_current * 1000  # convert A to mA
            current_density = current_ma / first_oer_run.properties.sample_area

            experiment_duration = 7200  #TODO calculate
            #experiment_duration = cycle_number * (toer + trecover)

            for sample in first_oer_run.samples:
                if sample.reference.chemical_composition_or_formulas:
                    if not archive.results:
                        archive.results = Results()
                    if not archive.results.material:
                        archive.results.material = Material()
                    try:
                        from nomad.atomutils import Formula
                        formula = Formula(sample.reference.chemical_composition_or_formulas)
                        formula.populate(section=archive.results.material)
                    except Exception as e:
                        logger.warn('Could not analyse material', exc_info=e)

            self.outputs = [CPOERAnalysisResult(name=first_oer_run.name,
                                                voltage_avg_first5=voltage_avg_first5,
                                                voltage_avg_last5=voltage_avg_last5,
                                                voltage_difference=voltage_difference,
                                                j=current_density,
                                                experiment_duration=experiment_duration,
                                                reaction_type=first_oer_run.method,
                                                samples=first_oer_run.samples)]
            self.outputs[0].normalize(archive, logger)
        super(CPAnalysis, self).normalize(archive, logger)


def find_all_cp_in_upload(data_archive, upload_id):
    from nomad.search import search
    from nomad.app.v1.models import MetadataPagination

    # search for all UVvisConcentrationDetection archives
    query = {
        'section_defs.definition_qualified_name': 'baseclasses.chemical_energy.chronopotentiometry.Chronopotentiometry',
        'results.eln.methods': 'OER Chronopotentiometry',
        'upload_id': upload_id
    }
    pagination = MetadataPagination()
    pagination.page_size = 800
    search_result = search(owner='all', query=query, pagination=pagination,
                           user_id=data_archive.metadata.main_author.user_id)

    refs = []
    for res in search_result.data:
        refs.append(get_reference(upload_id, res["entry_id"]))

    return refs
