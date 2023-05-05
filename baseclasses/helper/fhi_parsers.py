#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 10:11:18 2022

@author: a2853
"""
from configparser import ConfigParser
from openpyxl import load_workbook


def getGid(pid):
    split = pid.split("-")[0:4]
    return "-".join(split)


def readXY(datafile):
    import pandas as pd

    data = pd.read_csv(datafile, skiprows=1, header=None, delimiter=" ")
    result = {}

    result.update({"2Theta": list(data[0])})
    result.update({"Intensity": list(data[1])})

    return result


def readUXD(datafile, withdata=True):
    """Reads a uxd-datafile <datafile> and outputs two lists: two_theta,intensity"""
    res = {}

    with open(datafile, 'r') as file:
        for line in file:
            stripped_line = line.strip()
            if len(stripped_line) > 0:

                if stripped_line[0] == ";" and "\t" not in stripped_line:
                    key = ''.join(
                        e for e in stripped_line[1:] if e.isalnum() or e.isspace())
                    entry = {key: {}}
                elif "\t" in stripped_line and stripped_line[0] == ";" and withdata:
                    split = stripped_line[1:].split("\t")
                    keys = list(entry.keys())
                    col0 = split[0].strip()
                    col0 = ''.join(
                        e for e in col0 if e.isalnum() or e.isspace())
                    entry[keys[0]].update({col0: []})
                    col1 = split[1].strip()
                    col1 = ''.join(
                        e for e in col1 if e.isalnum() or e.isspace())
                    entry[keys[0]].update({col1: []})
                elif stripped_line[0] == "_":
                    split = stripped_line[1:].split(" = ")
                    if len(split) == 2:
                        key = ''.join(
                            e for e in split[0] if e.isalnum() or e.isspace())
                        try:
                            elm = {key: float(split[1])}
                        except BaseException:
                            elm = {key: split[1]}
                        keys = list(entry.keys())
                        entry[keys[0]].update(elm)
                elif "\t" in stripped_line and withdata:
                    try:
                        int(stripped_line[0])
                        split = stripped_line.split("\t")
                        keys = list(entry.keys())
                        entry[keys[0]][col0].append(float(split[0]))
                        entry[keys[0]][col1].append(float(split[1]))
                    except Exception as e:
                        print(e)
                        raise Exception
                res.update(entry)

    return res


def readXLSXCatalyticReaction(datafile):
    print(datafile)
    wb = load_workbook(datafile)
    sheet = wb.active
    processeddata = {}
    for col in sheet.columns:
        try:
            float(col[2].value)
            name = str(col[0].value)
            print(name)
            if name in processeddata:
                name += " 2"
            processeddata.update({name: []})
            for i in range(2, len(col)):
                processeddata[name].append(float(col[i].value))
        except BaseException:
            continue

    return processeddata


def readTXTSEM(datafile):
    print(datafile)
    processeddata = {}
    parser = ConfigParser()
    parser.optionxform = str
    parser.read(datafile)
    for each_section in parser.sections():
        for (each_key, each_val) in parser.items(each_section):
            try:
                processeddata.update({each_key: float(each_val)})
            except BaseException:
                processeddata.update({each_key: each_val.replace("\\", "")})

    return processeddata


def readTXTSEM_ov(datafile, withdata=True):
    """Reads a uxd-datafile <datafile> and outputs two lists: two_theta,intensity"""
    res = {}
    energy = []
    count = []
    with open(datafile, 'r') as file:
        for line in file:
            stripped_line = line.strip()
            if len(stripped_line) > 0:
                if stripped_line.startswith("Bruker"):
                    res.update({"name": stripped_line})
                if ":" in stripped_line:
                    split = stripped_line.split(":")
                    if len(split) == 2:
                        res.update({split[0].strip(): split[1].strip()})
                if not withdata:
                    break

        if withdata:
            res.update({"energy": energy})
            res.update({"count": count})

    return res


def readRayFile(datafile, withdata=True):
    import xml.etree.ElementTree as ET

    tree = ET.parse(datafile)
    root = tree.getroot()

    CriticalAngle = float(root.find(
        './/TreeNode[@name="Fit Curve"]/FitCurve/RawCurve').get("CriticalAngle"))
    x0_raw = root.find(
        './/TreeNode[@name="Fit Curve"]/FitCurve/RawCurve/Data/x0').text.strip().split()
    y0_raw = root.find(
        './/TreeNode[@name="Fit Curve"]/FitCurve/RawCurve/Data/y0').text.strip().split()

    chi2 = float(root.find(
        './/TreeNode[@name="Fit Curve"]/FitCurve/FitSolutions/Solution').get("chi2"))
    chi2mode = int(root.find(
        './/TreeNode[@name="Fit Curve"]/FitCurve/FitSolutions/Conditions').get("chi2Mode"))
    method = int(root.find(
        './/TreeNode[@name="Fit Curve"]/FitCurve/FitSolutions/Conditions').get("method"))
    x0_sim = root.find(
        './/TreeNode[@name="Fit Curve"]/FitCurve/FitSolutions/Solution/SimCurve/Data/x0').text.strip().split()
    y_sim = root.find(
        './/TreeNode[@name="Fit Curve"]/FitCurve/FitSolutions/Solution/SimCurve/Data/y').text.strip().split()

    app_roughness = float(root.find(
        './/TreeNode[@name="Fit Curve"]/FitCurve/FitSolutions/Solution/SimCurve/Sample/LayersGroups/LayersGroup/Layers/Layer[@index="0"]/Geometry').get("roughness"))

    app_density = float(root.find(
        './/TreeNode[@name="Fit Curve"]/FitCurve/FitSolutions/Solution/SimCurve/Sample/LayersGroups/LayersGroup/Layers/Layer[@index="0"]/Density').get("top"))

    app_roughness_std = float(root.find(
        './/TreeNode[@name="Fit Curve"]/FitCurve/FitSolutions/Solution/SimCurve/Sample/LayersGroups/LayersGroup/Layers/Layer[@index="0"]/Parameters/Parameter[@id="17"]').get("stdDeviation"))

    app_density_std = float(root.find(
        './/TreeNode[@name="Fit Curve"]/FitCurve/FitSolutions/Solution/SimCurve/Sample/LayersGroups/LayersGroup/Layers/Layer[@index="0"]/Parameters/Parameter[@id="18"]').get("stdDeviation"))

    diffuce_scattering = float(root.find(
        './/TreeNode[@name="Fit Curve"]/FitCurve/FitSolutions/Solution/SimCurve/SimParam').get("poisson"))

    detector_noise = float(root.find(
        './/TreeNode[@name="Fit Curve"]/FitCurve/FitSolutions/Solution/SimCurve/SimParam').get("background_poisson"))

    method_str = ''
    if method == 0:
        method_str = "Levenberg-Marquardt"
    elif method == 1:
        method_str = "VarMetrix/Simplex"

    chi2mode_str = ''
    if chi2mode == 1:
        chi2mode_str = "Logarithm"
    elif chi2mode == 2:
        chi2mode_str = "Logarithm N"

    res = {
        "Critcal Angle": CriticalAngle,
        "chi2": chi2,
        "chi2mode": chi2mode_str,
        "method": method_str,
        "Apparent Roughness": app_roughness,
        "Apparent Roughness Std": app_roughness_std,
        "Apparent Density": app_density,
        "Apparent Density Std": app_density_std,
        "Diffuse Scattering": diffuce_scattering,
        "Detector Noise": detector_noise,
    }

    results_nice = {
        "Critical Angle":
        {
            "symbol": "2theta_c",
            "value": CriticalAngle,
            "unit": "degrees"
        },
        "Apparent Density":
        {
            "symbol": "rho",
            "value": app_density,
            "std. error": app_density_std,
            "unit": "g/cm^3"
        },
        "Apparent Roughness":
            {
            "symbol": "sigma",
            "value": app_roughness,
            "std. error": app_roughness_std,
            "unit": "nm"
        },
        "chi^2":
            {
                "mode": chi2mode_str,
                "symbol": "chi^2",
                "value": chi2,
                "unit": " "
        },
        "Diffuse Scattering":
            {
                "value": diffuce_scattering,
                "unit": " "
        },
        "Detector Noise":
            {
                "value": detector_noise,
                "unit": " "
        }
    }

    if withdata:
        res.update({
            "x0 raw": [float(v) for v in x0_raw],
            "y0 raw": [float(v) for v in y0_raw],
            "x0 sim": [float(v) for v in x0_sim],
            "y sim": [float(v) for v in y_sim],
        })

    return res, results_nice
