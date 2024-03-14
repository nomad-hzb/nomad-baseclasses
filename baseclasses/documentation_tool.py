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
   "id": "b0eaf639-2deb-44f7-b901-84096b82a084",
   "metadata": {
    "tags": []
   },
   "outputs": [],
   "source": [
    "from ipyaggrid import Grid \\n",
    "import pandas as pd\\n",
    "import ipywidgets as widgets\\n",
    "import os\\n",
    "import time \\n",
    "import sys\\n",
    "from datetime import date\\n",
    "sys.path.insert(1, '../python-scripts-c6fxKDJrSsWp1xCxON1Y7g')\\n",
    "from api_calls import *\\n",
    "\\n",
    "url = 'https://nomad-hzb-ce.de/nomad-oasis/api/v1'\\n",
    "token = os.environ['NOMAD_CLIENT_ACCESS_TOKEN']\\n",
    "\\n",
    "file = 'docs.xlsx'\\n",
    "entry_id = '<entry_id>'\\n",
    "button_sample = widgets.Button(description='Add Sample')\\n",
    "button_env = widgets.Button(description='Add Environment')\\n",
    "button_setup = widgets.Button(description='Add Setup')\\n",
    "button_create = widgets.Button(description='Create Entries')\\n",
    "date_picker = widgets.DatePicker(value=date.today(),disabled=False)\\n",
    "out = widgets.Output()\\n",
    "out2 = widgets.Output()\\n",
    "samples = pd.DataFrame()\\n",
    "envs = pd.DataFrame()\\n",
    "setups = pd.DataFrame()\\n",
    "\\n",
    "data = {}\\n",
    "def load():\\n",
    "    global samples, envs, setups, data\\n",
    "    xls = pd.ExcelFile(file)\\n",
    "    samples = pd.read_excel(xls, 'samples').astype({'id': 'str'})\\n",
    "    envs = pd.read_excel(xls, 'environments').astype({'id': 'str'})\\n",
    "    setups = pd.read_excel(xls, 'setups').astype({'id': 'str'})\\n",
    "    for i in range(10):\\n",
    "        samples.loc[len(samples)] = pd.Series(dtype='float64')\\n",
    "        envs.loc[len(envs)] = pd.Series(dtype='float64')\\n",
    "        setups.loc[len(setups)] = pd.Series(dtype='float64')\\n",
    "    grid_options = {\\n",
    "        'columnDefs' : [{'headerName':c,'field': c} for c in samples.columns],\\n",
    "        'defaultColDef': {'editable': True},\\n",
    "        'rowSelection': 'multiple',\\n",
    "        'enableRangeSelection': True,\\n",
    "    }\\n",
    "    g1 = Grid(grid_data=samples,grid_options=grid_options,sync_on_edit=True,theme='ag-theme-balham',columns_fit='auto',index=False)\\n",
    "    grid_options.update({'columnDefs':[{'headername':c,'field': c} for c in envs.columns]})\\n",
    "    g2 = Grid(grid_data=envs,grid_options=grid_options,sync_on_edit=True,theme='ag-theme-balham',columns_fit='auto',index=False)\\n",
    "    grid_options.update({'columnDefs':[{'headername':c,'field': c} for c in setups.columns]})\\n",
    "    g3 = Grid(grid_data=setups,grid_options=grid_options,sync_on_edit=True,theme='ag-theme-balham',columns_fit='auto',index=False)\\n",
    "    data = {'samples':g1,\\n",
    "            'envs':g2,\\n",
    "            'setups':g3\\n",
    "       } \\n",
    "    out.clear_output()\\n",
    "    with out:\\n",
    "        display(g1)\\n",
    "\\n",
    "def save():\\n",
    "    global samples, envs, setups\\n",
    "    samples = data['samples'].grid_data_out['grid'] if  data['samples'].grid_data_out else data['samples'].grid_data_in\\n",
    "    samples['id'] = data['samples'].grid_data_in['id'].values\\n",
    "    envs = data['envs'].grid_data_out['grid'] if  data['envs'].grid_data_out else data['envs'].grid_data_in\\n",
    "    envs['id'] = data['envs'].grid_data_in['id'].values\\n",
    "    setups = data['setups'].grid_data_out['grid'] if  data['setups'].grid_data_out else data['setups'].grid_data_in\\n",
    "    setups['id'] = data['setups'].grid_data_in['id'].values\\n",
    "    print(samples)\\n",
    "    with pd.ExcelWriter(file) as writer:\\n",
    "        samples.to_excel(writer, sheet_name='samples', index=False)\\n",
    "        envs.to_excel(writer, sheet_name='environments', index=False)\\n",
    "        setups.to_excel(writer, sheet_name='setups', index=False)\\n",
    "    time.sleep(0.5)\\n",
    "    \\n",
    "def on_button_clicked(b, key):\\n",
    "    global data\\n",
    "    out.clear_output()\\n",
    "    save()\\n",
    "    with out:\\n",
    "        sheet = data[key]\\n",
    "        display(sheet)\\n",
    "        \\n",
    "def on_button_sample_clicked(b):\\n",
    "    on_button_clicked(b, 'samples')\\n",
    "\\n",
    "def on_button_env_clicked(b):\\n",
    "    on_button_clicked(b, 'envs')\\n",
    "\\n",
    "def on_button_setup_clicked(b):\\n",
    "    on_button_clicked(b, 'setups')\\n",
    "\\n",
    "def on_create_clicked(b):\\n",
    "    global samples, envs, setups, data\\n",
    "    save()\\n",
    "    out2.clear_output()\\n",
    "    with out2:\\n",
    "        print('creating entries (can take some time)')\\n",
    "    entry_metadata = get_entry_meta_data(url, token, entry_id)\\n",
    "    set_value_in_archive(url, token, entry_metadata, 'datetime', date_picker.value.strftime('%Y-%m-%d %H:%M:%S.%f'))\\n",
    "    time.sleep(1.0)\\n",
    "    set_value_in_archive(url, token, entry_metadata, 'create_entries', True)\\n",
    "    \\n",
    "    while(True):\\n",
    "        time.sleep(2)\\n",
    "        with out2:\\n",
    "            print('...')\\n",
    "        load()\\n",
    "        if not (samples[samples['id'] == 'nan']['id'].any() or envs[envs['id'] == 'nan']['id'].any() or setups[setups['id'] == 'nan']['id'].any()):\\n",
    "            break\\n",
    "    with out2:\\n",
    "        print('entries created')\\n",
    "\\n",
    "load()\\n",
    "button_sample.on_click(on_button_sample_clicked)\\n",
    "button_env.on_click(on_button_env_clicked)\\n",
    "button_setup.on_click(on_button_setup_clicked)\\n",
    "button_create.on_click(on_create_clicked)\\n",
    "display(widgets.HBox([button_sample, button_env, button_setup, date_picker]))\\n",
    "display(widgets.VBox([out, button_create, out2]))"
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

    create_entries = Quantity(
        type=bool,
        default=False,
        a_eln=dict(component='ButtonEditQuantity')
    )

    number_of_substances_per_env = Quantity(
        type=np.dtype(np.int64),
        default=6,
        a_eln=dict(component='NumberEditQuantity')
    )

    number_of_substances_per_synthesis = Quantity(
        type=np.dtype(np.int64),
        default=6,
        a_eln=dict(component='NumberEditQuantity')
    )

    identifier = SubSection(
        section_def=SampleIDCENOME)

    def normalize(self, archive, logger):
        super(DocumentationTool, self).normalize(archive, logger)

        if not self.data_file:

            with archive.m_context.raw_file(archive.metadata.mainfile) as f:
                path = os.path.dirname(f.name)

            samples = get_sample(self.number_of_substances_per_synthesis)
            envs = get_env(self.number_of_substances_per_env)
            setups = get_setup()
            file_name = self.name.replace(" ", "_")+".xlsx"
            jupyter_string_copy = jupyter_string.replace("docs.xlsx", file_name)
            jupyter_string_copy = jupyter_string_copy.replace("<entry_id>", archive.metadata.entry_id)
            jupyter_file_name = file_name + ".ipynb"
            with archive.m_context.raw_file(jupyter_file_name, 'w') as outfile:
                outfile.write(jupyter_string_copy)
                self.adding_tool = jupyter_file_name

            with pd.ExcelWriter(os.path.join(path, file_name)) as writer:
                samples.to_excel(writer, sheet_name='samples', index=False)
                envs.to_excel(writer, sheet_name='environments', index=False)
                setups.to_excel(writer, sheet_name='setups', index=False)
            self.data_file = file_name

        self.method = "Documentation"

        export_lab_id(archive, self.lab_id)
