def get_pump_rate_archive(data, entry_class):
    entry_class.time = data["Delta T"]
    entry_class.oxygen = data["Oxygen Value"]
    entry_class.temperature = data["Temperature [°C]"]
    entry_class.phase = data["Phase [°]"]
    entry_class.amplitude = data["Amplitude [rel. u.]"]
    entry_class.pressure = data["Pressure [hPa]"]

