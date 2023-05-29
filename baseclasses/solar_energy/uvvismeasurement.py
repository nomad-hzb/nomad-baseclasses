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
import os
from datetime import datetime
import pandas as pd


from nomad.metainfo import (
    Quantity,
    Section,
    SubSection,
    Datetime)
from nomad.datamodel.data import ArchiveSection

from .. import MeasurementOnSample


def get_data_of_file(filename, start, end):
    return pd.read_csv(
        filename,
        delimiter="\t",
        on_bad_lines='skip',
        header=None,
        skiprows=start + 1,
        nrows=end - start - 1)


class UVvisData(ArchiveSection):
    m_def = Section(label_quantity='name',
                    a_plot=[{
                        'x': 'wavelength',
                             'y': 'intensity',
                             'layout': {'yaxis': {"fixedrange": False},
                                        'xaxis': {"fixedrange": False}},
                             "config": {"scrollZoom": True,
                                        'staticPlot': False,
                                        }}])

    name = Quantity(
        type=str)

    datetime = Quantity(
        type=Datetime,
        description='The date and time associated with this section.',
        a_eln=dict(component='DateTimeEditQuantity'))

    wavelength = Quantity(
        type=np.dtype(
            np.float64), shape=['*'], unit='nm', a_plot=[
            {
                'x': 'wavelength', 'y': 'intensity', 'layout': {
                    'yaxis': {
                        "fixedrange": False}, 'xaxis': {
                            "fixedrange": False}}, "config": {
                    "editable": True, "scrollZoom": True}}])

    intensity = Quantity(
        type=np.dtype(
            np.float64), shape=['*'], a_plot=[
            {
                'x': 'wavelength', 'y': 'intensity', 'layout': {
                    'yaxis': {
                        "fixedrange": False}, 'xaxis': {
                            "fixedrange": False}}, "config": {
                    "editable": True, "scrollZoom": True}}])


class UVvisMeasurement(MeasurementOnSample):
    '''UV vis Measurement'''

    m_def = Section(
        a_eln=dict(hide=['certified_values', 'certification_institute']))

    data_file = Quantity(
        type=str,
        shape=['*'],
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    data_folder = Quantity(
        type=str,
        default="uvvis_data",
        a_eln=dict(component='StringEditQuantity'))

    measurements = SubSection(
        section_def=UVvisData, repeats=True)

    def normalize(self, archive, logger):
        super(UVvisMeasurement, self).normalize(archive, logger)
        self.method = "UVvis Measurement"

        archive_base = os.path.join(str(archive.m_context.upload_files), "raw")
        data_in_folder = []
        for folder in os.listdir(archive_base):
            if folder.startswith(self.data_folder):
                data_in_folder.append(folder)

        if self.data_file is None:
            self.data_file = []

        measurements = []
        files = []
        if self.data_file or data_in_folder:
            files = [file for file in self.data_file]

            for folder in data_in_folder:
                files.extend([os.path.join(folder, file) for file in os.listdir(
                    os.path.join(archive_base, folder))])

        for data_file in files:
            if os.path.splitext(data_file)[-1] not in [".txt", ".csv", ".ABS"]:
                continue

            try:
                with archive.m_context.raw_file(data_file) as f:
                    data_file = os.path.basename(data_file)
                    datetime_object = None
                    if os.path.splitext(data_file)[-1] == ".txt":
                        data = pd.read_csv(
                            f.name, delimiter=';', header=None)
                        datetime_str = data_file.split(".")[0]
                        datetime_object = datetime.strptime(
                            datetime_str, '%Y%m%d_%H_%M_%S_%f')

                    if os.path.splitext(data_file)[-1] == ".csv":
                        sections = dict()
                        for index, line in enumerate(f.readlines()):
                            if line.startswith("["):
                                sections.update({line[1:-2]: index})
                        metadata = get_data_of_file(
                            f.name, sections["SpectrumHeader"], sections["Data"])
                        data = get_data_of_file(
                            f.name, sections["Data"], sections["EndOfFile"])
                        datetime_str = f"{metadata[metadata[0] == '#Date'][1].iloc[0]}_{metadata[metadata[0] == '#GMTTime'][1].iloc[0]}"
                        datetime_object = datetime.strptime(
                            datetime_str, '%Y%m%d_%H%M%S%f')
                    if os.path.splitext(data_file)[-1] == ".ABS":
                        data = pd.read_csv(
                            f.name, delimiter='  ', header=None, skiprows=2)

                data_entry = UVvisData()
                if datetime_object is not None:
                    data_entry.datetime = datetime_object.strftime(
                        "%Y-%m-%d %H:%M:%S.%f")
                data_entry.name = data_file
                data_entry.wavelength = np.array(data[0])
                data_entry.intensity = np.array(data[1])

                measurements.append(data_entry)
            except BaseException:
                pass

        self.measurements = measurements
