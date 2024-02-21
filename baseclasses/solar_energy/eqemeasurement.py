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

from nomad.metainfo import (SubSection, Quantity)

from nomad.datamodel.metainfo.eln import SolarCellEQE
from .. import BaseMeasurement
from ..helper.file_parser.eqe_parser import fit_urbach_tail, calculate_jsc, calculate_bandgap, calculate_j0rad, calculate_voc_rad
from nomad.units import ureg
from ..helper.add_solar_cell import add_solar_cell, add_band_gap


class SolarCellEQECustom(SolarCellEQE):

    header_lines = Quantity(
        type=np.dtype(np.int64),
        description="""
        Number of header lines in the file. Edit in case your file has a header.
        """,
        a_eln=dict(component='NumberEditQuantity'))

    def normalize(self, archive, logger):
        if self.photon_energy_array is not None and self.eqe_array is not None:
            photon_energy_array = np.array(self.photon_energy_array)
            self.bandgap_eqe = calculate_bandgap(photon_energy_array, self.eqe_array)
            self.integrated_jsc = calculate_jsc(photon_energy_array, self.eqe_array) * ureg('A/m**2')
            try:
                self.integrated_j0rad = calculate_j0rad(photon_energy_array, self.eqe_array)[0] * ureg('A/m**2')
                self.voc_rad = calculate_voc_rad(photon_energy_array, self.eqe_array)
            except ValueError:
                print('Urbach energy is > 0.026 eV (~kB*T for T = 300K).\n')
            urbach_enery, *_, urbach_energy_fit_std_dev, _ = fit_urbach_tail(photon_energy_array, self.eqe_array)
            if urbach_enery <= 0.0 or urbach_enery >= 0.5:
                print('Failed to estimate a reasonable Urbach Energy')
            else:
                self.urbach_energy, self.urbach_energy_fit_std_dev = urbach_enery, urbach_energy_fit_std_dev

        if self.photon_energy_array is not None:
            self.wavelength_array = self.photon_energy_array.to('nm', 'sp')  # pylint: disable=E1101
            self.raw_wavelength_array = self.raw_photon_energy_array.to('nm', 'sp')  # pylint: disable=E1101

        add_solar_cell(archive)
        add_band_gap(archive, self.bandgap_eqe)


class EQEMeasurement(BaseMeasurement):
    '''Eqe Measurement'''
    eqe_data = SubSection(
        section_def=SolarCellEQECustom,
        repeats=True)

    data = SubSection(
        section_def=SolarCellEQECustom)

    def normalize(self, archive, logger):
        self.method = "EQE Measurement"
        super(EQEMeasurement, self).normalize(archive, logger)
