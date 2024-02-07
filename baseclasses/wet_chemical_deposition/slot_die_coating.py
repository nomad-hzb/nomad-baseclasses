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
    Reference,
    SubSection)
from nomad.datamodel.data import ArchiveSection

from ..solution import Solution
from .wet_chemical_deposition import WetChemicalDeposition
from ..material_processes_misc import Annealing, AirKnifeGasQuenching


class SlotDieCoatingProperties(ArchiveSection):

    flow_rate = Quantity(
        #Link to ontology class 'slot die coating flow rate' and 'slot die coating flow rate setting datum'
        links = ['https://purl.archive.org/tfsco/TFSCO_00005039', 'https://purl.archive.org/tfsco/TFSCO_00005048'],
        type=np.dtype(
            np.float64),
        unit=('ml/minute'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='ml/minute', props=dict(minValue=0)))

    slot_die_head_width = Quantity(
        #Link to ontology class 'slot die head width' and 'slot die head width setting datum'
        links = ['https://purl.archive.org/tfsco/TFSCO_00005038', 'https://purl.archive.org/tfsco/TFSCO_00005047'],
        type=np.dtype(
            np.float64),
        unit=('mm'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mm',
            props=dict(
                minValue=0)))

    slot_die_shim_width = Quantity(
        #Link to ontology class 'slot die shim width' and 'slot die chim width setting datum'
        links = ['https://purl.archive.org/tfsco/TFSCO_00005035', 'https://purl.archive.org/tfsco/TFSCO_00005045'],
        type=np.dtype(
            np.float64),
        unit=('mm'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mm',
            props=dict(
                minValue=0)))

    slot_die_shim_thickness = Quantity(
        #Link to ontology class 'slot die shim thickness' and 'slot die shim thickness setting datum'
        links = ['https://purl.archive.org/tfsco/TFSCO_00005036', 'https://purl.archive.org/tfsco/TFSCO_00005046'],
        type=np.dtype(
            np.float64),
        unit=('mm'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mm',
            props=dict(
                minValue=0)))

    slot_die_head_distance_to_thinfilm = Quantity(
        #Link to ontology class 'slot die head distance to thinfilm' and 'slot die head distane to thinfilm setting datum'
        links = ['https://purl.archive.org/tfsco/TFSCO_00005034', 'https://purl.archive.org/tfsco/TFSCO_00005044'],
        type=np.dtype(
            np.float64),
        unit=('mm'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mm',
            props=dict(
                minValue=0)))
    slot_die_head_speed = Quantity(
        #Link to ontology class 'slot die head speed' and 'slot die head speed setting datum'
        links = ['https://purl.archive.org/tfsco/TFSCO_00005033', 'https://purl.archive.org/tfsco/TFSCO_00005042'],
        type=np.dtype(
            np.float64),
        unit=('mm/s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mm/s',
            props=dict(
                minValue=0)))

    temperature = Quantity(
        #Link to ontology class 'temperature' and 'temperature setting datum'
        links = ['http://purl.obolibrary.org/obo/PATO_0000146', 'https://purl.archive.org/tfsco/TFSCO_00002111'],
        type=np.dtype(
            np.float64),
        unit=('°C'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='°C',
            props=dict(
                minValue=0)))


class SlotDieCoating(WetChemicalDeposition):
    '''Spin Coating'''
    m_def = Section(
        #Link to ontology class 'slot die coating'
        links = ['https://purl.archive.org/tfsco/TFSCO_00000075']
    )

    properties = SubSection(section_def=SlotDieCoatingProperties)

    def normalize(self, archive, logger):
        super(SlotDieCoating, self).normalize(archive, logger)

        self.method = "Slot Die Coating"
