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

import os

from nomad.units import ureg

from baseclasses.solar_energy.jvmeasurement import (
    SolarCellJVCurveCustom,
    SolarCellJVCurveDarkCustom,
)


def get_jv_archive(jv_dict, mainfile, jvm, append=False):
    jvm.file_name = os.path.basename(mainfile)
    if jv_dict.get('datetime'):
        jvm.datetime = jv_dict.get('datetime')
    jvm.active_area = jv_dict['active_area'] if 'active_area' in jv_dict else None

    # Calculate current density scaling factor if corrected_active_area is provided
    current_density_scaling_factor = 1.0
    resistance_scaling_factor = 1.0

    if (
        jvm.corrected_active_area is not None
        and jvm.active_area is not None
        and jvm.active_area != 0
        and jvm.corrected_active_area != 0
        and jvm.corrected_active_area != jvm.active_area
    ):
        print(
            f'jvm.corrected_active_area: {jvm.corrected_active_area}, jvm.active_area: {jvm.active_area}'
        )
        current_density_scaling_factor = (
            jvm.active_area / jvm.corrected_active_area
        ).magnitude
        print(f'Current density scaling factor: {current_density_scaling_factor}')
        resistance_scaling_factor = (
            jvm.corrected_active_area / jvm.active_area
        ).magnitude
        print(f'Resistance scaling factor: {resistance_scaling_factor}')

    jvm.intensity = jv_dict['intensity'] if 'intensity' in jv_dict else None
    jvm.integration_time = (
        jv_dict['integration_time'] if 'integration_time' in jv_dict else None
    )
    jvm.settling_time = jv_dict['settling_time'] if 'settling_time' in jv_dict else None
    jvm.averaging = jv_dict['averaging'] if 'averaging' in jv_dict else None
    jvm.compliance = jv_dict['compliance'] if 'compliance' in jv_dict else None
    if not append:
        jvm.jv_curve = []
    light_idx = 0
    for curve_idx, curve in enumerate(jv_dict['jv_curve']):
        # Apply scaling to current density
        corrected_curve_current_density = [
            cd * current_density_scaling_factor for cd in curve['current_density']
        ]
        if curve.get('dark'):
            jv_set = SolarCellJVCurveDarkCustom(
                cell_name=curve['name'],
                voltage=curve['voltage'],
                current_density=curve['current_density']
                * current_density_scaling_factor,
                dark=True,
            )
        else:
            jv_set = SolarCellJVCurveCustom(
                cell_name=curve['name'],
                voltage=curve['voltage'],
                current_density=curve['current_density']
                * current_density_scaling_factor,
                light_intensity=jv_dict['intensity']
                if 'intensity' in jv_dict
                else None,
                open_circuit_voltage=round(jv_dict['V_oc'][light_idx], 8) * ureg('V'),
                short_circuit_current_density=round(
                    jv_dict['J_sc'][light_idx] * current_density_scaling_factor, 8
                )
                * ureg('mA/cm^2'),
                fill_factor=round(jv_dict['Fill_factor'][light_idx], 8) * 0.01,
                efficiency=round(jv_dict['Efficiency'][light_idx], 8),
                potential_at_maximum_power_point=round(jv_dict['U_MPP'][light_idx], 8)
                * ureg('V'),
                current_density_at_maximun_power_point=round(
                    jv_dict['J_MPP'][light_idx] * current_density_scaling_factor, 8
                )
                * ureg('mA/cm^2'),
                series_resistance=round(jv_dict['R_ser'][light_idx], 8)
                * ureg('ohm*cm^2'),
                shunt_resistance=round(jv_dict['R_par'][light_idx], 8)
                * ureg('ohm*cm^2'),
            )
            light_idx += 1
        jvm.jv_curve.append(jv_set)
