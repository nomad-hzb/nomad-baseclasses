import pandas as pd

from baseclasses import PubChemPureSubstanceSectionCustom
from baseclasses.vapour_based_deposition.sputtering import (
    MultiTargetSputteringObservables,
    MultiTargetSputteringProcess,
    TargetProperties,
)


def get_observables(observables_df, num_targets):
    process_observables = []
    observables_df.drop(columns=['Steps'], inplace=True)
    for step_name, step in observables_df.items():
        if step.isna().all():
            continue
        observables = MultiTargetSputteringObservables()
        observables.step_number = f'step {step_name}'
        observables.base_pressure = step.get('Base Pressure (mbar)')
        temperature = step.get('Temperature  °C')
        # we set room temperature to 25 based on the obolibrary link provided in the schema
        observables.temperature = 25 if temperature == 'RT' else temperature
        observables.bias_voltage = step.iloc[3:3+num_targets].tolist()
        observables.bias_current = step.iloc[12:12+num_targets].tolist()
        observables.notes = step.get('Notes') if not pd.isna(
            step.get('Notes')) else None
        process_observables.append(observables)
    return process_observables


def get_process_properties(parameters_df, num_targets):
    process_properties = []
    parameters_df.drop(columns=['Unnamed: 1'], inplace=True)
    for step_name, step in parameters_df.items():
        if step.isna().all():
            continue
        properties = MultiTargetSputteringProcess()
        properties.step_number = f'step {step_name}'
        properties.orientation = step.get('Orientation (°)')
        properties.sputter_pressure = step.get('Sputter pressure (mB)')
        properties.substrate_temperature = step.get('Substrate Temperature (°C)')
        properties.ramp = step.get('Ramp (°C/min)')
        time_obj = step.get('Time (hh:mm:ss)')
        total_seconds = time_obj.hour * 3600 + time_obj.minute * \
            60 + time_obj.second if not pd.isna(time_obj) else None
        properties.deposition_time = total_seconds
        properties.power = step.iloc[9:9+num_targets].tolist()
        properties.rotation_rate = step.get('Rotation (°/s)')
        properties.z_position = step.get('Z position')
        properties.flow_rate = step.get('Flow Rate (ml/min)')
        gas = step.get('Gas')
        properties.gas = PubChemPureSubstanceSectionCustom(
            name=gas, load_data=False) if not pd.isna(gas) else None
        process_properties.append(properties)
    return process_properties


def get_target_properties(source_configuration_df):
    target_properties = []

    # up to 8 targets possible in prevac machine
    for position_idx in range(len(source_configuration_df)):
        properties = TargetProperties()
        material_name = source_configuration_df.loc[position_idx, 'Source']
        properties.name = f'{position_idx + 1}) {material_name}'
        properties.material = PubChemPureSubstanceSectionCustom(
            name=material_name, load_data=False)
        properties.position = source_configuration_df.loc[position_idx, 'Position']
        properties.angle = source_configuration_df.loc[position_idx, 'Position (grad)']
        properties.rf_dc = source_configuration_df.loc[position_idx, 'RF/DC']
        target_properties.append(properties)

    return target_properties
