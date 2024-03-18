# MIT License

# Copyright (c) 2019

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import pandas as pd

from baseclasses.chemical_energy import GasFEResults

def read_potentiostat_data(file):
    data = pd.read_excel(file, sheet_name='Raw Data', header=1)

    date_time = pd.to_datetime(data['time/s'])
    # TODO compute real time/s
    time = 0
    current = data['<I>/mA']
    working_electrode_potential = data['Ewe/V']

    return date_time, time, current, working_electrode_potential

def read_thermocouple_data(file):
    data = pd.read_excel(file, sheet_name='Raw Data', header=3)

    data['DateTime'] = pd.to_datetime(data['Time Stamp Local'].astype(str))
    data['DateTime'] = data['Date'] + pd.to_timedelta(data['DateTime'].dt.strftime('%H:%M:%S'))
    date_time = data['DateTime'].dropna()
    pressure = data['bar(g)'].dropna()
    temperature_cathode = data['øC  cathode?'].dropna()
    temperature_anode = data['øC  anode?'].dropna()

    return date_time, pressure, temperature_cathode, temperature_anode

def read_gaschromatography_data(file):
    data = pd.read_excel(file, sheet_name='Raw Data', header=1)

    experiment_name = data.loc[0, 'Experiment name']
    data['DateTime'] = pd.to_datetime(data['Time '].astype(str))
    data['DateTime'] = data['Date'] + pd.to_timedelta(data['DateTime'].dt.strftime('%H:%M:%S'))
    datetimes = data['DateTime'].dropna()

    gas_types = data.loc[0, data.columns.str.startswith('Gas type')]
    retention_times = data.loc[:, data.columns.str.startswith('RT')]
    areas = data.loc[:, data.columns.str.startswith('area')]
    ppms = data.loc[:, data.columns.str.startswith('ppm value')]

    retention_times.dropna(axis=0, how='all', inplace=True)
    areas.dropna(axis=0, how='all', inplace=True)
    ppms.dropna(axis=0, how='all', inplace=True)

    return experiment_name, datetimes, gas_types, retention_times, areas, ppms

def read_results_data(file):
    data = pd.read_excel(file, sheet_name='Results', header=0)

    total_flow_rate = data['Total flow rate (ml/min)'].dropna()
    total_fe = data['Total FE (%)'].dropna()

    gas_measurements = []
    current_column_headers = [col for col in data.columns if col.endswith("I (mA)")]

    for col_header in current_column_headers:
        gas_type = col_header.split(' ', 1)[0]
        current = data[col_header].dropna()
        fe = data[" ".join([gas_type, 'FE (%)'])].dropna()
        gas_measurements.append(GasFEResults(
            gas_type=gas_type,
            current=current,
            faradaic_efficiency=fe,
        ))

    return total_flow_rate, total_fe, gas_measurements

def read_properties(file):
    data = pd.read_excel(file, sheet_name='Experimental details', index_col=0, header=None)

    # TODO add missing attributes
    #experiment_id =
    # user
    #cathode
    #anode

    experimental_properties_dict = {
        'cell_type': data.loc['Cell type ', 1],
        'has_reference_electrode': data.loc['Reference Electrode (y/n)', 1] == 'y',
        'reference_electrode_type': data.loc['Reference electrode type', 1],
        'cathode_geometric_area': data.loc['Cathode geometric area', 1],
        'membrane_type': data.loc['Membrane type', 1],
        'membrane_name': data.loc['Membrane Name', 1],
        'membrane_thickness': data.loc['Membrane thickness', 1],
        'gasket_thickness': data.loc['Gasket thickness', 1],
        'anolyte_type': data.loc['Anolyte Type', 1],
        'anolyte_concentration': data.loc['Anolyte Conc. (M)', 1],
        'anolyte_flow_rate': data.loc['Anolyte flow rate (ml/min)', 1],
        'anolyte_volume': data.loc['Anolyte Volume (ml)', 1],
        'has_humidifier': data.loc['Humidifier (y/n)', 1] == 'y',
        'humidifier_temperature': data.loc['Humidifier Temperature', 1],
        'water_trap_volume': data.loc['Water trap volume', 1],
        # TODO 2 possible feed gases
        'feed_gas': data.loc['Feed gas 1', 1],
        'feed_gas_flow_rate': data.loc['Feed gas flow rate (ml/min)', 1].iat[0],
        'bleedline_flow_rate': data.loc['Bleedline flow rate', 1],
        'nitrogen_start_value': data.loc['Nitrogen start value', 1],
        'remarks': data.loc['Remarks', 1],
        'chronoanalysis_method': 'Chronoamperometry (CA)' if data.loc['CP/CA', 1] == 'CA' else 'Chronopotentiometry (CP)',
    }

    return experimental_properties_dict
