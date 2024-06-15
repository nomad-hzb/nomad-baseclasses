import pandas as pd


def get_pfo_measurement_csv(file_obj):
    lookup = '"Date [mm/dd/yyyy]";'
    for num, line in enumerate(file_obj):
        if lookup in line:
            break
    data = pd.read_csv(file_obj.name, sep=";",
                       header=num, skip_blank_lines=False)
    return data


def get_pfo_measurement_xlsx(file):
    dfs = pd.read_excel(file, sheet_name=None)
    for key, df in dfs.items():
        if 'Oxygen Concentration' in df.columns:
            return df
