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

from nomad.metainfo import (
    Quantity,
    SubSection,
    Reference,
    MEnum)
from nomad.datamodel.data import ArchiveSection

from ..solution import Solution
from .wet_chemical_deposition import WetChemicalDeposition


class NozzleVoltageProfile(ArchiveSection):
    pass


class PrintHeadPath(ArchiveSection):
    pass


class LP50NozzleVoltageProfile(NozzleVoltageProfile):
    voltage_a = Quantity(
        type=np.dtype(
            np.float64), unit=('V'), a_eln=dict(
            component='NumberEditQuantity', defaultDisplayUnit='V', props=dict(
                minValue=0, maxValue=130)))

    rise_edge_a = Quantity(
        type=np.dtype(
            np.float64),
        unit=('us'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='us',
            props=dict(
                minValue=1,
                maxValue=25)))

    peak_time_a = Quantity(
        type=np.dtype(
            np.float64),
        unit=('us'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='us',
            props=dict(
                minValue=0,
                maxValue=25)))

    fall_edge_a = Quantity(
        type=np.dtype(
            np.float64),
        unit=('us'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='us',
            props=dict(
                minValue=1,
                maxValue=25)))

    voltage_b = Quantity(
        type=np.dtype(
            np.float64), unit=('V'), a_eln=dict(
            component='NumberEditQuantity', defaultDisplayUnit='V', props=dict(
                minValue=0, maxValue=130)))

    rise_edge_b = Quantity(
        type=np.dtype(
            np.float64),
        unit=('us'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='us',
            props=dict(
                minValue=1,
                maxValue=25)))

    peak_time_b = Quantity(
        type=np.dtype(
            np.float64),
        unit=('us'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='us',
            props=dict(
                minValue=0,
                maxValue=25)))

    fall_edge_b = Quantity(
        type=np.dtype(
            np.float64),
        unit=('us'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='us',
            props=dict(
                minValue=1,
                maxValue=25)))


class LP50PrintHeadPath(PrintHeadPath):
    quality_factor = Quantity(
        type=MEnum(
            'QF1',
            'QF2',
            'QF3',
            'QF4',
            'QF5',
            'QF6',
            'QF7',
            'QF8',
            'QF9',
            'QF10',
            'QF11',
            'QF12',
            'QF13',
            'QF14',
            'QF15',
            'QF16'),
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
        ))

    directional = Quantity(
        type=MEnum('uni-directional', 'bi-directional',
                   'uni-directional reverse'),
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
        ))

    swaths = Quantity(
        type=np.dtype(
            np.float64), a_eln=dict(
            component='NumberEditQuantity'))

    wait_run_time = Quantity(
        type=np.dtype(
            np.float64), unit=('s'), a_eln=dict(
            component='NumberEditQuantity', defaultDisplayUnit='s', props=dict(
                minValue=0)))

    total_run_time = Quantity(
        type=np.dtype(
            np.float64), unit=('s'), a_eln=dict(
            component='NumberEditQuantity', defaultDisplayUnit='s', props=dict(
                minValue=0)))


class PrintHeadProperties(ArchiveSection):
    print_speed = Quantity(
        type=np.dtype(
            np.float64),
        unit=('mm/s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mm/s',
            props=dict(
                minValue=1, maxValue=400)))

    print_head_angle = Quantity(
        type=np.dtype(
            np.float64),
        unit=('deg'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='deg',
            props=dict(
                minValue=0)))

    print_head_temperature = Quantity(
        type=np.dtype(
            np.float64), unit=('°C'), a_eln=dict(
            component='NumberEditQuantity', defaultDisplayUnit='°C', props=dict(
                minValue=20, maxValue=120)))

    print_head_distance_to_substrate = Quantity(
        type=np.dtype(
            np.float64), unit=('mm'), a_eln=dict(
            component='NumberEditQuantity', defaultDisplayUnit='mm', props=dict(
                minValue=-27, maxValue=35)))

    print_head_width = Quantity(
        type=np.dtype(
            np.float64), unit=('mm'), a_eln=dict(
            component='NumberEditQuantity', defaultDisplayUnit='mm'))

    print_nozzle_distance = Quantity(
        type=np.dtype(
            np.float64), unit=('mm'), a_eln=dict(
            component='NumberEditQuantity', defaultDisplayUnit='mm'))

    print_nozzle_width = Quantity(
        type=np.dtype(
            np.float64), unit=('um'), a_eln=dict(
            component='NumberEditQuantity', defaultDisplayUnit='um'))

    print_nozzle_drop_volume = Quantity(
        type=np.dtype(
            np.float64), unit=('pl'), a_eln=dict(
            component='NumberEditQuantity', defaultDisplayUnit='pl'))


class InkjetPrintingProperties(ArchiveSection):

    # m_def = Section(label_quantity='name')

    resolution_x = Quantity(
        type=np.dtype(
            np.float64),
        # unit=('ml'),
        a_eln=dict(
            component='NumberEditQuantity',
            # defaultDisplayUnit='ml',
            props=dict(
                minValue=0)))

    resolution_y = Quantity(
        type=np.dtype(
            np.float64),
        # unit=('ml'),
        a_eln=dict(
            component='NumberEditQuantity',
            # defaultDisplayUnit='ml',
            props=dict(
                minValue=0)))

    substrate_height = Quantity(
        type=np.dtype(
            np.float64), unit=('mm'), a_eln=dict(
            component='NumberEditQuantity', defaultDisplayUnit='mm', props=dict(
                minValue=0, maxValue=35)))

    substrate_temperature = Quantity(
        type=np.dtype(
            np.float64), unit=('°C'), a_eln=dict(
            component='NumberEditQuantity', defaultDisplayUnit='°C', props=dict(
                minValue=20, maxValue=60)))

    cartridge_pressure = Quantity(
        type=np.dtype(
            np.float64), unit=('mbar'), a_eln=dict(
            component='NumberEditQuantity', defaultDisplayUnit='mbar', props=dict(
                minValue=0, maxValue=38)))

    cartridge_temperature = Quantity(
        type=np.dtype(
            np.float64), unit=('°C'), a_eln=dict(
            component='NumberEditQuantity', defaultDisplayUnit='°C'))

    print_head_properties = SubSection(
        section_def=PrintHeadProperties)


class LP50InkjetPrintingProperties(InkjetPrintingProperties):
    not_using_lp50_computer = Quantity(
        type=bool,
        shape=[],
        a_eln=dict(
            component='BoolEditQuantity',
        ))

    active_nozzles = Quantity(
        type=MEnum('all', 'Spectra', 'DMC', 'Konika Minolta'),
        shape=[],
        a_eln=dict(
            component='RadioEnumEditQuantity',
        ))

    printer_software = Quantity(
        type=str, a_eln=dict(
            component='StringEditQuantity'))


class LP50InkjetPrinting(WetChemicalDeposition):
    '''Base class for inkjet printing of a layer on a sample'''

    recipe_used = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    print_head_used = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    properties = SubSection(
        section_def=LP50InkjetPrintingProperties)

    print_head_path = SubSection(
        section_def=LP50PrintHeadPath)

    nozzle_voltage_profile = SubSection(
        section_def=LP50NozzleVoltageProfile)

    def normalize(self, archive, logger):
        super(LP50InkjetPrinting, self).normalize(archive, logger)
        self.method = "Inkjet printing"
