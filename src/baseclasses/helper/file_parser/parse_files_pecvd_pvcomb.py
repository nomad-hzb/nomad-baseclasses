#!/usr/bin/env python3
"""
Created on Tue Mar 14 11:51:01 2023

@author: a2853
"""

import numpy as np
import pandas as pd

from baseclasses.vapour_based_deposition.plasma_enhanced_physical_vapour_deposition import (
    GasFlow,
    LogData,
)


def parse_recipe_line(line):
    if line.startswith('  //') or len(line) < 2:
        return None
    else:
        nl = ''
        for c in line:
            if c == '/':
                break
            nl += c
        return nl.replace(' ', '').replace('\t', '')


def parse_recipe(f, process):
    lines = f.readlines()
    gases = []
    for line in lines:
        pline = parse_recipe_line(line.rstrip())
        if pline:
            key, value = pline.split('=')
            value = float(value)
            if key == 'PC2_rProcPressure[0]':
                process.pressure = value
            if key == 'PC2_rPower[0]':
                process.power = value

            if key == 'PC2_rSetpHub[0]':
                process.plate_spacing = value

            if key == 'PC2_iTimeProcess[0]':
                process.time = value

            if 'Setpoint' in key and value > 10e-8:
                gas = GasFlow()
                if key == 'PC2_rSetpointAr[0]':
                    gas.gas_str = 'Ar'

                if key == 'PC2_rSetpointCO2[0]':
                    gas.gas_str = 'CO2'

                if key == 'PC2_rSetpointH2[0]':
                    gas.gas_str = 'H2'

                if key == 'PC2_rSetpointD2[0]':
                    gas.gas_str = 'D2'

                if key == 'PC2_rSetpointSiH4[0]':
                    gas.gas_str = 'SiH4'

                if key == 'PC2_rSetpointN2O[0]':
                    gas.gas_str = 'N2O'

                if key == 'PC2_rSetpointNH3[0]':
                    gas.gas_str = 'NH3'

                if key == 'PC2_rSetpointN2[0]':
                    gas.gas_str = 'N2'

                if key == 'PC2_rSetpointNF3[0]':
                    gas.gas_str = 'NF3'

                if key == 'PC2_rSetpointPH3[0]':
                    gas.gas_str = 'PH3'

                if key == 'PC2_rSetpointB2H6[0]':
                    gas.gas_str = 'B2H6'

                if gas.gas_str is None:
                    continue

                gas.gas_flow_rate = value
                gases.append(gas)

    process.gases = gases


def parse_log(f, entry, time=None, shift=None):
    data = LogData()
    df = pd.read_csv(f.name, sep='\t', decimal=',')

    powerset = df['DETAIL_PC2.PC2_RFG.SETP']
    powerval = df['DETAIL_PC2.PC2_RFG.ACTVALUE']
    tempval = df['DETAIL_PC2.PC2_HT1.TEMP']
    # tempset = data["DETAIL_PC2.PC2_HT1.TEMPSET"]
    pressureval = df['DETAIL_PC2.PC2_BG.OUTPUT']
    power_ignite = 300  # df["PC2_rPower_ign[0]"]
    ignite = powerset[powerset == power_ignite].index.max()

    data.time = np.array(
        pd.to_timedelta(df['TimeDiff'].str.strip()) / np.timedelta64(1, 's')
    )
    data.power = np.array(powerval)
    data.pressure = np.array(pressureval)
    data.temperature = np.array(tempval)
    # assert powerset.index.max() - ignite > 30

    # if not pd.isnull(ignite) and time is not None and shift is not None:

    data.power_mean = powerval.iloc[ignite + shift : ignite + time + shift].mean()
    data.power_var = powerval.iloc[ignite + shift : ignite + time + shift].var()

    data.temperature_mean = tempval.iloc[ignite + shift : ignite + time + shift].mean()
    data.temperature_var = tempval.iloc[ignite + shift : ignite + time + shift].var()

    data.pressure_mean = pressureval.iloc[ignite + shift : ignite + time + shift].mean()
    data.pressure_var = pressureval.iloc[ignite + shift : ignite + time + shift].var()

    return data
