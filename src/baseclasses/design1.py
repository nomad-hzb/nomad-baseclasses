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
    Section,
    MEnum)
from nomad.datamodel.data import ArchiveSection
from baseclasses.helper.utilities import rewrite_json
from nomad.datamodel.metainfo.basesections import Entity


class Factor(ArchiveSection):

    m_def = Section(label_quantity='label')

    label = Quantity(
        type=str,
    )

    active = Quantity(
        type=bool,
        default=False,
        a_eln=dict(component='BoolEditQuantity'))

    name = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'))

    step = Quantity(
        type=np.dtype(np.int64),
        a_eln=dict(component='NumberEditQuantity')
    )

    def normalize(self, archive, logger):
        super(Factor, self).normalize(archive, logger)
        if self.name:
            self.label = self.name

        if self.step:
            self.label = str(self.step) + ' ' + self.label

        if self.active:
            self.label = self.label + " active"


class DiscreteFactor(Factor):
    m_def = Section(label_quantity='label',
                    a_eln=dict(
                        properties=dict(
                            order=[
                                "name",
                                "active",
                                "step",
                                "default_value", "unit", "minimum_value", "maximum_value", "values"])))

    values = Quantity(
        type=str,
        shape=['*'],
        a_eln=dict(
            component='StringEditQuantity',
        ))

    default_value = Quantity(
        type=str,
        a_eln=dict(
            component='StringEditQuantity',
        ))


class ContinuousFactor(Factor):
    m_def = Section(label_quantity='label',
                    a_eln=dict(
                        properties=dict(
                            order=[
                                "name",
                                "active",
                                "step",
                                "default_value", "unit", "minimum_value", "maximum_value", "values"])))

    unit = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'))

    minimum_value = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(
            component='NumberEditQuantity',
        ))

    maximum_value = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(
            component='NumberEditQuantity',
        ))

    default_value = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(
            component='NumberEditQuantity',
        ))


class Design(Entity):

    create_design_template = Quantity(
        type=bool,
        default=False,
        a_eln=dict(component='BoolEditQuantity')
    )

    design_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    continuous_factors = SubSection(
        section_def=ContinuousFactor, repeats=True)

    discrete_factors = SubSection(
        section_def=DiscreteFactor, repeats=True)

    def normalize(self, archive, logger):
        super(Design, self).normalize(archive, logger)

        self.method = "Design"

        if self.create_design_template and not self.design_file:
            with archive.m_context.raw_file(archive.metadata.mainfile) as f:
                path = os.path.dirname(f.name)
            self.create_design_template = False
            rewrite_json(["data", "create_design_template"], archive, False)
            import pandas as pd
            data = []
            columns = [f.get("label") for f in self.continuous_factors + self.discrete_factors]
            index = ["active", "unit", "minimum_value", "maximum_value", "values", "default_value"]
            for idx in index:
                row = []
                for f in self.continuous_factors + self.discrete_factors:
                    row.extend([f.get(idx)])
                data.append(row)

            df = pd.DataFrame(data, index=index, columns=columns)
            df = df.sort_values(by=df.index[0], ascending=False, axis=1)
            file_name = self.name.replace(" ", "_")+".tsv"
            df.to_csv(os.path.join(path, file_name), sep="\t")
            self.design_file = file_name
