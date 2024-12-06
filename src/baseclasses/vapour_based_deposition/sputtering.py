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
from nomad.datamodel.results import Material
from nomad.metainfo import MEnum, Quantity, Reference, Section, SubSection

from baseclasses import PubChemPureSubstanceSectionCustom

from .. import LayerDeposition
from ..chemical import Chemical


class SputteringProcess(ArchiveSection):
    target = Quantity(
        links=['https://purl.archive.org/tfsco/TFSCO_00002035'],
        type=Reference(Chemical.m_def),
        a_eln=dict(component='ReferenceEditQuantity'),
    )

    target_2 = SubSection(section_def=PubChemPureSubstanceSectionCustom)

    gas_2 = SubSection(section_def=PubChemPureSubstanceSectionCustom)

    thickness = Quantity(
        links=['http://purl.obolibrary.org/obo/PATO_0000915'],
        type=np.dtype(np.float64),
        unit=('nm'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='nm',
            props=dict(minValue=0),
        ),
    )

    gas = Quantity(
        links=['http://purl.obolibrary.org/obo/CHEBI_59999'],
        type=Reference(Chemical.m_def),
        a_eln=dict(component='ReferenceEditQuantity'),
    )

    source = Quantity(
        links=['https://purl.archive.org/tfsco/TFSCO_00002035'],
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=[
                    '1',
                    '2',
                    '3',
                    '4',
                ]
            ),
        ),
    )

    pressure = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0001025',
            'https://purl.archive.org/tfsco/TFSCO_00005040',
        ],
        type=np.dtype(np.float64),
        unit=('mbar'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mbar',
            props=dict(minValue=0),
        ),
    )

    capman_pressure = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0001025',
            'https://purl.archive.org/tfsco/TFSCO_00005040',
        ],
        type=np.dtype(np.float64),
        unit=('mmmHg'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mmmHg',
            props=dict(minValue=0),
        ),
    )

    temperature = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0000146',
            'https://purl.archive.org/tfsco/TFSCO_00002071',
        ],
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'),
    )

    burn_in_time = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0000165',
            'https://purl.archive.org/tfsco/TFSCO_00005085',
        ],
        type=np.dtype(np.float64),
        unit=('s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='s',
            props=dict(minValue=0),
        ),
    )

    deposition_time = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0000165',
            'https://purl.archive.org/tfsco/TFSCO_00005085',
        ],
        type=np.dtype(np.float64),
        unit=('s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='s',
            props=dict(minValue=0),
        ),
    )

    power = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0001024',
            'https://purl.archive.org/tfsco/TFSCO_00002104',
        ],
        type=np.dtype(np.float64),
        unit=('W'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='W',
            props=dict(minValue=0),
        ),
    )

    voltage = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0001464',
            'https://purl.archive.org/tfsco/TFSCO_00005005',
        ],
        type=np.dtype(np.float64),
        unit=('V'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='V'),
    )

    gas_flow_rate = Quantity(
        links=[
            'https://purl.archive.org/tfsco/TFSCO_00002114',
            'https://purl.archive.org/tfsco/TFSCO_00002108',
        ],
        type=np.dtype(np.float64),
        unit=('cm**3/minute'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='cm**3/minute',
            props=dict(minValue=0),
        ),
    )

    rotation_rate = Quantity(
        type=np.dtype(np.float64),
        unit=('rpm'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='rpm',
            props=dict(minValue=0),
        ),
    )


class Sputtering(LayerDeposition):
    """Base class for evaporation of a sample"""

    m_def = Section(
        links=['http://purl.obolibrary.org/obo/CHMO_0001364'],
    )

    processes = SubSection(section_def=SputteringProcess, repeats=True)

    def normalize(self, archive, logger):
        super().normalize(archive, logger)

        self.method = 'Sputtering'


class TargetProperties(ArchiveSection):
    m_def = Section(
        label_quantity='name',
    )
    name = Quantity(type=str)

    material = SubSection(
        links=['https://purl.archive.org/tfsco/TFSCO_00002035'],
        section_def=PubChemPureSubstanceSectionCustom,
    )

    position = Quantity(
        type=str,
    )

    angle = Quantity(
        type=np.dtype(np.float64),
        unit=('degree'),
    )

    rf_dc = Quantity(
        type=MEnum('RF', 'DC'), a_eln=dict(component='RadioEnumEditQuantity')
    )

    def normalize(self, archive, logger):
        if self.material and self.material.molecular_formula:
            self.name = self.material.molecular_formula


class MultiTargetSputteringProcess(ArchiveSection):
    m_def = Section(
        label_quantity='step_number',
    )
    step_number = Quantity(type=str)

    gas = SubSection(
        links=['http://purl.obolibrary.org/obo/CHEBI_59999'],
        section_def=PubChemPureSubstanceSectionCustom,
    )

    orientation = Quantity(
        type=np.dtype(np.float64),
        unit=('degree'),
    )

    sputter_pressure = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0001025',
            'https://purl.archive.org/tfsco/TFSCO_00005040',
        ],
        type=np.dtype(np.float64),
        unit=('mbar'),
        minValue=0,
    )

    substrate_temperature = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0000146',
            'https://purl.archive.org/tfsco/TFSCO_00002071',
        ],
        type=np.dtype(np.float64),
        unit=('°C'),
    )

    ramp = Quantity(
        type=np.dtype(np.float64),
        unit=('°C/minute'),
    )

    deposition_time = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0000165',
            'https://purl.archive.org/tfsco/TFSCO_00005085',
        ],
        type=np.dtype(np.float64),
        unit=('s'),
        minValue=0,
    )

    power = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0001024',
            'https://purl.archive.org/tfsco/TFSCO_00002104',
        ],
        type=np.dtype(np.float64),
        shape=['*'],
        unit='W',
    )

    rotation_rate = Quantity(
        type=np.dtype(np.float64),
        unit=('degree/s'),
        minValue=0,
    )

    z_position = Quantity(
        type=np.dtype(np.float64),
    )

    flow_rate = Quantity(
        type=np.dtype(np.float64),
        unit=('mL/minute'),
    )


class MultiTargetSputteringObservables(ArchiveSection):
    m_def = Section(
        label_quantity='step_number',
    )
    step_number = Quantity(type=str)

    base_pressure = Quantity(type=np.dtype(np.float64), unit=('mbar'), minValue=0)

    temperature = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0000146',
            'http://purl.obolibrary.org/obo/XCO_0000058',
        ],
        type=np.dtype(np.float64),
        unit=('°C'),
    )

    bias_voltage = Quantity(type=np.dtype(np.float64), shape=['*'], unit='V')

    bias_current = Quantity(type=np.dtype(np.float64), shape=['*'], unit='A')

    notes = Quantity(
        type=str,
        description='Any information that cannot be captured in the other fields.',
        a_eln=dict(component='RichTextEditQuantity'),
    )


class MultiTargetSputtering(LayerDeposition):
    """Base class for evaporation of a sample"""

    m_def = Section(
        links=['http://purl.obolibrary.org/obo/CHMO_0001364'],
    )

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'),
    )

    substrate = Quantity(type=str, shape=[], a_eln=dict(component='StringEditQuantity'))

    sample_owner = Quantity(
        type=str, shape=[], a_eln=dict(component='StringEditQuantity')
    )

    process_user = Quantity(
        type=str, shape=[], a_eln=dict(component='StringEditQuantity')
    )

    sample_lab_label = Quantity(
        type=str, shape=[], a_eln=dict(component='StringEditQuantity')
    )

    holder = Quantity(type=str, shape=[], a_eln=dict(component='StringEditQuantity'))

    process_properties = SubSection(
        section_def=MultiTargetSputteringProcess, repeats=True
    )

    targets = SubSection(section_def=TargetProperties, repeats=True)

    observables = SubSection(section_def=MultiTargetSputteringObservables, repeats=True)

    def normalize(self, archive, logger):
        self.method = 'Multi Target Sputtering'

        super().normalize(archive, logger)
        if self.targets and self.observables:
            elements = []
            for step in self.observables:
                if len(self.targets) != len(step.bias_voltage):
                    continue
                active = step.bias_voltage > 0
                active_targets = [t for i, t in enumerate(self.targets) if active[i]]
                new_elements = [v.material.molecular_formula for v in active_targets]
                elements.extend(new_elements)

            if not archive.results.material:
                archive.results.material = Material()
            archive.results.material.elements = list(set(elements))
