from datetime import datetime
import numpy as np
import pandas as pd

from baseclasses.vapour_based_deposition.sputtering import (
    MultiTargetSputteringObservables,
    MultiTargetSputteringProcess,
    TargetProperties
)
from baseclasses import PubChemPureSubstanceSectionCustom

def get_information():
    #multisputtering.description = data.get('Notes')
    pass


def get_observables(observables_df):
    observables = MultiTargetSputteringObservables()
    observables.base_pressure = observables_df.loc['Base Pressure (mbar)', '1']
    temperature = observables_df.loc['Temperature  °C', '1']
    # we set room temperature to 25 based on the obolibrary link provided in the schema
    observables.temperature = 25 if temperature == 'RT' else temperature
    return observables

def get_process_properties(parameters_df, num_targets):
    process_properties = []
    step_names = parameters_df.iloc[9:17]['Unnamed: 1'].tolist()
    parameters_df.drop(columns=['Unnamed: 1'], inplace=True)
    for process_name, process in parameters_df.items():
        if process.isna().all():
            continue
        properties = MultiTargetSputteringProcess()
        properties.process_number = f'step {process_name}'
        properties.orientation = process.get('Orientation (°)')
        properties.sputter_pressure = process.get('Sputter pressure (mB)')
        properties.substrate_temperature = process.get('Substrate Temperature (°C)')
        properties.ramp = process.get('Ramp (°C/min)')
        time_obj = process.get('Time (hh:mm:ss)')
        total_seconds = time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second if not pd.isna(time_obj) else None
        properties.deposition_time = total_seconds
        properties.power = [range(1,9), process.iloc[9:17].tolist()]
        # TODO was passiert wenn weniger targets vorhanden?
        properties.rotation_rate = process.get('Rotation (°/s)')
        properties.z_position = process.get('Z position')
        properties.flow_rate = process.get('Flow Rate (ml/min)')
        gas = process.get('Gas')
        properties.gas = PubChemPureSubstanceSectionCustom(name=gas) if not pd.isna(gas) else None
        process_properties.append(properties)
    return  process_properties


def get_target_properties(source_configuration_df):
    target_properties = []

    # up to 8 targets possible in prevac machine
    for position_idx in range(len(source_configuration_df)):
        properties = TargetProperties()
        material_name = source_configuration_df.loc[position_idx, 'Source']
        properties.name = f'{position_idx + 1}) {material_name}'
        properties.material = PubChemPureSubstanceSectionCustom(name=material_name)
        properties.position = source_configuration_df.loc[position_idx, 'Position']
        properties.angle = source_configuration_df.loc[position_idx, 'Position (grad)']
        properties.rf_dc = source_configuration_df.loc[position_idx, 'RF/DC']
        target_properties.append(properties)

    return target_properties


