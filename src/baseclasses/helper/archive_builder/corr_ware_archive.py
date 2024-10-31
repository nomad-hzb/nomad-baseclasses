from datetime import datetime

from nomad.units import ureg


def get_core_ware_archive(entry_class, metadata, data):
    from baseclasses.chemical_energy import VoltammetryCycleWithPlot
    if "curve" in data.index.name:
        if entry_class.cycles is None or len(entry_class.cycles) == 0:
            c = 0
            entry_class.cycles = []
            while (c in data.index):
                curve = data.loc[c]
                cycle = VoltammetryCycleWithPlot()
                cycle.voltage = curve["E(Volts)"]
                cycle.current_density = curve["I(A/cm2)"] * \
                    ureg("A/cm**2")
                cycle.current = curve["I(A/cm2)"] * \
                    ureg("A")
                cycle.time = curve["T(Seconds)"]
                entry_class.cycles.append(cycle)
                c += 1
    else:
        entry_class.voltage = data["E(Volts)"]
        entry_class.current_density = data["I(A/cm2)"] * \
            ureg("A/cm**2")
        entry_class.time = data["T(Seconds)"]
    datetime_str = metadata["Datetime"]
    datetime_object = datetime.strptime(
        datetime_str, '%m-%d-%Y %H:%M:%S')
    entry_class.datetime = datetime_object.strftime(
        "%Y-%m-%d %H:%M:%S.%f")


def get_core_ware_archive_properties(metadata):
    from baseclasses.chemical_energy import CVProperties
    experiment = metadata['Experiment']
    properties = CVProperties()
    properties.initial_potential = experiment.get(
        "Potential #1")
    properties.initial_potential_measured_against = "Eoc" if experiment.get(
        'Potential #1 Type') == 0.0 else "Eref"
    properties.limit_potential_1 = experiment.get(
        'Potential #2')
    properties.limit_potential_1_measured_against = "Eoc" if experiment.get(
        'Potential #2 Type') == 0.0 else "Eref"
    properties.limit_potential_2 = experiment.get(
        'Potential #3')
    properties.limit_potential_2_measured_against = "Eoc" if experiment.get(
        'Potential #3 Type') == 0.0 else "Eref"
    properties.final_potential = experiment.get(
        'Potential #4')
    properties.final_potential_measured_against = "Eoc" if experiment.get(
        'Potential #1 Type') == 0.0 else "Eref"
    properties.scan_rate = experiment.get(
        'Scan Rate')
    properties.cycles = experiment.get(
        'Scan Number')
    properties.open_circuit_potential = metadata.get(
        'Open Circuit Potential (V)')
    return properties
