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
import pandas as pd

from nomad.metainfo import (
    Quantity,
    SubSection,
    Section,
    Reference, MProxy)

from nomad.datamodel.metainfo.eln import Entity


from baseclasses.helper.utilities import rewrite_json

from baseclasses.chemical_energy import SampleIDCENOME


def get_sample():
    columns = ["id",
               "chemical_composition_or_formula",
               "component_description",
               "producer",
               "project_name_long",
               "description",
               "substrate_type",
               "substrate_dimension"
               ]
    return pd.DataFrame(columns=columns)


def get_env(number_of_substances):
    columns = ["id",
               "ph_value",
               "description",
               "solvent_name",
               "purging_gas_name",
               "purging_temperature",
               "purging_time",
               ]
    substance = ["substance_name", "concentration_M", "concentration_g_per_l"]
    for i in range(number_of_substances):
        columns.extend([s + "_" + str(i) for s in substance])

    return pd.DataFrame(columns=columns)


def get_setup():
    columns = ["id",
               "setup",
               "reference_electrode",
               "counter_electrode",
               "description"
               ]
    return pd.DataFrame(columns=columns)


class DocumentationTool(Entity):

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor')
    )

    create_template = Quantity(
        type=bool,
        default=False,
        a_eln=dict(component='ButtonEditQuantity')
    )

    create_entries = Quantity(
        type=bool,
        default=False,
        a_eln=dict(component='ButtonEditQuantity')
    )

    number_of_substances_per_env = Quantity(
        type=np.dtype(np.int64),
        default=3,
        a_eln=dict(component='NumberEditQuantity')
    )

    identifier = SubSection(
        section_def=SampleIDCENOME)

    def normalize(self, archive, logger):
        super(DocumentationTool, self).normalize(archive, logger)

        if self.create_template and not self.data_file:
            self.create_template = False
            rewrite_json(["data", "create_template"], archive, False)

            with archive.m_context.raw_file(archive.metadata.mainfile) as f:
                path = os.path.dirname(f.name)

            samples = get_sample()
            envs = get_env(self.number_of_substances_per_env)
            setups = get_setup()
            file_name = self.name.replace(" ", "_")+".xlsx"
            with pd.ExcelWriter(os.path.join(path, file_name)) as writer:
                samples.to_excel(writer, sheet_name='samples', index=False)
                envs.to_excel(writer, sheet_name='environments', index=False)
                setups.to_excel(writer, sheet_name='setups', index=False)
            self.data_file = file_name

        self.method = "Documentation"
