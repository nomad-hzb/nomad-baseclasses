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

from nomad.units import ureg


from scipy import integrate, optimize
import pandas as pd
import os
from scipy.signal import savgol_filter


# Constants
temperature = 300  # in [°K]
q = 1.602176462e-19  # % [As], elementary charge
h_Js = 6.62606876e-34  # % [Js], Planck's constant
k = 1.38064852e-23  # % [(m^2)kg(s^-2)(K^-1)], Boltzmann constant
T = temperature
VT = (k * T) / q  # % [V], 25.8mV thermal voltage at 300K
c = 299792458  # % [m/s], speed of light c_0
hc_eVnm = h_Js * c / q * 1e9  # % [eV nm]  Planck's constant for energy to wavelength conversion


def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]


def linear(x, a, b):
    return a * x + b

# Select a range from a numpy array from a given value to a given value and rerturn the indexes


def select_range(array, value_start, value_end):
    idx_start = np.where(array == value_start)[0][0]
    idx_end = np.where(array == value_end)[0][0]
    return idx_start, idx_end


def fit_urbach_tail(photon_energy, intensity, fit_window=0.06, filter_window=20):
    '''
    Fits the Urbach tail to the EQE data. To select the fitting range,
    finds the maximun of the derivative of the log(eqe) data. Then selects the range
    by going down a factor of 8 in eqe values from this reference point and up a factor of 2.
    This is unfortunately only a quick fix, but it works well enough based a few empirical tests
    with eqe data of perovskite solar cells.

    Returns:
        urbach_e: urnach energy in eV
        m:
        fit_min: photon energy of the minimum of the fitted range
        fit_max: photon energy of the maximum of the fitted range
    '''

    intensity = savgol_filter(intensity, 51, 4, mode='mirror')  # apply Savitzky-Golay filter to smooth the data
    data = pd.DataFrame({'y': intensity})
    log_data = data.apply(np.log)
    # find inflection point
    infl_point = log_data.rolling(
        window=filter_window,
        min_periods=int(filter_window / 4),
        center=True
    ).mean().diff().idxmax()
    min_eqe_fit = find_nearest(intensity, intensity[infl_point] / 8)
    max_eqe_fit = find_nearest(intensity, intensity[infl_point] * 2)
    start, stop = select_range(intensity, min_eqe_fit, max_eqe_fit)

    popt, pcov = optimize.curve_fit(  # pylint: disable=unbalanced-tuple-unpacking
        linear,
        photon_energy[start:stop],
        np.log(intensity[start:stop]),
        p0=[min(intensity) * 8, 0.026]
    )
    m = popt[1]
    fit_min, fit_max = photon_energy[start], photon_energy[stop]
    urbach_e = 1 / popt[0]
    # calculate the standard dev of popt[0]
    perr = np.sqrt(np.diag(pcov))
    urbach_e_std = perr[0] / (popt[0] ** 2)
    fit_data = dict(start=start,
                    stop=stop,
                    min_eqe_fit=min_eqe_fit,
                    max_eqe_fit=max_eqe_fit,
                    )
    return urbach_e, m, fit_min, fit_max, urbach_e_std, fit_data


def extrapolate_eqe(photon_energy, intensity):
    '''
    Extrapolates the EQE data with the fitted Urbach tail.

    Returns:
        photon_energy_extrapolated: array of the extrapolated photon energy values in eV
        eqe_extrapolated: array of the extrapolated eqe values
    '''
    try:
        urbach_e, *_, fit_data = fit_urbach_tail(photon_energy, intensity)
        min_eqe_fit = fit_data.get("min_eqe_fit")
        x_extrap = np.linspace(-1, 0, 500, endpoint=False) + photon_energy[fit_data.get("stop")]
        y_extrap = intensity[fit_data.get("stop")] * \
            np.exp((x_extrap - photon_energy[fit_data.get("stop")]) * 1 / urbach_e)
        x_interp = np.linspace(photon_energy[fit_data.get("stop")], max(photon_energy), 1000, endpoint=True)
        y_interp = np.interp(x_interp, photon_energy[max(fit_data.get("start"), fit_data.get("stop")):],
                             intensity[max(fit_data.get("start"), fit_data.get("stop")):])
        x_interp = x_interp[y_interp >= min_eqe_fit]
        y_interp = y_interp[y_interp >= min_eqe_fit]
        x_extrap = np.linspace(-1, 0, 500, endpoint=False) + min(x_interp)
        y_extrap = y_interp[0] * np.exp((x_extrap - min(x_interp)) / urbach_e)
        photon_energy_extrapolated = np.append(x_extrap, x_interp)
        eqe_extrapolated = np.append(y_extrap, y_interp)
    except ValueError:
        print('''The eqe could not be extrapolated because it was not possible
        to estimate the Urbach energy.''')
    return photon_energy_extrapolated, eqe_extrapolated


def calculate_jsc(photon_energy, intensity):
    '''
    Calculates the short circuit current (jsc) from the extrapolated eqe.

    Returns:
        jsc: short circuit current density in A m**(-2)
    '''
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filename2 = os.path.join(dir_path, 'AM15G.dat.txt')
    df_am15 = pd.read_csv(filename2, header=None)
    energy_AM15 = np.array(df_am15[df_am15.columns[1]])
    spectrum_AM15 = np.array(df_am15[df_am15.columns[2]])
    spectrum_AM15G_interp = np.interp(photon_energy, energy_AM15, spectrum_AM15)
    jsc_calc = integrate.cumtrapz(intensity * spectrum_AM15G_interp, photon_energy)
    jsc = max(jsc_calc * q * 1e4)
    return jsc

# Calculates the bandgap from the inflection point of the eqe.


def calculate_bandgap(photon_energy, intensity):
    '''
    calculates the bandgap from the inflection point of the eqe.

    Returns:
        bandgap: bandgap in eV calculated from in the inflection point of the eqe
    '''
    intensity = savgol_filter(intensity, 51, 4, mode='nearest')
    deqe_interp = np.diff(intensity) / np.diff(np.flip(-photon_energy))
    bandgap = photon_energy[deqe_interp.argmax()]
    # print('Bandgap: ' + str(bandgap) + ' eV')
    return bandgap


def calculate_j0rad(photon_energy, intensity):
    '''
    Calculates the radiative saturation current (j0rad) and the calculated electroluminescence (EL)
    spectrum (Rau's reciprocity) from the extrapolated eqe.

    Returns:
        j0rad: radiative saturation current density in A m**(-2)
        EL: EL spectrum
    '''
    try:
        urbach_e = fit_urbach_tail(photon_energy, intensity)[0]
        # try to calculate the j0rad and EL spectrum except if the urbach energy is larger than 0.026
        if urbach_e >= 0.026 or urbach_e <= 0.0:
            raise ValueError('''Urbach energy is > 0.026 eV (~kB*T for T = 300K), or
            it could notbe estimated. The `j0rad` could not be calculated.''')

        x, y = extrapolate_eqe(photon_energy, intensity)
        phi_BB = (2 * np.pi * q**3 * (x)**2) / (h_Js**3 * c**2 * (np.exp(x / VT) - 1))
        el = phi_BB * y
        j0rad = np.trapz(el, x)
        j0rad = j0rad * q
    except ValueError:
        raise ValueError('''Failed to estimate a reasonable Urbach Energy.''')
    # print('Radiative saturation current: ' + str(j0rad) + ' A / m^2')
    return j0rad, el


def calculate_voc_rad(photon_energy, intensity):
    '''
    Calculates the radiative open circuit voltage (voc_rad) with the calculted j0rad
    and j_sc.

    Returns:
        voc_rad: radiative open circuit voltage in V
    '''
    try:
        j0rad = calculate_j0rad(photon_energy, intensity)[0]
        jsc = calculate_jsc(photon_energy, intensity)
        voc_rad = VT * np.log(jsc / j0rad)
        # print('Voc rad: ' + str(voc_rad) + ' V')
    except ValueError:
        raise ValueError('''Urbach energy is > 0.026 eV (~kB*T for T = 300K).
                       The `j0rad` could not be calculated.''')
    return voc_rad


# test
# file = "/home/a2853/Documents/Projects/nomad/hysprintlab/testfiles_dragndrop/HZB_MiGo_20230225_p2_0_0.1.eqe.txt"
# x_raw, y_raw, x, y = read_file(file, 9)

# print(fit_urbach_tail(x, y))
# print(calculate_jsc(x, y))
# print(calculate_bandgap(x, y))
# print(calculate_j0rad(x, y))
# print(calculate_voc_rad(x, y))



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


class EQEMeasurement(BaseMeasurement):
    '''Eqe Measurement'''

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    eqe_data = SubSection(
        section_def=SolarCellEQECustom,
        repeats=True)

    data = SubSection(
        section_def=SolarCellEQECustom)

    def normalize(self, archive, logger):
        self.method = "EQE Measurement"
        super(EQEMeasurement, self).normalize(archive, logger)
