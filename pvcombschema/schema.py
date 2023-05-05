from nomad.metainfo import Package, Quantity, SubSection, Section
from nomad.datamodel.data import EntryData

from .processes.pvd_b import PVD_B
from .sample import Sample

m_package = Package()


class PVcomB_Sample(Sample, EntryData):
    m_def = Section(
        a_eln=dict(hide=['users']))


class PVcomB_PVD_B(PVD_B, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time']),
        a_plot=[
            {
                'label': 'LLS and ILR', 'x': 'data/process_time', 'y': ['data/lls', 'data/ilr'],
                "lines": [
                    {
                        "mode": "lines","yaxis": "y"
                    },
                    {
                        "mode": "lines","yaxis": "y2",
                    }
                ],
                'layout': {
                    "showlegend": True,
                    'yaxis': {
                        "fixedrange": False,
                        "side": "left"},        
                    'xaxis': {
                        "fixedrange": False},
                    "yaxis2": {
                        "fixedrange": False, 
                        "side": "right",
                        "overlaying":"y"},
                }
            },
            {
                'label': 'Temperature and Heating Power', 'x': 'data/process_time', 'y': ['data/substrate_temperature', 'data/pyrometer', 'data/heating_power'], 
                "lines": [
                    {
                        "mode": "lines","yaxis": "y"
                    },
                    {
                        "mode": "lines","yaxis": "y"
                    },
                    {
                        "mode": "lines","yaxis": "y2",
                    }
                ],
                'layout': {
                    "showlegend": True,
                    'yaxis': {
                        "fixedrange": False,
                        "side": "left"},        
                    'xaxis': {
                        "fixedrange": False},
                    "yaxis2": {
                        "fixedrange": False, 
                        "side": "right",
                        "overlaying":"y"},
                }
            },
            {
                'label': 'SE Rate and VCSC Valve Position', 'x': 'data/process_time', 'y': ['data/se_rate', 'data/vcsc_valveposition'],
                "lines": [
                    {
                        "mode": "lines","yaxis": "y"
                    },
                    {
                        "mode": "lines","yaxis": "y2",
                    }
                ],
                'layout': {
                    "showlegend": True,
                    'yaxis': {
                        "fixedrange": False,
                        "side": "left"},        
                    'xaxis': {
                        "fixedrange": False},
                    "yaxis2": {
                        "fixedrange": False, 
                        "side": "right",
                        "overlaying":"y"},
                }
            },
            {
                'label': 'Pressure Pump and Growth Chamber and Shroud Temperature Mid', 'x': 'data/process_time', 'y': ['data/pumpchamber_pressure', 'data/growthchamber_pressure', 'data/shroud_temperature_mid'], 
                "lines": [
                    {
                        "mode": "lines","yaxis": "y"
                    },
                    {
                        "mode": "lines","yaxis": "y"
                    },
                    {
                        "mode": "lines","yaxis": "y2",
                    }
                ],
                'layout': {
                    "showlegend": True,
                    'yaxis': {
                        "fixedrange": False,
                        "side": "left"},        
                    'xaxis': {
                        "fixedrange": False},
                    "yaxis2": {
                        "fixedrange": False, 
                        "side": "right",
                        "overlaying":"y"},
                }
            }
        ]
    )

m_package.__init_metainfo__()