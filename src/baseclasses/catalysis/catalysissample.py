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
)
from nomad.datamodel.results import Material
from nomad.metainfo import Quantity, Reference, SubSection

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


class CatalysisSample(CompositeSystem):
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
