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

from nomad.metainfo import Quantity, Reference, Section, SubSection, Datetime
from nomad.datamodel.metainfo.basesections import Analysis, AnalysisResult, SectionReference
from nomad.datamodel.metainfo.plot import PlotSection, PlotlyFigure
import plotly.graph_objects as go

from baseclasses.solar_energy import UVvisData, UVvisMeasurement
from ..helper.utilities import get_reference, create_archive

class UVvisDataConcentration(UVvisData):
    m_def = Section(label_quantity='name')

    concentration = Quantity(
        type=np.dtype(np.float64),
        unit=('ug/ml'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='ug/ml'))

    area = Quantity(
        type=np.dtype(np.float64),
        description='The integral of the wavelength-intensity graph. This area is automatically computed when saving.')

    peak = Quantity(
        type=np.dtype(np.float64),
        description='The peak value of the wavelength-intensity graph. It gets automatically computed when saving.')

    material_name = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'),
        default='material')
    # TODO use formula stuff and remove default

    def normalize(self, archive, logger):
        # TODO is np.trapz the right thing to use? Should area have a unit?
        if self.intensity is not None:
            self.peak = np.max(self.intensity)
            self.area = np.trapz(y=self.intensity, x=self.wavelength.magnitude)

        if self.concentration is None:
            self.concentration = getConcentrationData(archive, logger, self.material_name, self.area)




def getConcentrationData(data_archive, logger, material, uvvis_area):
    # This function gets all UVvisConcentrationDetection archives.
    # Iterates over them and selects suitable UVvisConcentrationDetection based on material and min/max areas.
    # Computes the concentration of the given UVvisMeasurement based on slope and intercept of suitable UVvisConcentrationDetection.
    # Returns a concentration.

    from nomad.search import search, update_by_query
    from nomad.app.v1.models import MetadataPagination
    from nomad import files

    data_upload_id = data_archive.metadata.upload_id
    data_entry_id = data_archive.metadata.entry_id
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
                    entry['upload_id'] = res["upload_id"]
                    entry['material_name'] = entry_data['material_name']
                    entry['minimum_area'] = entry_data['minimum_area']
                    entry['maximum_area'] = entry_data['maximum_area']
                    entry['slope'] = entry_data['slope']
                    entry['intercept'] = entry_data['intercept']
                except BaseException:
                    entry['material_name'] = None

                if entry['material_name'] == material:
                    if entry['minimum_area'] <= uvvis_area <= entry['maximum_area']:
                        matching_calibrations.append(entry)

        except Exception as e:
            logger.error("Error in processing data: ", e)

    concentration = None
    if len(matching_calibrations) > 0:
        calibration_entry = matching_calibrations[0]
        # compute concentration
        concentration = calibration_entry['slope'] * uvvis_area + calibration_entry['intercept']

        # reference current archive in outputs section of used UVvisConcentrationDetection
        with files.UploadFiles.get(upload_id=calibration_entry['upload_id']).read_archive(entry_id=calibration_entry['entry_id']) as archive:
            entry_id = calibration_entry['entry_id']

            inputs = []
            outputs = []
            for input in archive[entry_id]['data']['inputs'].to_json():
                inputs.append(UVvisReference(reference=input['reference']))

            if 'outputs' in archive[entry_id]['data'].to_json():
                for output in archive[entry_id]['data']['outputs'].to_json():
                    outputs.append(UVVisConcentrationResult(reference=output['reference']))

            measurement_ref = get_reference(data_upload_id, data_entry_id)
            # TODO set correct data_ref
            data_ref = '/measurements/0'
            new_reference = f'{measurement_ref}{data_ref}'
            print('#############')
            print(archive[entry_id]['data'].to_json())
            for key, value in archive[entry_id]['data'].to_json().items():
                print(key)
            #archive[entry_id]['data']['outputs'][0] = UVVisConcentrationResult(reference=new_reference)
            outputs.append(UVVisConcentrationResult(reference=new_reference))
            new_uvvisconcentrationdetection = UVvisConcentrationDetection(
                name=archive[entry_id]['data']['name'],
                inputs=inputs,
                outputs=outputs,
                material_name=calibration_entry['material_name'],
                minimum_area=calibration_entry['minimum_area'],
                maximum_area=calibration_entry['maximum_area'],
                slope=calibration_entry['slope'],
                intercept=calibration_entry['intercept']
            )
            file_name = archive[entry_id]['metadata']['mainfile']
            #create_archive(new_uvvisconcentrationdetection, data_archive, file_name, overwrite=False) # TODO set True

            query = {
                'entry_id': entry_id
            }

            update_by_query(update_script="""
                                ctx._source.entry_name = "other name";
                            """,
                            owner='all',
                            query=query,
                            user_id=data_archive.metadata.main_author.user_id,
                            refresh=True)


    else:
        logger.error('For the chosen material and area no calibration exists yet.')

    if len(matching_calibrations) > 1:
        logger.error('For the chosen material and area multiple UVvisConcentrationDetections exist.'
                     'The computation of the concentration is based on the calibration linked in '
                     'the \'REFERENCED BY\' section.')

    return concentration



class UVvisMeasurementConcentration(UVvisMeasurement):
    '''UV vis Measurement associated with concentration'''

    measurements = SubSection(
        section_def=UVvisDataConcentration, repeats=True)

    def normalize(self, archive, logger):
        self.method = "UVvis Measurement"
        super(UVvisMeasurementConcentration, self).normalize(archive, logger)

class UVvisReference(SectionReference):

    reference = Quantity(
        type=Reference(UVvisMeasurementConcentration.m_def),
        a_eln=dict(component='ReferenceEditQuantity', label='UVvis Measurement'))

class UVVisConcentrationResult(SectionReference, AnalysisResult):
    reference = Quantity(
        type=Reference(UVvisDataConcentration.m_def),
        a_eln=dict(component='ReferenceEditQuantity', label='UVvis Measurement'))


class UVvisConcentrationDetection(Analysis, PlotSection):

    inputs = Analysis.inputs.m_copy()
    inputs.section_def = UVvisReference

    outputs = Analysis.outputs.m_copy()
    outputs.section_def = UVVisConcentrationResult

    material_name = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'))

    minimum_area = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity'))

    maximum_area = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity'))

    slope = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity'))

    intercept = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity'))

    # TODO maybe add R² value?

    def normalize(self, archive, logger):
        super(UVvisConcentrationDetection, self).normalize(archive, logger)

        areas = []
        concentrations = []

        for uvvis_reference in self.inputs:
            for uvvisdata in uvvis_reference.reference.measurements:
                if uvvisdata.concentration is None or uvvisdata.area is None:
                    logger.error('Please provide concentration and area data for each UVvis Measurement.')
                else:
                    concentrations.append(uvvisdata.concentration)
                    areas.append(uvvisdata.area)

        #TODO check for inputs before computing this
        self.minimum_area = min(areas)
        self.maximum_area = max(areas)

        # TODO assure correct unit
        #concentration_values = np.array([measure.to_base_units().magnitude for measure in concentrations])
        concentration_values = np.array([measure.magnitude for measure in concentrations])
        area_values = areas

        try:
            self.slope, self.intercept = np.polyfit(area_values, concentration_values, 1)
        except BaseException:
            self.slope = 0
            self.intercept = 0

        fig = go.Figure(data=[go.Scatter(name='Calibration Curve', x=areas, y=concentrations, mode='markers')])
        fig.add_traces(go.Scatter(x=[self.minimum_area, self.maximum_area],
                                  y=[self.intercept + self.slope * self.minimum_area,
                                     self.intercept + self.slope * self.maximum_area],
                                  mode='lines'))
        fig.update_layout(xaxis_title='Areas',
                          yaxis_title='Concentrations',
                          title_text='Calibration Curve')
        self.figures = [PlotlyFigure(label='figure 1', figure=fig.to_plotly_json())]
