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
import pytz
from nomad.datamodel.metainfo.eln import Entity
from nomad.metainfo import Datetime, MEnum, Quantity


class TEM_Session(Entity):
    """Vaccume Values for Experiment Session."""

    datetime = Quantity(
        type=Datetime,
        description='The date and time of the maintenance.',
        a_eln=dict(component='DateTimeEditQuantity'),
    )

    accelaration_voltage = Quantity(
        type=MEnum(['40', '60', '80', '120', '200']),
        a_eln=dict(component='EnumEditQuantity'),
    )

    emission_current = Quantity(
        type=np.dtype(np.float64),
        unit='uA',
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='uA',
            minValue=0,
            maxValue=300,
        ),
    )
    filament_current = Quantity(
        type=np.dtype(np.float64),
        unit='A',
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='A',
            minValue=0,
            maxValue=5,
        ),
    )
    extractor_voltage = Quantity(
        type=np.dtype(np.float64),
        unit='V',
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='V',
            minValue=0,
            maxValue=5000,
        ),
    )
    vaccuum_gun = Quantity(
        type=np.dtype(np.float64),
        unit='mbar',
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mbar',
            minValue=1e-12,
            maxValue=1,
        ),
    )
    vaccum_column = Quantity(
        type=np.dtype(np.float64),
        unit='mbar',
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mbar',
            minValue=1e-9,
            maxValue=1,
        ),
    )
    vaccum_camera = Quantity(
        type=np.dtype(np.float64),
        unit='mbar',
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mbar',
            minValue=1e-9,
            maxValue=1,
        ),
    )

    def normalize(self, archive, logger):
        super().normalize(archive, logger)
        if self.datetime:
            archive.metadata.entry_name = self.datetime.astimezone(
                pytz.timezone('Europe/Berlin')
            ).strftime('%Y/%m/%d-%H:%M:%S')
