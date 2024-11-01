# import glob
from io import StringIO

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import interpolate


def calculatePVparametersFromJV(
    jvData, savename, printing, enablePlot, cellArea=0.105, lineFittingDataPoints=20
):
    digitsPCE = 1
    digitsJSC = 1
    digitsVOC = 5
    digitsFF = 1
    digitsRS = 0
    digitsRSHUNT = 0

    v = jvData[:, 0]
    j = (jvData[:, 1], jvData[:, 2])

    p = (v * j[0], v * j[1])

    ind_mpp = (np.argmax(p[0]), np.argmax(p[1]))

    mpp = ((v[ind_mpp[0]], j[0][ind_mpp[0]]), (v[ind_mpp[1]], j[1][ind_mpp[1]]))

    f0 = interpolate.interp1d(v, j[0])
    f1 = interpolate.interp1d(v, j[1])
    v_new = np.linspace(v[0], v[len(v) - 1], 1000)
    j_interpolated = (f0(v_new), f1(v_new))

    # check if the curve crosses both axes

    if (True in np.diff(np.signbit(j_interpolated[0]))) & (
        True in np.diff(np.signbit(v_new))
    ):
        try:
            voc_ind = (
                np.where(np.diff(np.signbit(j_interpolated[0])))[0].item(),
                np.where(np.diff(np.signbit(j_interpolated[1])))[0].item(),
            )
            voc = (
                np.round(v_new[voc_ind[0]], digitsVOC),
                np.round(v_new[voc_ind[1]], digitsVOC),
            )
        except BaseException:
            voc_ind = (
                np.where(np.diff(np.signbit(j_interpolated[0])))[0][0],
                np.where(np.diff(np.signbit(j_interpolated[1])))[0][0],
            )
            voc = (
                np.round(v_new[voc_ind[0]], digitsVOC),
                np.round(v_new[voc_ind[1]], digitsVOC),
            )

        jsc_ind = (
            np.where(np.diff(np.signbit(v_new)))[0].item(),
            np.where(np.diff(np.signbit(v_new)))[0].item(),
        )

        jsc = (
            np.round(j_interpolated[0][jsc_ind[0]], digitsJSC),
            np.round(j_interpolated[1][jsc_ind[1]], digitsJSC),
        )

        if voc[0] > 0 and jsc[0] > 0:
            ff = (
                np.round((mpp[0][0] * mpp[0][1]) / (voc[0] * jsc[0]) * 100, digitsFF),
                np.round((mpp[1][0] * mpp[1][1]) / (voc[1] * jsc[1]) * 100, digitsFF),
            )
        else:
            ff = (0, 0)

        pce = (
            np.round(voc[0] * jsc[0] * ff[0] / 100, digitsPCE),
            np.round(voc[1] * jsc[1] * ff[1] / 100, digitsPCE),
        )

        try:
            m1, b1 = np.polyfit(
                v_new[
                    voc_ind[0] - lineFittingDataPoints : voc_ind[0]
                    + lineFittingDataPoints
                ],
                j_interpolated[0][
                    voc_ind[0] - lineFittingDataPoints : voc_ind[0]
                    + lineFittingDataPoints
                ],
                1,
            )
            rs_backward = np.round(((-1 / m1) / cellArea) / 1e-3, digitsRS)
        except BaseException:
            rs_backward = np.nan

        try:
            m2, b2 = np.polyfit(
                v_new[
                    voc_ind[1] - lineFittingDataPoints : voc_ind[1]
                    + lineFittingDataPoints
                ],
                j_interpolated[1][
                    voc_ind[1] - lineFittingDataPoints : voc_ind[1]
                    + lineFittingDataPoints
                ],
                1,
            )
            rs_forward = np.round(((-1 / m2) / cellArea) / 1e-3, digitsRS)

        except BaseException:
            rs_forward = np.nan

        r_s = (rs_backward, rs_forward)

        # at JSC there are more data points available
        factor = 4
        factor = 1

        try:
            m3, b3 = np.polyfit(
                v_new[
                    jsc_ind[0] - lineFittingDataPoints * factor : jsc_ind[0]
                    + lineFittingDataPoints * factor
                ],
                j_interpolated[0][
                    jsc_ind[0] - lineFittingDataPoints * factor : jsc_ind[0]
                    + lineFittingDataPoints * factor
                ],
                1,
            )
            i = 1
            while m3 > 0:
                m3, b3 = np.polyfit(
                    v_new[
                        jsc_ind[0] - lineFittingDataPoints + i : jsc_ind[0]
                        + lineFittingDataPoints
                        + i
                    ],
                    j_interpolated[0][
                        jsc_ind[0] - lineFittingDataPoints + i : jsc_ind[0]
                        + lineFittingDataPoints
                        + i
                    ],
                    1,
                )
                i += 1
            rshunt_backward = np.round(((-1 / m3) / cellArea) / 1e-3, digitsRSHUNT)

        except BaseException:
            rshunt_backward = np.nan

        try:
            m4, b4 = np.polyfit(
                v_new[
                    jsc_ind[1] - lineFittingDataPoints * factor : jsc_ind[1]
                    + lineFittingDataPoints * factor
                ],
                j_interpolated[1][
                    jsc_ind[1] - lineFittingDataPoints * factor : jsc_ind[1]
                    + lineFittingDataPoints * factor
                ],
                1,
            )
            i = 1
            while m4 > 0:
                m4, b4 = np.polyfit(
                    v_new[
                        jsc_ind[1] - lineFittingDataPoints * factor + i : jsc_ind[1]
                        + lineFittingDataPoints * factor
                        + i
                    ],
                    j_interpolated[1][
                        jsc_ind[1] - lineFittingDataPoints * factor + i : jsc_ind[1]
                        + lineFittingDataPoints * factor
                        + i
                    ],
                    1,
                )
                i += 1
            rshunt_forward = np.round(((-1 / m4) / cellArea) / 1e-3, digitsRSHUNT)

        except BaseException:
            rshunt_forward = np.nan

        r_shunt = (rshunt_backward, rshunt_forward)

        # if np.isnan(r_s[0])==True:
        #     pce=(np.nan,np.nan)
        #     voc=(np.nan,np.nan)
        #     jsc=(np.nan,np.nan)
        #     ff=(np.nan,np.nan)
        #     r_shunt=(np.nan,np.nan)
        #     r_s=(np.nan,np.nan)

        # if (r_s[0] > 10000) and (r_shunt[0] > 10000):
        #     pce=(np.nan,np.nan)
        #     voc=(np.nan,np.nan)
        #     jsc=(np.nan,np.nan)
        #     ff=(np.nan,np.nan)
        #     r_shunt=(np.nan,np.nan)
        #     r_s=(np.nan,np.nan)

        # if (r_s[0] < 0) or (r_shunt[0] < 0) or (pce[0] < 0) or (voc[0] < 0) or (jsc[0] < 0) or (ff[0] < 0):
        #     pce=(np.nan,np.nan)
        #     voc=(np.nan,np.nan)
        #     jsc=(np.nan,np.nan)
        #     ff=(np.nan,np.nan)
        #     r_shunt=(np.nan,np.nan)
        #     r_s=(np.nan,np.nan)

        # if (jsc[0] > 25) :
        #     pce=(np.nan,np.nan)
        #     voc=(np.nan,np.nan)
        #     jsc=(np.nan,np.nan)
        #     ff=(np.nan,np.nan)
        #     r_shunt=(np.nan,np.nan)
        #     r_s=(np.nan,np.nan)

        if enablePlot:
            plt.figure(figsize=(10, 5))
            try:
                plt.plot(v_new, m4 * v_new + b4, 'r')
                plt.plot(v_new, m3 * v_new + b3, 'r')
            except BaseException:
                pass

            try:
                plt.plot(v_new, m2 * v_new + b2, 'k')
                plt.plot(v_new, m1 * v_new + b1, 'k')
            except BaseException:
                pass

            plt.plot(mpp[0][0], mpp[0][1], 'o')
            plt.plot(mpp[1][0], mpp[1][1], 'o')
            plt.plot(voc[0], 0, 'x')
            plt.plot(voc[1], 0, 'x')
            plt.plot(0, jsc[0], 'x')
            plt.plot(0, jsc[1], 'x')

    else:
        pce = (np.nan, np.nan)
        voc = (np.nan, np.nan)
        jsc = (np.nan, np.nan)
        ff = (np.nan, np.nan)
        r_shunt = (np.nan, np.nan)
        r_s = (np.nan, np.nan)

    s = f'pce = {pce} % \n'
    s += f'voc = {voc} V \n'
    s += f'jsc = {jsc} mA/cm2 \n'
    s += f'ff = {ff} % \n'
    s += f'r_shunt = {r_shunt} Ohm/cm2 \n'
    s += f'r_s = {r_s} Ohm/cm2\n'
    s += f'mpp = {mpp} mA/cm2 V'

    if printing:
        print(s)
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)

    if enablePlot:
        plt.plot(v_new, j_interpolated[0])
        plt.plot(v_new, j_interpolated[1])

        # plt.text(1.3, 29, s, fontsize=14, verticalalignment='top', bbox=props)
        plt.text(
            -0.2, -5, s, fontsize=14, verticalalignment='top', bbox=props, alpha=0.3
        )
        plt.axhline(y=0, xmin=-0.25, xmax=1.25, color='k')
        plt.axvline(x=0, ymin=-2, ymax=30, color='k')
        plt.ylim(-2, 30)
        plt.tight_layout
        # plt.show()

    if printing:
        print('-' * 60)

    return pce, voc, jsc, ff, r_shunt, r_s, mpp


def get_jv_data(filedata):
    df_header = pd.read_csv(
        StringIO(filedata),
        skiprows=0,
        nrows=10,
        sep='\t',
        # index_col=0,
        engine='python',
    )

    jv_dict = {}
    jv_dict['active_area'] = float(df_header.iloc[1, 1])
    jv_dict['datetime'] = f'{df_header.iloc[3, 0]} {df_header.iloc[3, 1]}'
    # jv_dict['intensity'] = df_header.iloc[1, 1]
    # jv_dict['integration_time'] = df_header.iloc[2, 1]
    # jv_dict['settling_time'] = df_header.iloc[3, 1]
    # jv_dict['averaging'] = df_header.iloc[4, 1]
    # jv_dict['compliance'] = df_header.iloc[5, 1]

    df = pd.read_csv(
        StringIO(filedata),
        skiprows=0,
        nrows=10,
        sep='\t',
        # index_col=0,
        engine='python',
    )

    jv_dict['J_sc'] = list(np.abs([float(df.iloc[4, 1]), float(df.iloc[4, 2])]))
    jv_dict['V_oc'] = list(np.abs([float(df.iloc[5, 1]), float(df.iloc[5, 2])]))
    jv_dict['Fill_factor'] = list([float(df.iloc[6, 1]), float(df.iloc[6, 2])])
    jv_dict['Efficiency'] = list([float(df.iloc[7, 1]), float(df.iloc[7, 2])])

    df_curves = pd.read_csv(
        StringIO(filedata),
        # header=0,
        skiprows=11,
        sep='\t',
        engine='python',
    )
    df_curves = df_curves.dropna(how='all', axis=1)

    if df_curves.iloc[0, 0] < 0:
        # df_curves = df_curves*-1
        j_columns = ['Voltage [V]']
        df_curves[j_columns] = df_curves[j_columns] * -1
        print('inverted')
    else:
        j_columns = [
            'Current density [1] [mA/cm^2]',
            'Current density [2] [mA/cm^2]',
            'Average current density [mA/cm^2]',
        ]
        df_curves[j_columns] = df_curves[j_columns] * -1

    jv_dict['jv_curve'] = []
    for column in range(1, len(df_curves.columns) - 1):
        jv_dict['jv_curve'].append(
            {
                'name': df_curves.columns[column],
                'voltage': df_curves[df_curves.columns[0]].values,
                'current_density': df_curves[df_curves.columns[column]].values,
            }
        )

    # PCE, VOC, JSC, FF, RSHUNT, RS, mpp = calculatePVparametersFromJV(np.array(
    #     df_curves), "", printing=False, enablePlot=True, cellArea=jv_dict['active_area'], lineFittingDataPoints=20)

    _, _, _, _, RSHUNT, RS, mpp = calculatePVparametersFromJV(
        np.array(df_curves),
        '',
        printing=False,
        enablePlot=True,
        cellArea=jv_dict['active_area'],
        lineFittingDataPoints=20,
    )

    jv_dict['P_MPP'] = list(
        (np.round(mpp[0][0] * mpp[0][1], 2), np.round(mpp[1][0] * mpp[1][1], 2))
    )
    jv_dict['J_MPP'] = list((mpp[0][1], mpp[1][1]))
    jv_dict['U_MPP'] = list((mpp[0][0], mpp[1][0]))
    jv_dict['R_ser'] = list(RS)
    jv_dict['R_par'] = list(RSHUNT)

    return jv_dict


# filename="/home/a2853/Documents/Projects/nomad/perotf_examplary_jv_data/CR/ACL2_1_02_Cycle_0_illu.csv"
# filename="examplary_jv_data/TFL/R4_XC2_thick_01_Cycle_2_illu.csv"
# filename="examplary_jv_data/TFL/B4_01_GB_03_Cycle_1_illu.csv"
# filename="examplary_jv_data/CR/MB3_Thick flipped_01_Cycle_1_illu.csv"
# filename="examplary_jv_data/CR/MB1_Thick_No2P_01_Cycle_1_illu.csv"
# filename="examplary_jv_data/CR/Cell-01-Ref_02_Cycle_2_illu.csv"


# jv_info=get_jv_data(filename, encoding='ISO-8859-1')
