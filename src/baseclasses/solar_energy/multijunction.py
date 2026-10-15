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
from nomad.units import ureg

# Names and conventions follow the tandem schema of
# nomad-perovskite-solar-cells-database (General, device_subset), so lab samples
# can later be mapped onto tandem database entries.
# Subcells are counted from the bottom of the device (the side furthest from
# the sun): 1 = bottom subcell, 2 = second subcell (the top cell in a tandem).
# On measurements, subcell_index 0 stands for the complete device.


class SubcellConfiguration(ArchiveSection):
    """
    One subcell of a multijunction device, filled from the subcell sample that
    declares itself as part of the multijunction (part_of_multijunction).
    """

    m_def = Section(
        label_quantity='absorber_material',
        a_eln=dict(hide=['absorber_material_from_sample', 'band_gap_from_sample']),
    )

    subcell_index = Quantity(
        type=int,
        description='Position of the subcell, 1 = bottom subcell.',
    )

    subcell_sample = Quantity(
        type=Reference(CompositeSystem.m_def),
        description='The sample entry of this subcell.',
    )

    absorber_material = Quantity(
        type=str,
        description="""
            The absorber material, e.g. Cs0.05FA0.8MA0.15Pb(I0.8Br0.2)3. Follows
            the absorber layers of the subcell sample, unless changed by hand.
            """,
        a_eln=dict(component='StringEditQuantity'),
    )

    band_gap = Quantity(
        type=np.dtype(np.float64),
        unit='eV',
        description="""
            Band gap of the subcell absorber. Follows the EQE measured on this
            subcell in the device, otherwise the band gap of the subcell sample,
            unless changed by hand.
            """,
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='eV'),
    )

    efficiency = Quantity(
        type=np.dtype(np.float64),
        description="""
            Best efficiency (in %) of the subcell. From JV measurements on the
            multijunction sample with this subcell_index, otherwise for the top
            subcell from the results of its subcell sample.
            """,
    )

    absorber_material_from_sample = Quantity(type=str)

    band_gap_from_sample = Quantity(type=np.dtype(np.float64), unit='eV')

    def follow_sample(self, name, value):
        """Sets the quantity `name` to the value taken from the subcell sample or
        its measurements, unless it was changed by hand since it was last set.
        The last automatic value is kept in the hidden `<name>_from_sample`."""
        current = getattr(self, name)
        if current is None or current == getattr(self, f'{name}_from_sample'):
            setattr(self, name, value)
        setattr(self, f'{name}_from_sample', value)


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
        description='Position of this sample in the multijunction, 1 = bottom.',
        a_eln=dict(component='NumberEditQuantity', props=dict(minValue=1)),
    )


class MultijunctionConfiguration(ArchiveSection):
    """
    Present when the sample is a multijunction (tandem, triple junction, ...)
    device. Orthogonal to the module configuration: a tandem can also be a
    module. The number of junctions is SolcarCellSample.number_of_junctions.
    """

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

    subcells = SubSection(
        section_def=SubcellConfiguration,
        description='The subcells, starting from the bottom of the device.',
        repeats=True,
    )

    def get_subcell(self, subcell_index):
        for subcell in self.subcells:
            if subcell.subcell_index == subcell_index:
                return subcell
        return None

    def update_subcells(self, result_data, number_of_junctions):
        """
        Fills the subcells from what SolcarCellSample.normalize collected:
        result_data['subcells'] are the subcell samples pointing to this
        multijunction, result_data['EQEs'] and result_data['JVs'] the
        measurements on the multijunction sample, each with a subcell_index.
        """
        eqe_band_gaps = best_per_subcell(result_data['EQEs'].values(), 'band_gap')
        jv_efficiencies = best_per_subcell(result_data['JVs'].values(), 'efficiency')
        subcell_samples = sorted(
            result_data['subcells'].values(), key=lambda s: s['subcell_index']
        )
        top_index = number_of_junctions or max(
            (s['subcell_index'] for s in subcell_samples), default=None
        )

        for subcell_sample in subcell_samples:
            index = subcell_sample['subcell_index']
            subcell = self.get_subcell(index)
            if subcell is None:
                subcell = SubcellConfiguration(subcell_index=index)
                self.m_add_sub_section(MultijunctionConfiguration.subcells, subcell)
            subcell.subcell_sample = subcell_sample['reference']
            subcell.follow_sample(
                'absorber_material', ', '.join(subcell_sample['absorber']) or None
            )
            band_gap = eqe_band_gaps.get(index, subcell_sample['band_gap'])
            subcell.follow_sample(
                'band_gap', band_gap * ureg('eV') if band_gap is not None else None
            )

            # The top subcell gets full light, so the efficiency of its own
            # sample can be used. Lower subcells need a measurement under the
            # cells above, which only exists on the multijunction sample.
            subcell.efficiency = jv_efficiencies.get(index)
            if subcell.efficiency is None and index == top_index:
                subcell.efficiency = subcell_sample['efficiency']

    def four_terminal_efficiency(self, number_of_junctions):
        """Sum of the subcell efficiencies of a 4-terminal device, if every
        subcell has one."""
        efficiencies = [s.efficiency for s in self.subcells if s.efficiency is not None]
        if (
            self.number_of_terminals == 4
            and number_of_junctions
            and len(efficiencies) == number_of_junctions
        ):
            return sum(efficiencies)
        return None

    def band_gaps(self):
        """(value in eV, label) for each subcell with a band gap, bottom first."""
        return [
            (
                s.band_gap.to('eV').magnitude,
                f'subcell {s.subcell_index}'
                + (f' - {s.absorber_material}' if s.absorber_material else ''),
            )
            for s in sorted(self.subcells, key=lambda s: s.subcell_index)
            if s.band_gap is not None
        ]


def best_per_subcell(measurements, key):
    """Highest value of `key` per subcell_index > 0, from collected JV or EQE
    measurements whose `key` holds a list of values."""
    best = {}
    for measurement in measurements:
        index = measurement.get('subcell_index')
        if not index:
            continue
        for value in measurement[key]:
            if value is None or np.isnan(value):
                continue
            if value > best.get(index, -1):
                best[index] = value
    return best
