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
from nomad.metainfo import Quantity, Reference, Section, SubSection

# Names and conventions follow the tandem schema of
# nomad-perovskite-solar-cells-database (General, SubCellOrigin, device_subset),
# so lab samples can later be mapped onto tandem database entries.
# The same subcell_index is used on layers and measurements, where 0 stands for
# the complete device or a layer shared by the subcells.


class SubcellConfiguration(ArchiveSection):
    """
    One subcell (junction) of a multijunction device.
    """

    m_def = Section(
        label_quantity='absorber_material',
        a_eln=dict(hide=['absorber_material_from_sample']),
    )

    subcell_index = Quantity(
        type=int,
        description="""
            Position of the subcell, counted from the bottom of the device (the
            side furthest from the sun): 1 = bottom subcell, 2 = second subcell
            (the top cell in a tandem), 3 = third subcell. Filled from the
            position in the list if left empty.
            """,
        a_eln=dict(component='NumberEditQuantity', props=dict(minValue=1)),
    )

    absorber_material = Quantity(
        type=str,
        description="""
            The absorber material, e.g. Cs0.05FA0.8MA0.15Pb(I0.8Br0.2)3. Filled
            from the absorber layers of the subcell sample and kept up to date,
            unless it is changed by hand.
            """,
        a_eln=dict(component='StringEditQuantity'),
    )

    absorber_material_from_sample = Quantity(
        type=str,
        description="""
            The absorber material last taken from the subcell sample. If
            absorber_material still equals it, it was not changed by hand and is
            updated from the subcell sample.
            """,
    )

    def update_absorber_material(self, absorber_material):
        """Takes the absorber material of the subcell sample, unless the user
        changed absorber_material by hand since it was last filled."""
        if self.absorber_material in (None, self.absorber_material_from_sample):
            self.absorber_material = absorber_material
        self.absorber_material_from_sample = absorber_material

    band_gap = Quantity(
        type=np.dtype(np.float64),
        unit='eV',
        description="""
            Band gap of the subcell absorber. If left empty, it is filled from EQE
            spectra measured on this subcell.
            """,
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='eV'),
    )

    commercial = Quantity(
        type=bool,
        description="""
            TRUE if the subcell was bought or provided ready-made (e.g. a silicon
            bottom cell), FALSE if it was made in the lab.
            """,
        a_eln=dict(component='BoolEditQuantity'),
    )

    supplier = Quantity(
        type=str,
        description='Company or research group the subcell comes from.',
        a_eln=dict(component='StringEditQuantity'),
    )

    subcell_sample = Quantity(
        type=Reference(CompositeSystem.m_def),
        description="""
            The sample entry of this subcell, if it exists as a separate sample,
            e.g. the two cells of a mechanically stacked 4-terminal device.
            Filled automatically from the samples that declare themselves as a
            subcell of this multijunction (part_of_multijunction).
            """,
        a_eln=dict(component='ReferenceEditQuantity'),
    )

    efficiency = Quantity(
        type=np.dtype(np.float64),
        description="""
            Best efficiency (in %) of the subcell. Taken from JV measurements on
            the multijunction sample with this subcell_index, otherwise for the
            top subcell from the results of its subcell sample.
            """,
    )


class MultijunctionReference(CompositeSystemReference):
    """
    Present on a sample that is a subcell of a multijunction device: the
    multijunction sample it belongs to and its position in it. Repeats, so the
    same subcell sample (e.g. a silicon bottom cell) can be combined with
    different top cells in several multijunction devices.
    """

    m_def = Section(label_quantity='lab_id')

    subcell_index = Quantity(
        type=int,
        description="""
            Position of this sample in the multijunction, counted from the bottom
            of the device (the side furthest from the sun): 1 = bottom subcell,
            2 = second subcell (the top cell in a tandem), 3 = third subcell.
            """,
        a_eln=dict(component='NumberEditQuantity', props=dict(minValue=1)),
    )


class MultijunctionConfiguration(ArchiveSection):
    """
    Present when the sample is a multijunction (tandem, triple junction, ...)
    device. Orthogonal to the module configuration: a tandem can also be a
    module.
    """

    m_def = Section()

    integration = Quantity(
        type=str,
        description="""
            How the subcells are combined.
            - *Monolithic*: subcells deposited on top of each other and connected
              through a recombination or interconnecting layer.
            - *Mechanically Stacked*: independently made subcells on top of each
              other (typically 4-terminal).
            - *Laminated*: subcells made separately and laminated together.
            - *Spectral splitter*: the light is split and sent to separate cells.
            """,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=[
                    'Monolithic',
                    'Mechanically Stacked',
                    'Laminated',
                    'Spectral splitter',
                    'Other',
                ]
            ),
        ),
    )

    number_of_terminals = Quantity(
        type=int,
        description="""
            Number of electrical terminals of the device. 2 for subcells connected
            in series, 4 for independently contacted subcells, 3 for devices with
            a shared middle contact.
            """,
        a_eln=dict(component='NumberEditQuantity', props=dict(minValue=2)),
    )

    number_of_junctions = Quantity(
        type=int,
        description="""
            Number of junctions (subcells). Taken from the number of subcells if
            left empty.
            """,
        a_eln=dict(component='NumberEditQuantity', props=dict(minValue=2)),
    )

    subcells = SubSection(
        section_def=SubcellConfiguration,
        description='The subcells, starting from the bottom of the device.',
        repeats=True,
    )

    photoabsorbers_string = Quantity(
        type=str,
        description="""
            The absorber materials from bottom to top, e.g. "Si-CsFAPbIBr".
            Generated from the subcells.
            """,
    )

    def sorted_subcells(self):
        return sorted(
            self.subcells,
            key=lambda s: s.subcell_index if s.subcell_index is not None else 0,
        )

    def get_subcell(self, subcell_index):
        for subcell in self.subcells:
            if subcell.subcell_index == subcell_index:
                return subcell
        return None

    def derive_quantities(self):
        """Fills the derived quantities. Called in normalize and again by the
        sample after it filled values from the measurements, since sub-sections
        are normalized before their parent section."""
        for i, subcell in enumerate(self.subcells):
            if subcell.subcell_index is None:
                subcell.subcell_index = i + 1

        if self.subcells and self.number_of_junctions is None:
            self.number_of_junctions = len(self.subcells)

        absorbers = [s.absorber_material or '-' for s in self.sorted_subcells()]
        if absorbers:
            self.photoabsorbers_string = '-'.join(absorbers)

    def normalize(self, archive, logger):
        super().normalize(archive, logger)
        self.derive_quantities()
