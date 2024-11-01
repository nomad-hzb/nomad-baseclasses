import numpy as np


def get_trpl_archive(data, data_file):
    from baseclasses.solar_energy import TRPLProperties

    trpl_properties = TRPLProperties(
        ns_per_bin=data.ns_per_bin if data.ns_per_bin > 0 else None
    )
    trpl_properties.counts = np.array(data.counts)
    trpl_properties.time = np.array(data.time)
    trpl_properties.name = data_file
    return trpl_properties
