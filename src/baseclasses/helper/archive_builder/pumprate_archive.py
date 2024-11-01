def get_pump_rate_archive(data, entry_class):
    entry_class.time = data['duration_s']
    entry_class.flow_rate_set = data.iloc[:, 2]
    entry_class.flow_rate_measured = data.iloc[:, 3]
    entry_class.pressure = data.iloc[:, 1]
    entry_class.datetime = data.iloc[0, 0]
