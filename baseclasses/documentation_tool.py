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

from baseclasses.chemical_energy import SampleIDCENOME, export_lab_id

jupyter_string = '''
{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "640cf366-3395-4f4c-b192-9b1287f58119",
   "metadata": {
    "tags": []
   },
   "outputs": [],
   "source": [
    "import ipysheet\n",
    "import pandas as pd\n",
    "import ipywidgets as widgets\n",
    "\n",
    "file = \"docs.xlsx\"\n",
    "\n",
    "button_sample = widgets.Button(description=\"Add Sample\")\n",
    "button_env = widgets.Button(description=\"Add Environment\")\n",
    "button_setup = widgets.Button(description=\"Add Setup\")\n",
    "button_save = widgets.Button(description=\"Save\")\n",
    "button_load = widgets.Button(description=\"Load\")\n",
    "out = widgets.Output()\n",
    "samples = pd.DataFrame()\n",
    "envs = pd.DataFrame()\n",
    "setups = pd.DataFrame()\n",
    "\n",
    "data = {}\n",
    "def load():\n",
    "    global samples, envs, setups, data\n",
    "    xls = pd.ExcelFile(file)\n",
    "    samples = pd.read_excel(xls, 'samples').astype({'id': 'str'})\n",
    "    envs = pd.read_excel(xls, 'environments').astype({'id': 'str'})\n",
    "    setups = pd.read_excel(xls, 'setups').astype({'id': 'str'})\n",
    "    for i in range(10):\n",
    "        samples.loc[len(samples)] = pd.Series(dtype='float64')\n",
    "        envs.loc[len(envs)] = pd.Series(dtype='float64')\n",
    "        setups.loc[len(setups)] = pd.Series(dtype='float64')\n",
    "\n",
    "    samples.fillna('', inplace=True)\n",
    "    envs.fillna('', inplace=True)\n",
    "    setups.fillna('', inplace=True)\n",
    "    data = {\"samples\":ipysheet.from_dataframe(samples),\n",
    "        \"envs\":ipysheet.from_dataframe(envs),\n",
    "        \"setups\":ipysheet.from_dataframe(setups)\n",
    "       } \n",
    "\n",
    "load()\n",
    "  \n",
    "def save():\n",
    "    global samples, envs, setups\n",
    "    samples = ipysheet.to_dataframe(data[\"samples\"])\n",
    "    envs = ipysheet.to_dataframe(data[\"envs\"])\n",
    "    setups = ipysheet.to_dataframe(data[\"setups\"])\n",
    "\n",
    "def on_button_clicked(b, key):\n",
    "    global data\n",
    "    out.clear_output()\n",
    "    save()\n",
    "    with out:\n",
    "        sheet = data[key]\n",
    "        display(sheet)\n",
    "        data.update({key:sheet})\n",
    "        \n",
    "def on_button_sample_clicked(b):\n",
    "    on_button_clicked(b, \"samples\")\n",
    "\n",
    "def on_button_env_clicked(b):\n",
    "    on_button_clicked(b, \"envs\")\n",
    "\n",
    "def on_button_setup_clicked(b):\n",
    "    on_button_clicked(b, \"setups\")\n",
    "\n",
    "def on_save_clicked(b):\n",
    "    save()\n",
    "    with pd.ExcelWriter(file) as writer:\n",
    "        samples.to_excel(writer, sheet_name='samples', index=False)\n",
    "        envs.to_excel(writer, sheet_name='environments', index=False)\n",
    "        setups.to_excel(writer, sheet_name='setups', index=False)\n",
    "\n",
    "def on_load_clicked(b):\n",
    "    out.clear_output()\n",
    "    load()\n",
    "      \n",
    "button_sample.on_click(on_button_sample_clicked)\n",
    "button_env.on_click(on_button_env_clicked)\n",
    "button_setup.on_click(on_button_setup_clicked)\n",
    "button_save.on_click(on_save_clicked)\n",
    "button_load.on_click(on_load_clicked)\n",
    "widgets.VBox([button_load, button_sample, button_env, button_setup, out, button_save])"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.10.10"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
'''


def get_sample(number_of_substances):
    columns = ["id",
               "chemical_composition_or_formula",
               "component_description",
               "producer",
               "project_name_long",
               "description",
               "substrate_type",
               "substrate_dimension",
               "active_area_cm**2",
               "mass_coverage_ug_cm**2",
               "synthesis_method",
               "synthesis_description"
               ]
    substance = ["substance_name", "concentration_M", "concentration_g_per_l", "amount_relative"]
    for i in range(number_of_substances):
        columns.extend([s + "_" + str(i) for s in substance])
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
    substance = ["substance_name", "concentration_M", "concentration_g_per_l", "amount_relative"]
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

    for i in range(5):
        columns.extend(["equipment" + "_" + str(i)])

    return pd.DataFrame(columns=columns)


class DocumentationTool(Entity):

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor')
    )

    adding_tool = Quantity(
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
        default=5,
        a_eln=dict(component='NumberEditQuantity')
    )

    number_of_substances_per_synthesis = Quantity(
        type=np.dtype(np.int64),
        default=5,
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

            samples = get_sample(self.number_of_substances_per_synthesis)
            envs = get_env(self.number_of_substances_per_env)
            setups = get_setup()
            file_name = self.name.replace(" ", "_")+".xlsx"
            jupyter_string_copy = jupyter_string.replace("docs.xlsx", file_name)
            jupyter_file_name = file_name + ".ipynb"
            with open(jupyter_file_name, "w") as f:
                f.write(jupyter_string_copy)
                self.adding_tool = jupyter_file_name

            with pd.ExcelWriter(os.path.join(path, file_name)) as writer:
                samples.to_excel(writer, sheet_name='samples', index=False)
                envs.to_excel(writer, sheet_name='environments', index=False)
                setups.to_excel(writer, sheet_name='setups', index=False)
            self.data_file = file_name

        self.method = "Documentation"

        export_lab_id(archive, self.lab_id)
