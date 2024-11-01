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
from nomad.metainfo import Quantity, Reference, SubSection

from .. import LibrarySample


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


class CatalysisLibrary(LibrarySample):
    substrate = Quantity(
        type=Reference(CatalysisSubstrate.m_def),
        a_eln=dict(component='ReferenceEditQuantity'),
    )

    def normalize(self, archive, logger):
        super().normalize(archive, logger)
