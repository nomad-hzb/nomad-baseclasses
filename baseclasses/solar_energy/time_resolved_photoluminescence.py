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

from nomad.metainfo import (
    Quantity,
    SubSection,
    Section)
from nomad.datamodel.data import ArchiveSection

from .. import MeasurementOnSample


class TRPLProperties(ArchiveSection):
    m_def = Section(label_quantity='name',
                    a_plot=[{
                        'x': 'time',
                             'y': 'counts',
                             'layout': {'yaxis': {"fixedrange": False},
                                        'xaxis': {"fixedrange": False}},
                             "config": {"scrollZoom": True,
                                        'staticPlot': False,
                                        }}])

    name = Quantity(
        type=str)

    repetition_rate = Quantity(
        type=np.dtype(
            np.float64),
        unit=('MHz'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='MHz',
            props=dict(
                minValue=0)))

    spotsize = Quantity(
        type=np.dtype(
            np.float64),
        unit=('1/cm^2'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='1/cm^2', props=dict(minValue=0)))

    laser_power = Quantity(
        type=np.dtype(
            np.float64),
        unit=('nW'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='nW',
            props=dict(
                minValue=0)))

    excitation_peak_wavelength = Quantity(
        type=np.dtype(
            np.float64), unit=('nm'), shape=[], a_eln=dict(
            component='NumberEditQuantity', defaultDisplayUnit='nm', props=dict(
                minValue=0)))

    excitation_FWHM = Quantity(
        type=np.dtype(
            np.float64),
        unit=('nm'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='nm',
            props=dict(
                minValue=0)))

    excitation_attenuation_filter = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        a_eln=dict(component='NumberEditQuantity'))

    signal_attenuation_filter = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        a_eln=dict(component='NumberEditQuantity'))

    ns_per_bin = Quantity(
        type=np.dtype(
            np.float64),
        unit=('ns'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='ns',
            props=dict(
                minValue=0)))

    time = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        unit=('ns'),
        description='Counts of the trpl measurement per bin.',
        a_plot={
            'x': 'time', 'y': 'counts'
        })

    counts = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        description='Counts of the trpl measurement per bin.',
        a_plot={
            'x': 'time', 'y': 'counts'
        })


class TimeResolvedPhotoluminescence(MeasurementOnSample):

    m_def = Section(label_quantity='file_name', validate=False)

    data_file = Quantity(
        type=str,
        shape=['*'],
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    trpl_properties = SubSection(
        section_def=TRPLProperties, repeats=True)

    def normalize(self, archive, logger):
        super(TimeResolvedPhotoluminescence, self).normalize(archive, logger)
        self.method = "Time-Resolved Photoluminescence"

        if self.data_file is not None:
            # if self.trpl_properties is not None:
            #     return
            self.trpl_properties = []
            for data_file in self.data_file:
                # todo detect file format
                if os.path.splitext(data_file)[-1] not in [".txt", ".dat"]:
                    continue

                with archive.m_context.raw_file(data_file, "br") as f:
                    import chardet
                    encoding = chardet.detect(f.read())["encoding"]

                with archive.m_context.raw_file(data_file, encoding=encoding) as f:
                    bin_line = -1
                    count_line = -1
                    counts = []
                    time = []
                    for l_idx, raw_line in enumerate(f):
                        line = raw_line.strip()
                        if line.startswith("#ns/bin"):
                            bin_line = l_idx + 1
                        if l_idx == bin_line:
                            ns_per_bin = float(line)
                        if line.startswith("#counts"):
                            count_line = l_idx + 1
                        if l_idx >= count_line and count_line >= 0:
                            counts.append(float(line))
                            time.append(
                                float(
                                    (l_idx + 1 - count_line)
                                    * ns_per_bin) if ns_per_bin > 0 else float(
                                    (l_idx + 1 - count_line)))

                    trpl_properties = TRPLProperties(
                        ns_per_bin=ns_per_bin if ns_per_bin > 0 else None)
                    trpl_properties.counts = np.array(counts)
                    trpl_properties.time = np.array(time)
                    trpl_properties.name = data_file
                    self.trpl_properties.append(trpl_properties)
