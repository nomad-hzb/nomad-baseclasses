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

from nomad.units import ureg


def get_eqe_archive(eqe_dict, mainfile, eqem, logger):

    eqem.measured = True
    eqem.bandgap_eqe = eqe_dict['bandgap']
    eqem.integrated_jsc = eqe_dict['jsc'] * ureg('A/m**2')
    eqem.integrated_j0rad = eqe_dict['j0rad'] * ureg(
        'A/m**2') if 'j0rad' in eqe_dict else logger.warning('The j0rad could not be calculated.')
    eqem.voc_rad = eqe_dict['voc_rad'] if 'voc_rad' in eqe_dict else logger.warning(
        'The voc_rad could not be calculated.')
    eqem.urbach_energy = eqe_dict.get('urbach_e')
    eqem.photon_energy_array = np.array(eqe_dict['interpolated_photon_energy'])
    eqem.raw_photon_energy_array = np.array(eqe_dict['photon_energy_raw'])
    eqem.eqe_array = np.array(eqe_dict['interpolated_eqe'])
    eqem.raw_eqe_array = np.array(eqe_dict['eqe_raw'])

    if eqem.photon_energy_array is not None:
        eqem.wavelength_array = eqem.photon_energy_array.to(
            'nm', 'sp')  # pylint: disable=E1101
        eqem.raw_wavelength_array = eqem.raw_photon_energy_array.to(
            'nm', 'sp')  # pylint: disable=E1101
