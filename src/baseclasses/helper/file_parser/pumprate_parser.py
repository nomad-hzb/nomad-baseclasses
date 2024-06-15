import pandas as pd


def get_pump_rate_measurement_csv(file_obj):
    data = pd.read_csv(file_obj.name, sep=";",
                       header=0, skip_blank_lines=False)

    from baseclasses.helper.utilities import lookup
    data['time'] = lookup(
        data.iloc[:, 0], format='%Y-%m-%d %H:%M:%S.%f')
    data["duration"] = (data.time - data.time.iloc[0])
    data["duration_s"] = data.duration.dt.total_seconds()
    return data
