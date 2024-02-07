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

from nomad.metainfo import (
    Quantity,
    Datetime)

from .. import BaseProcess



class Storage(BaseProcess):
    '''Base class for storage of a sample'''
    start_date = Quantity(
        type=Datetime,
        a_eln=dict(component='DateTimeEditQuantity'))

    end_date = Quantity(
        type=Datetime,
        a_eln=dict(component='DateTimeEditQuantity'))

    duration = Quantity(
        #Link to ontology class 'duration', Link to ontology class 'duration setting datum'
        links = ['http://purl.obolibrary.org/obo/PATO_0001309', 'https://purl.archive.org/tfsco/TFSCO_00002006'],
        type=str)

    start_humidity = Quantity(
        #Link to ontology class 'humidity'
        links = ['http://purl.obolibrary.org/obo/PATO_0015009'],
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity'))

    end_humidity = Quantity(
        #Link to ontology class 'humidity'
        links = ['http://purl.obolibrary.org/obo/PATO_0015009'],
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity'))

    def normalize(self, archive, logger):
        super(Storage, self).normalize(archive, logger)

        self.method = "Storage"
        if self.start_date and self.end_date:
            if self.start_date < self.end_date:
                self.duration = str(self.end_date - self.start_date)
            else:
                self.duration = "invalid, start date after end date"
