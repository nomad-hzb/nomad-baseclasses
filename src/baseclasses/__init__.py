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

import json

import hdf5plugin
import numpy as np
from nomad.datamodel.data import ArchiveSection
from nomad.datamodel.metainfo.basesections import (
    Collection,
    CompositeSystem,
    CompositeSystemReference,
    Entity,
    Experiment,
    ExperimentStep,
    Measurement,
    Process,
    PubChemPureSubstanceSection,
    PureSubstanceSection,
)
from nomad.datamodel.metainfo.eln import ElnWithFormulaBaseSection
from nomad.datamodel.results import Material, Results
from nomad.metainfo import Datetime, MEnum, Quantity, Reference, Section, SectionProxy, SubSection

from .atmosphere import Atmosphere
from .customreadable_identifier import ReadableIdentifiersCustom
from .helper.add_solar_cell import add_solar_cell
from .helper.utilities import get_processes, update_archive


class PubChemPureSubstanceSectionCustom(PubChemPureSubstanceSection):
    """
    A section for pure substances existing as "compounds" in the PubChem database
    and for tracking substances provided by suppliers
    """
    product_number = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'),
        description='Product Number, as defined by materials sent by the suppliers',
    )

    lot_number = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'),
        description='LOT, Experiment or Batch Number, as defined by suppliers',
    )

    product_volume = Quantity(
        type=np.dtype(np.float64),
        unit=('ml'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='ml'),
        description = 'Delivered Product Volume'
    )

    product_weight = Quantity(
        type=np.dtype(np.float64),
        unit=('g'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='g'),
        description = 'Delivered Product Weight'
    )

    shipping_date = Quantity(type=Datetime, a_eln=dict(component='DateTimeEditQuantity')
                             )

    opening_date = Quantity(type=Datetime, a_eln=dict(component='DateTimeEditQuantity'))

    supplier = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'),
        description = 'Partner/Company that supplies the product to the end user'
    )
    
    product_description = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'),
    )

    load_data = Quantity(
        type=bool,
        default=True,
        a_eln=dict(
            component='BoolEditQuantity',
        ),
    )

    def normalize(self, archive, logger):
        if self.load_data:
            super().normalize(archive, logger)
        else:
            super(PubChemPureSubstanceSection, self).normalize(archive, logger)


class Batch(Collection):
    export_batch_ids = Quantity(
        type=bool, default=False, a_eln=dict(component='ActionEditQuantity')
    )

    csv_export_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'),
    )

    entities = Collection.entities.m_copy()
    entities.a_eln = dict(label='Samples')

    batch_id = SubSection(section_def=ReadableIdentifiersCustom)

    def normalize(self, archive, logger):
        super().normalize(archive, logger)

        if self.export_batch_ids and self.entities:
            self.export_batch_ids = False
            # try:
            samples = []
            for sample in self.entities:
                sample_id = (
                    sample.reference.lab_id
                    if sample.reference is not None
                    else self.lab_id
                )
                sample_entry_id = sample.reference.m_parent.entry_id
                samples.append(
                    [sample_id]
                    + [p[1] for p in get_processes(archive, sample_entry_id)]
                )
            import pandas as pd

            df = pd.DataFrame(samples)
            export_file_name = f'list_of_ids_{self.name}.csv'
            with archive.m_context.raw_file(export_file_name, 'w') as outfile:
                df.to_csv(outfile.name)
            self.csv_export_file = export_file_name
            # except BaseException:
            #     pass


class SampleReference(CompositeSystemReference):
    sample_type = Quantity(
        type=MEnum('Sample', 'Library'),
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
        ),
    )

    create_sample = Quantity(
        type=bool, default=False, a_eln=dict(component='ActionEditQuantity')
    )


class ExperimentalStepData(ArchiveSection):
    data_folder = Quantity(type=str, a_eln=dict(component='StringEditQuantity'))

    data_files = Quantity(
        type=str,
        shape=['*'],
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'),
    )


class SingleSampleExperimentStep(ExperimentStep):
    m_def = Section(
        label_quantity='name',
        a_eln=dict(
            hide=['lab_id'],
            properties=dict(
                order=[
                    'name',
                    'method',
                    'method_type',
                    'create_experimental_step',
                    'activity',
                ]
            ),
        ),
    )

    method = Quantity(
        type=str,
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=[
                    'XRR',
                    'XRD',
                    'XRF',
                    'Ellipsometry',
                    'Sputtering',
                    'SEM_Merlin',
                    'Measurement',
                    'Synthesis',
                    'Dektak',
                    'TGA',
                    'PECVD',
                    'Catalytic_Reaction',
                ]
            ),
        ),
    )

    method_type = Quantity(
        type=MEnum('Single', 'X-Y'),
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
        ),
    )

    create_experimental_step = Quantity(
        type=bool, default=False, a_eln=dict(component='ActionEditQuantity')
    )

    with_last_step = Quantity(
        type=bool, default=False, a_eln=dict(component='BoolEditQuantity')
    )

    # data = SubSection(
    #     section_def=ExperimentalStepData)


class SingleSampleExperiment(Experiment):
    sample = SubSection(
        links=['https://purl.archive.org/tfsco/TFSCO_00005000'],
        section_def=SampleReference,
        description="""
        The samples as that have undergone the process.
        """,
    )

    steps = SubSection(
        section_def=SingleSampleExperimentStep,
        description="""
        An ordered list of all the dependant steps that make up this Experiment.
        """,
        repeats=True,
    )


class SingleLibraryMeasurement(ArchiveSection):
    m_def = Section(label_quantity='name')
    name = Quantity(type=str)

    position_x = Quantity(
        links=['http://purl.obolibrary.org/obo/PATO_0000140'],
        type=np.dtype(np.float64),
        unit=('mm'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mm'),
    )

    position_y = Quantity(
        links=['http://purl.obolibrary.org/obo/PATO_0000140'],
        type=np.dtype(np.float64),
        unit=('mm'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mm'),
    )

    position_z = Quantity(
        type=np.dtype(np.float64),
        unit=('mm'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mm'),
    )

    data_file = Quantity(
        type=str,
        shape=['*'],
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'),
    )

    # position_x_relative = Quantity(
    #     type=np.dtype(np.float64),
    #     a_eln=dict(component='NumberEditQuantity')
    # )

    # position_y_relative = Quantity(
    #     type=np.dtype(np.float64),
    #     a_eln=dict(component='NumberEditQuantity'))

    # position_index = Quantity(
    #     type=np.dtype(np.int64),
    #     a_eln=dict(component='NumberEditQuantity')
    # )

    def normalize(self, archive, logger):
        super().normalize(archive, logger)
        if self.position_x is not None and self.position_y is not None:
            self.name = f'{self.position_x},{self.position_y}'


class LibrarySample(CompositeSystem):
    grid_information = Quantity(type=str, a_eln=dict(component='StringEditQuantity'))

    library_id = SubSection(section_def=ReadableIdentifiersCustom)


class BaseProcess(Process):
    # is_standard_process = Quantity(
    #     type=bool,
    #     default=False,
    #     a_eln=dict(component='BoolEditQuantity')
    # )

    present = Quantity(
        type=bool, default=True, a_eln=dict(component='BoolEditQuantity')
    )

    batch = Quantity(
        type=Reference(Batch.m_def), a_eln=dict(component='ReferenceEditQuantity')
    )

    positon_in_experimental_plan = Quantity(
        type=np.dtype(np.float64), a_eln=dict(component='NumberEditQuantity')
    )

    atmosphere = SubSection(
        links=['http://purl.obolibrary.org/obo/RO_0000057'],
        section_def=Atmosphere,
    )

    def normalize(self, archive, logger):
        if not self.positon_in_experimental_plan:
            try:
                self.positon_in_experimental_plan = float(
                    archive.metadata.mainfile.split('_')[0]
                )
            except Exception:
                pass

        if self.batch:
            self.samples = self.batch.entities

        if self.samples:
            for s in self.samples:
                s.normalize(archive, logger)

        super().normalize(archive, logger)


class StandardSample(Entity):
    processes = Quantity(
        links=['http://purl.obolibrary.org/obo/BFO_0000015'],
        type=Reference(BaseProcess.m_def),
        shape=['*'],
        a_eln=dict(component='ReferenceEditQuantity'),
    )

    def normalize(self, archive, logger):
        super().normalize(archive, logger)
        # checked_processesocesses = []
        # if self.processes:
        #     for process in self.processes:
        #         if process.is_standard_process:
        #             checked_processes.append(process)
        # self.processes = checked_processes


class LayerProperties(ArchiveSection):
    m_def = Section(
        links=['https://purl.archive.org/tfsco/TFSCO_00000007'],
        label_quantity='layer_material_name',
    )

    layer_type = Quantity(
        links=['https://purl.archive.org/tfsco/TFSCO_00000007'],
        type=str,
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=[
                    'Hole Transport Layer',
                    'Electron Transport Layer',
                    'Absorber Layer',
                    'Buffer Layer',
                    'A.R.C.',
                    'Back reflection',
                    'Down conversion',
                    'Encapsulation',
                    'Light management',
                    'Upconversion',
                    'Back Contact',
                    'Passivation',
                    'Carbon Paste Layer',
                    'Substrate Conductive Layer',
                ]
            ),
        ),
    )

    layer_material_name = Quantity(
        type=str,
        # links=["https://www.helmholtz-berlin.de"],
        description=(
            'The chemical formula using common abreviations. '
            'This will be used to set layer material, if not set, e.g. MAPbI3.'
        ),
        a_eln=dict(component='StringEditQuantity'),
    )

    layer_material = Quantity(
        type=str,
        description=(
            'The chemical formula of the layer. This will be used directly and '
            'indirectly in the search. The formula will be used itself as well as '
            'the extracted chemical elements.'
        ),  # a_eln=dict(
        # component='StringEditQuantity')
    )

    layer_thickness = Quantity(
        # links=[],
        type=np.dtype(np.float64),
        description=('The thickness of the sample, either measured or assumed.'),
        unit=('nm'),
        shape=[],
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='nm'),
    )

    layer_transmission = Quantity(
        type=np.dtype(np.float64),
        description=('Percentage of light that gets transmitted through the layer.'),
        a_eln=dict(
            component='NumberEditQuantity', props=dict(minValue=0)
        ),  # is described in percentage
    )

    layer_morphology = Quantity(
        # links=[],
        type=str,
        description=('A description of the morphology of the film'),
        shape=[],
        a_eln=dict(component='StringEditQuantity'),
    )
    layer_sheet_resistance = Quantity(
        type=np.dtype(np.float64),
        unit='ohm',
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='ohm',
            props=dict(
                minValue=0, description='Sheet resistance in ohms per square (Ω/□)'
            ),
        ),
    )


class LayerDeposition(BaseProcess):
    m_def = Section(
        links=['https://purl.archive.org/tfsco/TFSCO_00000067'], label_quantity='layer'
    )

    layer = SubSection(
        links=['http://purl.obolibrary.org/obo/RO_0002234'],
        section_def=LayerProperties,
        repeats=True,
    )

    def normalize(self, archive, logger):
        super().normalize(archive, logger)

        if not archive.results:
            archive.results = Results()
        if not archive.results.material:
            archive.results.material = Material()

        if self.layer is None:
            return
        device_stack = []
        hole_transport_layer = []
        electron_transport_layer = []
        back_contact = []
        absorber = []
        elements_final = []
        add_solar_cell(archive)
        for layer in self.layer:
            layer_material_name = layer.layer_material_name
            if layer_material_name:
                layer.layer_material = ''

                from .helper.formula_normalizer import PerovskiteFormulaNormalizer

                formulas = [
                    PerovskiteFormulaNormalizer(
                        formula.replace('x', '').strip()
                    ).clean_formula()
                    for formula in layer_material_name.split(',')
                ]
                try:
                    elements = [f for formula in formulas for f in formula[1]]
                    print(elements)
                    elements_final.extend(list(set(elements)))
                    lm_tmp = (
                        ','.join([formulas[i][0] for i, _ in enumerate(formulas)])
                        if isinstance(formulas, list)
                        else None
                    )
                    layer.layer_material = lm_tmp

                except BaseException as e:
                    print(e)

            # from nomad.atomutils import Formula
            layer_material = layer.layer_material
            # if layer_material:
            #     try:
            #         formula = Formula(layer_material)
            #         formula.populate(section=archive.results.material)
            #     except Exception as e:
            #         logger.warn('could not analyse layer material', exc_info=e)

            layer_type = layer.layer_type
            if layer_type:
                if layer_material or layer_material_name:
                    layer_material_name_tmp = (
                        layer_material_name if layer_material_name else layer_material
                    )

                    if layer_type:
                        device_stack.append(layer_material_name_tmp)
                    if layer_type == 'Hole Transport Layer':
                        hole_transport_layer.append(layer_material_name_tmp)
                    if layer_type == 'Electron Transport Layer':
                        electron_transport_layer.append(layer_material_name_tmp)
                    if layer_type == 'Back Contact':
                        back_contact.append(layer_material_name_tmp)
                    if layer_type == 'Absorber Layer':
                        absorber.append(layer_material_name_tmp)

                if layer_type == 'Absorber Layer':
                    archive.results.properties.optoelectronic.solar_cell.absorber_fabrication = [
                        self.method
                    ]
        archive.results.properties.optoelectronic.solar_cell.device_stack = device_stack
        archive.results.properties.optoelectronic.solar_cell.hole_transport_layer = (
            hole_transport_layer
        )
        archive.results.properties.optoelectronic.solar_cell.electron_transport_layer = electron_transport_layer
        archive.results.properties.optoelectronic.solar_cell.back_contact = back_contact
        archive.results.properties.optoelectronic.solar_cell.absorber = absorber
        try:
            archive.results.material.elements = elements_final
        except Exception:
            pass


class BaseMeasurement(Measurement):
    m_def = Section(links=['http://purl.obolibrary.org/obo/OBI_0000070'])

    atmosphere = SubSection(
        links=['http://purl.obolibrary.org/obo/RO_0000057'],
        section_def=Atmosphere,
        repeats=True,
    )

    def normalize(self, archive, logger):
        if self.samples:
            for s in self.samples:
                s.normalize(archive, logger)
        super().normalize(archive, logger)


class LibraryMeasurement(BaseMeasurement):
    measurements = SubSection(section_def=SingleLibraryMeasurement, repeats=True)

    def normalize(self, archive, logger):
        super().normalize(archive, logger)


# class MeasurementOnBatch(Measurement):

#     samples = Quantity(
#         type=Reference(Batch.m_def),
#         shape=['*'],
#         a_eln=dict(component='ReferenceEditQuantity'))

#     def normalize(self, archive, logger):
#         super(MeasurementOnBatch, self).normalize(archive, logger)
