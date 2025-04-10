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
from nomad.datamodel.metainfo.basesections import (
    CompositeSystem,
    CompositeSystemReference,
    Measurement,
)
from nomad.datamodel.results import Material
from nomad.metainfo import Quantity, Reference, Section, SubSection
from nomad_material_processing.combinatorial import (
    CombinatorialLibrary,
    CombinatorialSample,
)

from .. import LibrarySample


def collectSampleData(archive):
    # This function gets all archives whcih reference this archive.
    # Iterates over them and selects relevant data for the
    # result section of the solarcellsample
    # At the end the synthesis steps are ordered
    # returns a dictionary containing synthesis process, JV and EQE information

    from nomad import files
    from nomad.app.v1.models import MetadataPagination
    from nomad.search import search

    # search for all archives referencing this archive
    query = {
        'entry_references.target_entry_id': archive.metadata.entry_id,
    }
    pagination = MetadataPagination()
    pagination.page_size = 100
    search_result = search(
        owner='all',
        query=query,
        pagination=pagination,
        user_id=archive.metadata.main_author.user_id,
    )
    entry = {}
    for res in search_result.data:
        try:
            # Open Archives
            with files.UploadFiles.get(upload_id=res['upload_id']).read_archive(
                entry_id=res['entry_id']
            ) as arch:
                entry_id = res['entry_id']
                entry.update({entry_id: {}})
                try:
                    entry[entry_id]['elements'] = arch[entry_id]['results']['material'][
                        'elements'
                    ]
                except BaseException:
                    entry[entry_id]['elements'] = []

        except Exception as e:
            print('Error in processing data: ', e)

    return entry


class CatalysisSubstrate(ArchiveSection):
    substrate_type = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=[
                    'glassy carbon',
                    'ITO on glass',
                    'Platinum',
                    'glass',
                    'silicon wafer',
                ]
            ),
        ),
    )

    substrate_dimension = Quantity(
        type=str,
        a_eln=dict(
            component='StringEditQuantity',
        ),
    )


class CombinatorialProperty(ArchiveSection):
    model = Quantity(
        type=str,
        description="""
        The model/calculation method used to calculate the property.
        """,
    )

    analysis = Quantity(
        type=str,
        description="""
        The model used to calculate the property.
        """,
        a_browser=dict(adaptor='RawFileAdaptor'),
    )

    measurements = Quantity(
        type=Reference(Measurement.m_def),
        description="""
        List of measurements used to determine the property.
        """,
        shape=['*'],
    )


class SynthesisVariation(ArchiveSection):
    variation_name = Quantity(
        type=str,
        description="""
        The name of a paramter which is varied over a campaign
        """,
    )

    variation_value_number = Quantity(
        type=float,
        description="""
        The numerical value of a continous paramter which is varied over a campaign
        """,
    )

    variation_value_string = Quantity(
        type=str,
        description="""
        The string value of a categorical paramter which is varied over a campaign
        """,
    )


class XRayDiffraction(CombinatorialProperty):
    def derive_n_values(self):
        if self.intensity is not None:
            return len(self.intensity)
        if self.scattering_vector is not None:
            return len(self.scattering_vector)
        else:
            return 0

    n_values = Quantity(type=int, derived=derive_n_values)

    intensity = Quantity(
        type=float,
        description="""
        The intensity of the X-ray diffraction pattern.
        """,
        shape=['n_values'],
    )
    scattering_vector = Quantity(
        type=float,
        description="""
        The corresponding scattering vector values of the measured X-ray diffraction
        pattern.
        """,
        shape=['n_values'],
        unit='1/nm',
    )


class Thickness(CombinatorialProperty):
    value = Quantity(
        type=float,
        description="""
        The (average) thickness of the sample.
        """,
        unit='m',
    )


class Formula(CombinatorialProperty):
    value = Quantity(
        type=str,
        description="""
        The molecular formula of the sample.
        """,
    )


class CatalysisXYSample(CombinatorialSample):
    synthesis_variation = SubSection(section_def=SynthesisVariation, repeats=True)
    formula = SubSection(section_def=Formula)
    thickness = SubSection(section_def=Thickness)
    xray_diffraction = SubSection(section_def=XRayDiffraction)


class CatalysisSample(CombinatorialLibrary):
    """Base class for a catalysis sample"""
    m_def = Section(links=['https://w3id.org/nfdi4cat/voc4cat_0000194']) #annotation to voc4cat

    active_area = Quantity(
        type=np.dtype(np.float64),
        unit=('cm^2'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='cm^2'),
    )

    substrate = SubSection(section_def=CatalysisSubstrate)

    parent = SubSection(section_def=CompositeSystemReference)

    def normalize(self, archive, logger):
        super().normalize(archive, logger)

        if not archive.results.material:
            archive.results.material = Material()
        archive.results.material.elements = []

        result_data = collectSampleData(archive)
        for _, process in result_data.items():
            if not process['elements']:
                continue
            archive.results.material.elements.extend(process['elements'])
        archive.results.material.elements = list(set(archive.results.material.elements))


class CatalysisLibrary(LibrarySample):
    substrate = Quantity(
        type=Reference(CatalysisSubstrate.m_def),
        a_eln=dict(component='ReferenceEditQuantity'),
    )

    def normalize(self, archive, logger):
        super().normalize(archive, logger)
