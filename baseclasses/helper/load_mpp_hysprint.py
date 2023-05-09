import pandas as pd
import re


def filter_columns(columns):
    matched_columns = []
    for column in columns:
        matched = re.match("^Anlage_Box\d*_Probe\(\d*\)_Pixel\(\d*\)", column)
        if not bool(matched):
            continue
        matched_columns.append(column)

    return matched_columns


def get_integer(string):
    return int(string.replace("(", "").replace(")", ""))


def get_dimensions(columns):
    columns = filter_columns(columns)
    box = int(columns[0].split("_")[1][3:])
    number_of_sample = max([get_integer(c.split("_")[2][5:])
                           for c in columns])+1
    number_of_pixels = max([get_integer(c.split("_")[3][5:])
                           for c in columns])+1

    return {"box": box, "number_of_samples": number_of_sample, "number_of_pixels": number_of_pixels}


def process_timestamp(df):
    df.Timestamp = df.Timestamp.astype('datetime64[ns]')
    df["Duration"] = (df.Timestamp - df.Timestamp.iloc[0])
    df["Duration_s"] = df.Duration.dt.total_seconds()
    df["Duration_h"] = df.Duration.dt.total_seconds()/3600


def process_mpp_data(df):
    df["MPPT_J"] = df.InMPPT_I.abs()  # division by area in normalizer
    df["MPPT_V"] = df.InMPPT_V / 1000
    df["MPPT_EFF"] = (df.MPPT_J * df.MPPT_V * 1000 / df.InEinstrahlung).abs()
    if df.empty:
        return
    process_timestamp(df)


def process_mpp_data_jv(df, suffix):
    # division by area in normalizer
    df["J_sc"] = df[f"InIV_I_sc{suffix}"].abs()
    df["V_oc"] = df[f"InIV_V_oc{suffix}"] / 1000
    df["n"] = df[f"InIV_n{suffix}"]
    df["FF"] = df[f"InIV_FF{suffix}"] * 100
    if df.empty:
        return
    process_timestamp(df)


def rename_columns(df, box, sample_id, pixel_id):
    columns_new = {}
    for column in df.columns:
        columns_new.update({column: column.replace(f"Anlage_Box{box}_", "").replace(
            f"Probe({sample_id})_", "").replace(f"Pixel({pixel_id})_", "")})
    columns_new["Zeitstempel"] = "Timestamp"
    df = df.rename(columns=columns_new)
    return df


def apply_filter_trigger_code(df, box, trigger_code):
    df_filtered = df.loc[(
        df[f"Anlage_Box{box}_InTriggerSource"] == trigger_code)]
    df_final = df_filtered.drop(columns=[f"Anlage_Box{box}_InTriggerSource"])
    return df_final


def filter_and_process_mpp_data(df, box, sample_id, pixel_id, trigger_code):
    df_filtered = apply_filter_trigger_code(df, box, trigger_code)
    df_filtered = df.loc[(
        df[f"Anlage_Box{box}_Probe({sample_id})_Pixel({pixel_id})_InMPPT_I"] > -999)]

    df_final = rename_columns(df_filtered, box, sample_id, pixel_id)
    process_mpp_data(df_final)
    return df_final


def calculate_trigger_code_jv(box, sample_id, pixel_id):
    return (box-1)*48+sample_id*6+pixel_id + 1


def get_jv_data(df, box, sample_id, pixel_id, forward=True):
    suffix = ''
    if not forward:
        suffix = "_rev"
    columns = ["Zeitstempel", f"Anlage_Box{box}_Probe({sample_id})_Pixel({pixel_id})_InIV_V_oc{suffix}",
               f"Anlage_Box{box}_Probe({sample_id})_Pixel({pixel_id})_InIV_FF{suffix}",
               f"Anlage_Box{box}_Probe({sample_id})_Pixel({pixel_id})_InIV_n{suffix}",
               f"Anlage_Box{box}_Probe({sample_id})_Pixel({pixel_id})_InIV_I_sc{suffix}",
               f"Anlage_Box{box}_InTriggerSource"]
    df_raw = df[columns].copy()

    trigger_code_jv = calculate_trigger_code_jv(box, sample_id, pixel_id)
    if not forward:
        trigger_code_jv = (-1) * trigger_code_jv
    df_filtered = apply_filter_trigger_code(df_raw, box, trigger_code_jv)
    df_final = rename_columns(df_filtered, box, sample_id, pixel_id)
    process_mpp_data_jv(df_final, suffix)
    return df_final


def parse_pixel(box, sample_id, pixel_id, df):
    columns = ["Zeitstempel", f"Anlage_Box{box}_Probe({sample_id})_Pixel({pixel_id})_InMPPT_I",
               f"Anlage_Box{box}_Probe({sample_id})_Pixel({pixel_id})_InMPPT_V", f"Anlage_Box{box}_Probe({sample_id})_InEinstrahlung",
               f"Anlage_Box{box}_InTriggerSource"]
    df_raw = df[columns].copy()
    df_final = filter_and_process_mpp_data(
        df_raw, box, sample_id, pixel_id, trigger_code=0)

    columns_dark = columns.copy()
    columns_dark.append(f"Anlage_Box{box}_InShutterState")
    df_raw_dark = df[columns_dark].copy()
    df_final_dark = filter_and_process_mpp_data(
        df_raw_dark, box, sample_id, pixel_id, trigger_code=10000)

    data_jv_for = get_jv_data(df, box, sample_id, pixel_id, forward=True)
    data_jv_rev = get_jv_data(df, box, sample_id, pixel_id, forward=False)

    data = {"id": pixel_id,
            "data": df_final, "data_dark": df_final_dark, "data_jv_for": data_jv_for, "data_jv_rev": data_jv_rev}
    return data


def parse_sample(info, sample_id, df):
    df_sample = df[["Zeitstempel", f"Anlage_Box{info['box']}_Probe({sample_id})_InTemperatur",
                    f"Anlage_Box{info['box']}_Probe({sample_id})_InEinstrahlung"]].copy()
    df_sample = rename_columns(df_sample, info['box'], sample_id, None)
    process_timestamp(df_sample)
    data = {
        "id": sample_id,
        "data": df_sample,
        "pixels": []
    }

    for pixel_id in range(info["number_of_pixels"]):
        pixel_data = parse_pixel(info["box"], sample_id, pixel_id, df)
        data["pixels"].append(pixel_data)

    return data


def load_mpp_file(filename):
    df = pd.read_csv(filename, sep=";")
    info = get_dimensions(df.columns)
    print(info)

    data = {"samples": [],
            "box": info["box"]}
    for sample_id in range(info["number_of_samples"]):
        sample_data = parse_sample(info, sample_id, df)
        data["samples"].append(sample_data)

    return data


# filename = "/home/a2853/Documents/Projects/nomad/hysprintlab/titan/20230503_AgeingTest_Example/20230331_113543_Jiahuan-2/Data.csv"
# d = load_mpp_file(filename)
