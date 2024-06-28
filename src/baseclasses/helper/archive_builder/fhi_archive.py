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
import json
from baseclasses.characterizations.xrd import XRDData, XRDShiftedData
from baseclasses.characterizations.xrr import XRRData, XRRFittedData


def get_xrd_data_entry(archive, data_files):

    shifted_data = []
    measurements = []

    for data_file in data_files:
        if os.path.splitext(data_file)[-1] == ".uxd":
            from baseclasses.helper.file_parser.fhi_parsers import readUXD
            with archive.m_context.raw_file(data_file) as f:
                data = readUXD(f.name)

                with archive.m_context.raw_file(f"_{data_file}.json", 'w') as outfile:
                    json.dump(readUXD(f.name, False), outfile)

                datarange = 1
                while (True):
                    if " Data for range " + str(datarange) in data:
                        xrr_data_entry = XRDData()
                        xrr_data_entry.angle_type = "2THETA"

                        xrr_data_entry.angle = data[" Data for range " + str(
                            datarange)]["2THETA"]
                        xrr_data_entry.intensity = data[" Data for range " + str(
                            datarange)]["Cnt2D1"]
                        xrr_data_entry.metadata = f"_{data_file}.json"
                        xrr_data_entry.name = f"{data_file}_{datarange}"

                        measurements.append(xrr_data_entry)
                        datarange += 1
                    else:
                        break

        if os.path.splitext(data_file)[-1] == ".xy":
            from baseclasses.helper.file_parser.fhi_parsers import readXY
            with archive.m_context.raw_file(data_file) as f:
                data = readXY(f.name)

                xrr_data_entry = XRDShiftedData()
                xrr_data_entry.model = "XRD, TOPAS, EVA"
                xrr_data_entry.angle_type = "2THETA"
                xrr_data_entry.angle = data["2Theta"]
                xrr_data_entry.intensity = data["Intensity"]

                shifted_data.append(xrr_data_entry)

    return measurements, shifted_data


def get_xrr_data_entry(archive, data_files):

    fitted_data = []
    measurement = None
    for data_file in data_files:
        if os.path.splitext(data_file)[-1] == ".uxd":
            from baseclasses.helper.file_parser.fhi_parsers import readUXD
            with archive.m_context.raw_file(data_file) as f:
                data = readUXD(f.name)

                with archive.m_context.raw_file(f"_{data_file}.json", 'w') as outfile:
                    json.dump(readUXD(f.name, False), outfile)
                xrr_data_entry = XRRData()
                xrr_data_entry.angle_type = "2THETA"
                xrr_data_entry.angle = data[" Detector type  Scintillation counter"]["2THETA"]
                xrr_data_entry.intensity = data[" Detector type  Scintillation counter"]["Cnt1D2"]
                xrr_data_entry.metadata = f"_{data_file}.json"
                measurement = xrr_data_entry

        if os.path.splitext(data_file)[-1] == ".ray":
            from baseclasses.helper.file_parser.fhi_parsers import readRayFile
            with archive.m_context.raw_file(data_file) as f:
                data, data_nice = readRayFile(f.name)

                with archive.m_context.raw_file(f"_{data_file}.json", 'w') as outfile:
                    json.dump(data_nice, outfile)
                xrr_data_entry = XRRFittedData()
                xrr_data_entry.model = f'{data["method"]} chi^2 {data["chi2mode"]}'
                xrr_data_entry.angle_type = "2THETA"
                xrr_data_entry.angle = data["x0 sim"]
                xrr_data_entry.intensity = data["y sim"]
                xrr_data_entry.metadata = f"_{data_file}.json"

                xrr_data_entry.critical_angle = data_nice["Critical Angle"]['value']
                xrr_data_entry.apparent_density = data_nice["Apparent Density"]['value']
                xrr_data_entry.apparent_roughness = data_nice["Apparent Roughness"]['value']
                xrr_data_entry.chi_squared = data_nice["chi^2"]['value']
                xrr_data_entry.diffuse_scattering = data_nice["Diffuse Scattering"]['value']
                xrr_data_entry.detector_noise = data_nice["Detector Noise"]['value']
                fitted_data.append(xrr_data_entry)

    return measurement, fitted_data
