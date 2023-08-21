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
from nomad.metainfo import (
    Quantity,
    Reference,
    Section,
    SectionProxy,
    SubSection)

from nomad.datamodel.metainfo.eln import (
    ElnWithFormulaBaseSection)

from nomad.datamodel.metainfo.basesections import (
    CompositeSystem,
    Collection,
    Process,
    Measurement,
    Entity,
    CompositeSystemReference
)

from nomad.datamodel.results import Results, Material
from nomad.datamodel.data import ArchiveSection


from .helper.add_solar_cell import add_solar_cell

from .solution import Solution
from .customreadable_identifier import ReadableIdentifiersCustom


class Batch(Collection):

    export_batch_ids = Quantity(
        type=bool,
        default=False,
        a_eln=dict(component='BoolEditQuantity')
    )

    csv_export_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor')
    )
    # for legacy reasons
    samples = Quantity(
        type=Reference(CompositeSystem),
        shape=['*'],
        descriptions='The samples in the batch.',
        a_eln=dict(component='ReferenceEditQuantity')
    )

    entities = Collection.entities.m_copy()
    entities.label = "Samples"

    batch_id = SubSection(
        section_def=ReadableIdentifiersCustom)

    def normalize(self, archive, logger):
        super(Batch, self).normalize(archive, logger)

        if self.samples and self.entities is None:
            entities = []
            for sample in self.samples:
                entities.append(CompositeSystemReference(reference=sample))
            self.entities = entities

        if self.export_batch_ids and self.entities is not None:
            self.export_batch_ids = False
            try:
                samples = []
                for sample in self.entities:
                    sample_id = sample.reference.lab_id if sample.reference is not None else self.lab_id
                    sample_name = sample.reference.name
                    samples.append([sample_id, sample_name])
                import pandas as pd
                df = pd.DataFrame(samples, columns=[
                                  "sample_id", "sample_name"])
                export_file_name = f"list_of_ids_{self.name}.csv"
                with archive.m_context.raw_file(export_file_name, 'w') as outfile:
                    df.to_csv(outfile.name)
                self.csv_export_file = export_file_name
            except BaseException:
                pass


class BaseProcess(Process):

    # is_standard_process = Quantity(
    #     type=bool,
    #     default=False,
    #     a_eln=dict(component='BoolEditQuantity')
    # )

    present = Quantity(
        type=bool,
        default=True,
        a_eln=dict(component='BoolEditQuantity')
    )

    batch = Quantity(
        type=Reference(Batch.m_def),
        a_eln=dict(component='ReferenceEditQuantity'))

    previous_process = Quantity(
        type=Reference(SectionProxy("BaseProcess")),
        shape=['*'],
        a_eln=dict(component='ReferenceEditQuantity'))

    def normalize(self, archive, logger):
        super(BaseProcess, self).normalize(archive, logger)

        if self.batch:
            self.samples = self.batch.entities


class Deposition(BaseProcess, ElnWithFormulaBaseSection):
    function = Quantity(
        type=str,
        shape=[],
        a_eln=dict(
            component='StringEditQuantity'
        ))

    def normalize(self, archive, logger):
        super(Deposition, self).normalize(archive, logger)


class StandardSample(Entity):

    processes = Quantity(
        type=Reference(BaseProcess.m_def),
        shape=['*'],
        a_eln=dict(component='ReferenceEditQuantity'))

    def normalize(self, archive, logger):
        super(StandardSample, self).normalize(archive, logger)
        # checked_processesocesses = []
        # if self.processes:
        #     for process in self.processes:
        #         if process.is_standard_process:
        #             checked_processes.append(process)
        # self.processes = checked_processes


class LayerProperties(ArchiveSection):
    layer_type = Quantity(
        type=str,
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=['Hole Transport Layer',
                             'Electron Transport Layer',
                             'Absorber Layer',
                             'Buffer Layer', 'A.R.C.',
                             'Back reflection',
                             'Down conversion',
                             'Encapsulation',
                             'Light management',
                             'Upconversion',
                             'Back Contact',
                             'Passivation'])
        ))

    layer_material_name = Quantity(
        type=str,
        # links=["https://www.helmholtz-berlin.de"],
        description=(
            'The chemical formula using common abreviations. This will be used to set layer material, if not set, e.g. MAPbI3.'),
        a_eln=dict(component='StringEditQuantity'))

    layer_material = Quantity(
        type=str, description=(
            'The chemical formula of the layer. This will be used directly and '
            'indirectly in the search. The formula will be used itself as well as '
            'the extracted chemical elements.'),  # a_eln=dict(
        # component='StringEditQuantity')
    )


class LayerDeposition(BaseProcess):
    m_def = Section(label_quantity='layer')

    layer = SubSection(section_def=LayerProperties)

    def normalize(self, archive, logger):
        super(LayerDeposition, self).normalize(archive, logger)

        if not archive.results:
            archive.results = Results()
        if not archive.results.material:
            archive.results.material = Material()

        if self.layer is None:
            return

        layer_material_name = self.layer.layer_material_name
        if layer_material_name:
            self.layer.layer_material = ''
            material = archive.results.material

            from .helper.formula_normalizer import PerovskiteFormulaNormalizer
            formulas = [PerovskiteFormulaNormalizer(
                formula.strip()).clean_formula()
                for formula in layer_material_name.split(",")]
            try:
                elements = [f for formula in formulas for f in formula[1]]
                material.elements = []
                material.elements = list(set(elements))
                lm_tmp = ",".join([formulas[i][0] for i, _ in enumerate(formulas)]
                                  ) if isinstance(formulas, list) else None
                self.layer.layer_material = lm_tmp

            except BaseException as e:
                print(e)

        from nomad.atomutils import Formula
        layer_material = self.layer.layer_material
        if layer_material:
            try:
                formula = Formula(layer_material)
                formula.populate(section=archive.results.material)
            except Exception as e:
                logger.warn('could not analyse layer material', exc_info=e)

        layer_type = self.layer.layer_type
        if layer_type:
            add_solar_cell(archive)

            if layer_material or layer_material_name:

                layer_material_name_tmp = layer_material_name if layer_material_name else layer_material

                if layer_type:
                    archive.results.properties.optoelectronic.solar_cell.device_stack \
                        = [layer_type + " " + layer_material_name_tmp]
                if layer_type == 'Hole Transport Layer':
                    archive.results.properties.optoelectronic.solar_cell.hole_transport_layer \
                        = [layer_material_name_tmp]
                if layer_type == 'Electron Transport Layer':
                    archive.results.properties.optoelectronic.solar_cell.electron_transport_layer \
                        = [layer_material_name_tmp]
                if layer_type == 'Back Contact':
                    archive.results.properties.optoelectronic.solar_cell.back_contact \
                        = [layer_material_name_tmp]
                if layer_type == 'Absorber Layer':
                    archive.results.properties.optoelectronic.solar_cell.absorber \
                        = [layer_material_name_tmp]

            if layer_type == 'Absorber Layer':
                archive.results.properties.optoelectronic.solar_cell.absorber_fabrication \
                    = [self.method]


class BaseMeasurement(Measurement):

    solution = Quantity(
        type=Reference(Solution.m_def),
        shape=['*'],
        a_eln=dict(component='ReferenceEditQuantity'))

    samples2 = Quantity(
        type=Reference(CompositeSystem.m_def),
        shape=['*'],
        a_eln=dict(component='ReferenceEditQuantity'))

    def normalize(self, archive, logger):
        super(BaseMeasurement, self).normalize(archive, logger)
        if self.samples2 is None:
            self.samples2 = self.samples
            self.samples = None
        if self.samples2 and self.samples is None:
            samples = []
            for sample in self.samples2:
                samples.append(CompositeSystemReference(reference=sample))
            print(samples)
            # self.samples = samples


# class MeasurementOnBatch(Measurement):

#     samples = Quantity(
#         type=Reference(Batch.m_def),
#         shape=['*'],
#         a_eln=dict(component='ReferenceEditQuantity'))

#     def normalize(self, archive, logger):
#         super(MeasurementOnBatch, self).normalize(archive, logger)
