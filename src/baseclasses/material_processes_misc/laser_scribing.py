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
from nomad.metainfo import Quantity, SubSection

from .. import BaseProcess


class LaserScribingProperties(ArchiveSection):
    laser_wavelength = Quantity(
        type=np.dtype(np.float64),
        unit=('nm'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='nm',
            props=dict(minValue=0),
        ),
    )

    laser_pulse_time = Quantity(
        type=np.dtype(np.float64),
        unit=('ps'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='ps',
            props=dict(minValue=0),
        ),
    )

    laser_pulse_frequency = Quantity(
        type=np.dtype(np.float64),
        unit=('kHz'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='kHz',
            props=dict(minValue=0),
        ),
    )

    speed = Quantity(
        type=np.dtype(np.float64),
        unit=('mm/s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mm/s',
            props=dict(minValue=0),
        ),
    )

    fluence = Quantity(
        type=np.dtype(np.float64),
        unit=('J/cm**2'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='J/cm**2',
            props=dict(minValue=0),
        ),
    )

    power_in_percent = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity', props=dict(minValue=0)),
    )


class LaserScribing(BaseProcess):
    """Baseclass for laser scribing of ITO substrates"""

    recipe_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'),
    )

    patterning = Quantity(
        type=str,
        description = ('States the patterning step'),
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=['P1', 'P2', 'P3', 'Commercially Etched']
            )
        ),
    )

    layout = Quantity(
        type=str,
        description=('Layout of solar cell electrodes and connections dictating the laser scribing paths'),
        a_eln=dict(component='StringEditQuantity'),
    )   

    properties = SubSection(section_def=LaserScribingProperties)


    def normalize(self, archive, logger):
        super().normalize(archive, logger)

        self.method = 'Laser Scribing'
