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
from scipy import signal

from nomad.metainfo import Quantity, Reference, Section, SubSection, Datetime
from nomad.datamodel.metainfo.basesections import Analysis

from nomad.datamodel.metainfo.plot import PlotSection, PlotlyFigure
import plotly.graph_objects as go

from baseclasses.solar_energy import UVvisData, UVvisMeasurement
from ..helper.utilities import get_reference

class UVvisDataConcentration(UVvisData, PlotSection):

    concentration = Quantity(
        type=np.dtype(np.float64),
        unit=('ug/ml'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='ug/ml'))

    peak_value = Quantity(
        type=np.dtype(np.float64),
        description='The peak value of the wavelength-intensity graph. It gets automatically computed when saving.')

    peak_x_value = Quantity(
        type=np.dtype(np.float64),
        unit='nm',
        description='The wavelength value of the automatically computed peak.')

    chemical_composition_or_formulas = Quantity(
        type=str,
        description='A list of the elements involved',
        a_eln=dict(component='StringEditQuantity', label='Material'))

    reference = Quantity(
        type=Reference(Analysis.m_def),
        description=('References the calibration that was used to calculate the concentration.'),
        a_eln=dict(component='ReferenceEditQuantity', label='Concentration Detection'))

    def normalize(self, archive, logger):
        if self.intensity is not None:
            # TODO is data always sorted along xvalues for peak finding algorithm?
            peak_indices, _ = signal.find_peaks(self.intensity)
            # TODO think about peak finding algorithm (e.g. for NH3 peak x should always be at ~650nm)
            peak_widths, _, _, _ = signal.peak_widths(self.intensity, peak_indices)
            index_max = peak_indices[np.argmax(peak_widths)]
            self.peak_value = self.intensity[index_max]
            self.peak_x_value = self.wavelength[index_max]

            fig = go.Figure(
                data=[go.Scatter(name='Calibration Curve', x=self.wavelength, y=self.intensity, mode='lines')])
            fig.add_traces(go.Scatter(x=[self.peak_x_value.magnitude], y=[self.peak_value], mode='markers'))
            fig.update_layout(xaxis_title='Peak Values',
                              yaxis_title='Concentrations',
                              title_text='Calibration Curve')
            self.figures = [PlotlyFigure(label='figure 1', figure=fig.to_plotly_json())]

        if self.concentration is None:
            self.concentration, self.reference = getConcentrationData(archive, logger,
                                                                      self.chemical_composition_or_formulas,
                                                                      self.peak_value)


def getConcentrationData(data_archive, logger, material, peak_value):
    # This function gets all UVvisConcentrationDetection archives.
    # Iterates over them and selects suitable UVvisConcentrationDetection based on material and min/max peak_values.
    # Computes the concentration of the given UVvisMeasurement based on slope and intercept of suitable UVvisConcentrationDetection.
    # Returns a concentration.

    from nomad.search import search, update_by_query
    from nomad.app.v1.models import MetadataPagination
    from nomad import files

    # search for all UVvisConcentrationDetection archives
    query = {
        'entry_type': 'CE_NOME_UVvisConcentrationDetection',
    }
    pagination = MetadataPagination()
    pagination.page_size = 100
    search_result = search(owner='all', query=query, pagination=pagination,
                           user_id=data_archive.metadata.main_author.user_id)

    matching_calibrations = []

    for res in search_result.data:
        try:
            # Open Archives
            with files.UploadFiles.get(upload_id=res["upload_id"]).read_archive(entry_id=res["entry_id"]) as archive:
                entry_id = res["entry_id"]
                entry_data = archive[entry_id]["data"]
                entry = {}
                try:
                    entry['entry_id'] = entry_id
                    entry['upload_id'] = res['upload_id']
                    entry['material_name'] = entry_data['material_name']
                    entry['minimum_peak_value'] = entry_data['minimum_peak_value']
                    entry['maximum_peak_value'] = entry_data['maximum_peak_value']
                    entry['slope'] = entry_data['slope']
                    entry['intercept'] = entry_data['intercept']
                except BaseException:
                    entry['material_name'] = None

                if entry['material_name'] == material:
                    if entry['minimum_peak_value'] <= peak_value <= entry['maximum_peak_value']:
                        matching_calibrations.append(entry)

        except Exception as e:
            logger.error("Error in processing data: ", e)

    concentration = None
    calibration_reference = None
    if len(matching_calibrations) > 0:
        calibration_entry = matching_calibrations[0]
        # compute concentration
        concentration = calibration_entry['slope'] * peak_value + calibration_entry['intercept']
        # reference used UVvisConcentrationDetection
        calibration_reference = get_reference(calibration_entry['upload_id'], calibration_entry['entry_id'])
    else:
        logger.error('For the chosen material and peak value no calibration exists yet.')

    if len(matching_calibrations) > 1:
        logger.warning('For the chosen material and peak value multiple UVvisConcentrationDetections exist.'
                       'The computation of the concentration is based on the calibration linked in '
                       'the \'Concentration Detection\' reference section.')

    return concentration, calibration_reference


class UVvisMeasurementConcentration(UVvisMeasurement):
    '''UV vis Measurement associated with concentration'''

    measurements = SubSection(
        section_def=UVvisDataConcentration, repeats=True)

    def normalize(self, archive, logger):
        self.method = "UVvis Measurement"
        super(UVvisMeasurementConcentration, self).normalize(archive, logger)


