import pandas as pd
from nomad.datamodel.metainfo.basesections import (
    CompositeSystemReference,
)

from baseclasses import LayerProperties, PubChemPureSubstanceSectionCustom
from baseclasses.atmosphere import Atmosphere
from baseclasses.material_processes_misc import (
    AirKnifeGasQuenching,
    Annealing,
    AntiSolventQuenching,
    GasQuenchingWithNozzle,
    PlasmaCleaning,
    SolutionCleaning,
    UVCleaning,
    VacuumQuenching,
)
from baseclasses.material_processes_misc.laser_scribing import LaserScribingProperties
from baseclasses.solution import Solution, SolutionChemical
from baseclasses.vapour_based_deposition.atomic_layer_deposition import (
    ALDMaterial,
    ALDPropertiesIris,
)
from baseclasses.vapour_based_deposition.close_space_sublimation import CSSProcess
from baseclasses.vapour_based_deposition.evaporation import (
    InorganicEvaporation,
    OrganicEvaporation,
    PerovskiteEvaporation,
)
from baseclasses.vapour_based_deposition.sputtering import SputteringProcess
from baseclasses.wet_chemical_deposition import PrecursorSolution
from baseclasses.wet_chemical_deposition.dip_coating import DipCoatingProperties
from baseclasses.wet_chemical_deposition.inkjet_printing import (
    InkjetPrintingProperties,
    PrintHeadPath,
    PrintHeadProperties,
    LP50NozzleVoltageProfile,
    NotionNozzleVoltageProfile,
)
from baseclasses.wet_chemical_deposition.slot_die_coating import (
    SlotDieCoatingProperties,
)
from baseclasses.wet_chemical_deposition.spin_coating import SpinCoatingRecipeSteps


def get_entry_id_from_file_name(file_name, upload_id):
    from nomad.utils import hash

    return hash(upload_id, file_name)


def get_reference(upload_id, file_name):
    entry_id = get_entry_id_from_file_name(file_name, upload_id)
    return f'../uploads/{upload_id}/archive/{entry_id}#data'


def convert_quantity(value, factor):
    try:
        return float(value) * factor
    except Exception:
        return None


def get_value(data, key, default=None, number=True):
    try:
        if key not in data:
            return default
        if pd.isna(data[key]):
            return default
        if number:
            return float(data[key])
        return str(data[key]).strip()
    except Exception as e:
        raise e


def map_basic_sample(data, substrate_name, upload_id, sample_class):
    archive = sample_class(
        name=data['Nomad ID'],
        lab_id=data['Nomad ID'],
        substrate=get_reference(upload_id, substrate_name),
        description=get_value(data, 'Variation', None, False),
        number_of_junctions=get_value(data, 'Number of junctions', None),
    )
    return (data['Nomad ID'], archive)


def map_batch(batch_ids, batch_id, upload_id, batch_class):
    archive = batch_class(
        name=batch_id,
        lab_id=batch_id,
        entities=[
            CompositeSystemReference(
                reference=get_reference(upload_id, f'{lab_id}.archive.json'),
                lab_id=lab_id,
            )
            for lab_id in batch_ids
        ],
    )
    return (batch_id, archive)


def map_annealing(data):
    return Annealing(
        temperature=get_value(data, 'Annealing temperature [°C]', None),
        time=convert_quantity(get_value(data, 'Annealing time [min]', None), 60),
        atmosphere=get_value(data, 'Annealing athmosphere', None, False),
    )


def map_layer(data):
    return [
        LayerProperties(
            layer_type=get_value(data, 'Layer type', None, False),
            layer_material_name=get_value(data, 'Material name', None, False),
        )
    ]


def map_solutions(data):
    solvents = []
    solutes = []
    for col in data.index:
        if col.lower().startswith('solvent'):
            solvents.append(' '.join(col.split(' ')[:2]))
        if col.lower().startswith('solute'):
            solutes.append(' '.join(col.split(' ')[:2]))

    final_solvents = []
    final_solutes = []
    for solvent in sorted(set(solvents)):
        if not get_value(data, f'{solvent} name', None, False) and not get_value(
            data, f'{solvent} volume [uL]', None
        ):
            continue
        final_solvents.append(
            SolutionChemical(
                chemical_2=PubChemPureSubstanceSectionCustom(
                    name=get_value(data, f'{solvent} name', None, False),
                    load_data=False,
                ),
                chemical_volume=convert_quantity(
                    get_value(data, f'{solvent} volume [uL]', None), 1 / 1000
                ),
            )
        )
    for solute in sorted(set(solutes)):
        if not get_value(data, f'{solute} type', None, False) and not get_value(
            data, f'{solute} Concentration [mM]', None
        ):
            continue
        final_solutes.append(
            SolutionChemical(
                chemical_2=PubChemPureSubstanceSectionCustom(
                    name=get_value(data, f'{solute} type', None, False), load_data=False
                ),
                concentration_mol=convert_quantity(
                    get_value(data, f'{solute} Concentration [mM]', None), 1 / 1000
                ),
                concentration_mass=convert_quantity(
                    get_value(data, f'{solute} Concentration [wt%]', None), 10
                ),
            )
        )

    archive = Solution(solvent=final_solvents, solute=final_solutes)

    return archive


def map_spin_coating(i, j, lab_ids, data, upload_id, sc_class):
    archive = sc_class(
        name='spin coating ' + get_value(data, 'Material name', '', False),
        location=get_value(data, 'Tool/GB name', '', False),
        positon_in_experimental_plan=i,
        description=get_value(data, 'Notes', '', False),
        samples=[
            CompositeSystemReference(
                reference=get_reference(upload_id, f'{lab_id}.archive.json'),
                lab_id=lab_id,
            )
            for lab_id in lab_ids
        ],
        layer=map_layer(data),
        solution=[
            PrecursorSolution(
                solution_details=map_solutions(data),  # check unit
                # check unit
                solution_volume=convert_quantity(
                    get_value(data, 'Solution volume [um]', None), 1 / 1000
                ),
            )
        ],
        annealing=map_annealing(data),
        recipe_steps=[
            SpinCoatingRecipeSteps(
                speed=get_value(data, f'Rotation speed {step}[rpm]', None),
                time=get_value(data, f'Rotation time {step}[s]', None),
                acceleration=get_value(data, f'Acceleration {step}[rpm/s]', None),
            )
            for step in ['', '1 ', '2 ', '3 ', '4 ']
            if get_value(data, f'Rotation time {step}[s]')
        ],
    )
    if get_value(data, 'Anti solvent name', None, False):
        archive.quenching = AntiSolventQuenching(
            anti_solvent_volume=get_value(data, 'Anti solvent volume [ml]', None),
            anti_solvent_dropping_time=get_value(
                data, 'Anti solvent dropping time [s]', None
            ),
            anti_solvent_dropping_height=get_value(
                data, 'Anti solvent dropping heigt [mm]', None
            ),
            anti_solvent_dropping_flow_rate=get_value(
                data, 'Anti solvent dropping speed [ul/s]', None
            ),
            anti_solvent_2=PubChemPureSubstanceSectionCustom(
                name=get_value(data, 'Anti solvent name', None, False), load_data=False
            ),
        )
    if get_value(data, 'Vacuum quenching duration [s]', None, False):
        archive.quenching = VacuumQuenching(
            start_time=get_value(data, 'Vacuum quenching start time [s]', None),
            duration=get_value(data, 'Vacuum quenching duration [s]', None),
            pressure=get_value(data, 'Vacuum quenching pressure [bar]', None),
        )

    if get_value(data, 'Gas', None, False):
        archive.quenching = GasQuenchingWithNozzle(
            starting_delay=get_value(data, 'Gas quenching start time [s]', None),
            flow_rate=get_value(data, 'Gas quenching flow rate [ml/s]', None),
            height=get_value(data, 'Gas quenching height [mm]', None),
            duration=get_value(data, 'Gas quenching duration [s]', None),
            pressure=get_value(data, 'Gas quenching pressure [bar]', None),
            velocity=get_value(data, 'Gas quenching velocity [m/s]', None),
            nozzle_shape=get_value(data, 'Nozzle shape', None, False),
            nozzle_size=get_value(data, 'Nozzle size [mm²]', None, False),
            gas=get_value(data, 'Gas', None, False),
        )

    material = get_value(data, 'Material name', '', False)
    return (f'{i}_{j}_spin_coating_{material}', archive)


def map_sdc(i, j, lab_ids, data, upload_id, sdc_class):
    archive = sdc_class(
        name='slot die coating ' + get_value(data, 'Material name', '', False),
        location=get_value(data, 'Tool/GB name', '', False),
        positon_in_experimental_plan=i,
        description=get_value(data, 'Notes', None, False),
        samples=[
            CompositeSystemReference(
                reference=get_reference(upload_id, f'{lab_id}.archive.json'),
                lab_id=lab_id,
            )
            for lab_id in lab_ids
        ],
        solution=[
            PrecursorSolution(
                solution_details=map_solutions(data),  # check unit
                # check unit
                solution_volume=convert_quantity(
                    get_value(data, 'Solution volume [um]', None), 1 / 1000
                ),
            )
        ],
        layer=map_layer(data),
        annealing=map_annealing(data),
        properties=SlotDieCoatingProperties(
            coating_run=get_value(data, 'Coating run', None, False),
            flow_rate=convert_quantity(data.get('Flow rate [uL/min]', None), 1 / 1000),
            slot_die_head_distance_to_thinfilm=get_value(data, 'Head gap [mm]'),
            slot_die_head_speed=get_value(data, 'Speed [mm/s]'),
            coated_area=get_value(data, 'Coated area [mm²]'),
        ),
        quenching=AirKnifeGasQuenching(
            air_knife_angle=get_value(data, 'Air knife angle [°]', None),
            # is this the same as (drying) gas flow rate/velocity?
            bead_volume=get_value(data, 'Bead volume [mm/s]', None),
            drying_speed=get_value(data, 'Drying speed [cm/min]', None),
            air_knife_distance_to_thin_film=convert_quantity(
                data.get('Air knife gap [cm]', None), 10000
            ),
            drying_gas_temperature=get_value(data, 'Drying gas temperature [°]', None),
            heat_transfer_coefficient=get_value(
                data, 'Heat transfer coefficient [W m^-2 K^-1]', None
            ),
        ),
    )
    material = get_value(data, 'Material name', '', False)
    return (f'{i}_{j}_slot_die_coating_{material}', archive)


def map_inkjet_nozzle_voltage_profile(data):
    location = get_value(data, 'Tool/GB name', '', False)
    if location in ['Pixdro', 'iLPixdro']: # printer param
                print_head_waveform_parameters=LP50NozzleVoltageProfile(
                    number_of_pulses=get_value(data, 'Wf Number of Pulses', None, False),
                    # for loop over number of pulses with changing _a suffix of variales below needed? There can be max 3 Pulses but if there is less they are potentially not in data..
                    voltage_a=get_value(data, 'Wf Level 1[V]', None, False),
                    rise_edge_a=get_value(data, 'Wf Level 1[V]', None, False) / get_value(data, 'Wf Rise 1[V/us]', None, False), # umrechnen time [us] = V_level [V]/ rise[V/us]
                    peak_time_a=get_value(data, 'Wf Width 1[us]', None, False),
                    fall_edge_a=get_value(data, 'Wf Level 1[V]', None, False) / get_value(data, 'Wf Fall 1[V/us]', None, False), #umrechnen
                    time_space_a=get_value(data, 'Wf Space 1[us]', None, False),
                    voltage_b=get_value(data, 'Wf Level 2[V]', None, False),
                    rise_edge_b=get_value(data, 'Wf Level 2[V]', None, False) / get_value(data, 'Wf Rise 2[V/us]', None, False), # umrechnen time [us] = V_level [V]/ rise[V/us]
                    peak_time_b=get_value(data, 'Wf Width 2[us]', None, False),
                    fall_edge_b=get_value(data, 'Wf Level 2[V]', None, False) / get_value(data, 'Wf Fall 2[V/us]', None, False), #umrechnen
                    time_space_b=get_value(data, 'Wf Space 2[us]', None, False),
                    voltage_c=get_value(data, 'Wf Level 3[V]', None, False),
                    rise_edge_c=get_value(data, 'Wf Level 3[V]', None, False) / get_value(data, 'Wf Rise 3[V/us]', None, False), # umrechnen time [us] = V_level [V]/ rise[V/us]
                    peak_time_c=get_value(data, 'Wf Width 3[us]', None, False),
                    fall_edge_c=get_value(data, 'Wf Level 3[V]', None, False) / get_value(data, 'Wf Fall 3[V/us]', None, False), #umrechnen
                    time_space_c=get_value(data, 'Wf Space 3[us]', None, False),
                    ),

    elif location in ['iLNotion', 'Notion']: # printer param
                print_head_waveform_parameters=NotionNozzleVoltageProfile(
                    number_of_pulses=get_value(data, 'Wf Number of Pulses', None, False),
                    #for loop over number of pulses with changing _a suffix of variales below
                    delay_time_a=get_value(data, 'Wf Delay Time [us]', None, False),
                    rise_edge_a=get_value(data, 'Wf Rise Time [us]', None, False),
                    peak_time_a=get_value(data, 'Wf Hold Time [us]', None, False),
                    fall_edge_a=get_value(data, 'Wf Fall Time [us]', None, False),
                    time_space_a=get_value(data, 'Wf Relax Time [us]', None, False),
                    voltage_a=get_value(data, 'Wf Voltage [V]', None, False),
                    #multipulse_a=get_value(data, 'Wf Multipulse [1/0]', None, False),
                    number_of_greylevels_a=get_value(data, 'Wf Number Greylevels', None, False),
                    grey_level_0_pulse_a=get_value(data, 'Wf Grey Level 0 Use Pulse [1/0]', None, False),
                    grey_level_1_pulse_a=get_value(data, 'Wf Grey Level 1 Use Pulse [1/0]', None, False),
                    )
    return print_head_waveform_parameters


def map_inkjet_printing(i, j, lab_ids, data, upload_id, inkjet_class):
    archive = inkjet_class(
        name='inkjet printing ' + get_value(data, 'Material name', '', False),
        location=get_value(data, 'Tool/GB name', '', False),
        positon_in_experimental_plan=i,
        description=get_value(data, 'Notes', None, False),
        samples=[
            CompositeSystemReference(
                reference=get_reference(upload_id, f'{lab_id}.archive.json'),
                lab_id=lab_id,
            )
            for lab_id in lab_ids
        ],
        solution=[
            PrecursorSolution(
                solution_details=map_solutions(data),  # check unit
                # check unit
                solution_volume=convert_quantity(
                    get_value(data, 'Solution volume [um]', None), 1 / 1000
                ),
            )
        ],
        layer=map_layer(data),
        properties=InkjetPrintingProperties(
            printing_run=get_value(data, 'Printing run', None, False),
            print_head_properties=PrintHeadProperties(
                number_of_active_print_nozzles=get_value(
                    data, 'Number of active nozzles', None
                ),
                print_nozzle_drop_frequency=get_value(
                    data, 'Droplet per second [1/s]', None
                ),
                print_nozzle_drop_volume=get_value(data, 'Droplet volume [pL]', None),
                print_head_temperature=get_value(
                    data, 'Nozzle temperature [°C]', None),
                print_head_distance_to_substrate=get_value(
                    data, 'Dropping Height [mm]', None
                ),
                print_head_name=get_value(data, 'Printhead name', None, False),
                print_head_waveform_parameters = map_inkjet_nozzle_voltage_profile(data),
            ),
            cartridge_pressure=convert_quantity(
                get_value(data, 'Ink reservoir pressure [mbar]', None), 1000
            ),
            substrate_temperature=get_value(data, 'Table temperature [°C]', None),
            drop_density=get_value(data, 'Droplet density [dpi]', None),
            printed_area=get_value(data, 'Printed area [mm²]', None),

            
        ),
        print_head_path=PrintHeadPath(
            quality_factor=get_value(data, 'Quality factor', None, False),
            step_size=get_value(data, 'Step size', None, False),
            directional=get_value(data, 'Printing direction', None, False),
        ),

        atmosphere=Atmosphere(
            relative_humidity=get_value(data, 'rel. humidity [%]', None),
            temperature=get_value(data, 'Room temperature [°C]', None),
        ),
        annealing=map_annealing(data),
    )
    material = get_value(data, 'Material name', '', False)
    return (f'{i}_{j}_inkjet_printing_{material}', archive)


def map_cleaning(i, j, lab_ids, data, upload_id, cleaning_class):
    archive = cleaning_class(
        name='Cleaning',
        positon_in_experimental_plan=i,
        location=get_value(data, 'Tool/GB name', '', False),
        description=get_value(data, 'Notes', '', False),
        samples=[
            CompositeSystemReference(
                reference=get_reference(upload_id, f'{lab_id}.archive.json'),
                lab_id=lab_id,
            )
            for lab_id in lab_ids
        ],
        cleaning=[
            SolutionCleaning(
                time=convert_quantity(get_value(data, f'Time {i} [s]', None), 1 / 60),
                temperature=get_value(data, f'Temperature {i} [°C]', None),
                solvent_2=PubChemPureSubstanceSectionCustom(
                    name=get_value(data, f'Solvent {i}', None, False), load_data=False
                ),
            )
            for i in range(10)
            if get_value(data, f'Solvent {i}', None, False)
        ],
        cleaning_uv=[
            UVCleaning(
                time=convert_quantity(
                    get_value(data, 'UV-Ozone Time [s]', None), 1 / 60
                )
            )
        ],
        cleaning_plasma=[
            PlasmaCleaning(
                time=convert_quantity(
                    get_value(data, 'Gas-Plasma Time [s]', None), 1 / 60
                ),
                power=get_value(data, 'Gas-Plasma Power [W]', None),
                plasma_type=get_value(data, 'Gas-Plasma Gas', None, False),
            )
        ],
    )
    return (f'{i}_{j}_cleaning', archive)


def map_substrate(data, substrate_class):
    archive = substrate_class(
        name='Substrate '
        + get_value(data, 'Sample dimension', '', False)
        + ' '
        + get_value(data, 'Substrate material', '', False)
        + ' '
        + get_value(data, 'Substrate conductive layer', '', False),
        solar_cell_area=get_value(data, 'Sample area [cm^2]', ''),
        substrate=get_value(data, 'Substrate material', '', False),
        description=get_value(data, 'Notes', '', False),
        lab_id=get_value(data, 'Bottom Cell Name', '', False),
        conducting_material=[get_value(data, 'Substrate conductive layer', '', False)],
    )
    return archive


def map_evaporation(
    i, j, lab_ids, data, upload_id, evaporation_class, coevaporation=False
):
    material = get_value(data, 'Material name', '', False)
    file_name = (
        f'{i}_{j}_coevaporation_{material}'
        if coevaporation
        else f'{i}_{j}_evaporation_{material}'
    )
    archive = evaporation_class(
        name='evaporation ' + get_value(data, 'Material name', '', False),
        location=get_value(data, 'Tool/GB name', '', False),
        positon_in_experimental_plan=i,
        description=get_value(data, 'Notes', '', False),
        co_evaporation=coevaporation,
        samples=[
            CompositeSystemReference(
                reference=get_reference(upload_id, f'{lab_id}.archive.json'),
                lab_id=lab_id,
            )
            for lab_id in lab_ids
        ],
        layer=map_layer(data),
    )
    evaporations = []
    for mat in ['', ' 1', ' 2', ' 3', ' 4']:
        if pd.isna(data.get(f'Material name{mat}')) or (
            f'Material name{mat}' == 'Material name' and coevaporation
        ):
            continue
        evaporation = None
        if coevaporation:
            evaporation = PerovskiteEvaporation()
        if get_value(data, 'Organic', '', False).lower().startswith('n') or get_value(
            data, 'Organic', '', False
        ).lower().startswith('0'):
            evaporation = InorganicEvaporation()

        if get_value(data, 'Organic', '', False).lower().startswith('y') or get_value(
            data, 'Organic', '', False
        ).lower().startswith('1'):
            evaporation = OrganicEvaporation()
            if get_value(data, 'Temperature [°C]', None):
                evaporation.temparature = [
                    get_value(data, 'Temperature [°C]', None)
                ] * 2       # warum wird hier die temperatur mit 2 multipliziert?

        if not evaporation:
            return (file_name, archive)

        if get_value(data, f'Source temperature start{mat}[°C]', None) and get_value(
            data, f'Source temperature end{mat}[°C]', None
        ):
            evaporation.temparature = [
                get_value(data, f'Source temperature start{mat}[°C]', None),
                get_value(data, f'Source temperature end{mat}[°C]', None),
            ]

        evaporation.thickness = get_value(data, f'Thickness{mat} [nm]')
        evaporation.start_rate = get_value(data, f'Rate{mat} [angstrom/s]')
        evaporation.substrate_temparature = get_value(
            data, f'Substrate temperature{mat} [°C]'
        )
        evaporation.pressure = convert_quantity(
            get_value(data, f'Base pressure{mat} [bar]'), 1000
        )
        evaporation.pressure_start = convert_quantity(
            get_value(data, f'Pressure start{mat} [bar]'), 1000
        )
        evaporation.pressure_end = convert_quantity(
            get_value(data, f'Pressure end{mat} [bar]'), 1000
        )
        evaporation.tooling_factor = get_value(data, f'Tooling factor{mat}')

        evaporation.chemical_2 = PubChemPureSubstanceSectionCustom(
            name=get_value(data, f'Material name{mat}', None, False), load_data=False
        )
        evaporations.append(evaporation)

    if get_value(data, 'Organic', '', False).lower().startswith('n') or get_value(
        data, 'Organic', '', False
    ).lower().startswith('0'):
        archive.inorganic_evaporation = evaporations
    elif get_value(data, 'Organic', '', False).lower().startswith('y') or get_value(
        data, 'Organic', '', False
    ).lower().startswith('1'):
        archive.organic_evaporation = evaporations
    elif coevaporation:
        archive.perovskite_evaporation = evaporations
    return (file_name, archive)


def map_annealing_class(i, j, lab_ids, data, upload_id, annealing_class):
    archive = annealing_class(
        name='Thermal Annealing',
        positon_in_experimental_plan=i,
        location=get_value(data, 'Tool/GB name', '', False),
        description=get_value(data, 'Notes', '', False),
        samples=[
            CompositeSystemReference(
                reference=get_reference(upload_id, f'{lab_id}.archive.json'),
                lab_id=lab_id,
            )
            for lab_id in lab_ids
        ],
        annealing=map_annealing(data),
        atmosphere=Atmosphere(
            relative_humidity=get_value(data, 'Relative humidity [%]', None),
        ),
    )
    return (f'{i}_{j}_annealing', archive)


def map_sputtering(i, j, lab_ids, data, upload_id, sputter_class):
    archive = sputter_class(
        name='sputtering ' + get_value(data, 'Material name', '', False),
        positon_in_experimental_plan=i,
        location=get_value(data, 'Tool/GB name', '', False),
        description=get_value(data, 'Notes', '', False),
        samples=[
            CompositeSystemReference(
                reference=get_reference(upload_id, f'{lab_id}.archive.json'),
                lab_id=lab_id,
            )
            for lab_id in lab_ids
        ],
        layer=map_layer(data),
    )
    process = SputteringProcess(
        thickness=get_value(data, 'Thickness [nm]'),
        gas_flow_rate=get_value(data, 'Gas flow rate [cm^3/min]'),
        rotation_rate=get_value(data, 'Rotation rate [rpm]'),
        power=get_value(data, 'Power [W]'),
        temperature=get_value(data, 'Temperature [°C]'),
        deposition_time=get_value(data, 'Deposition time [s]'),
        burn_in_time=get_value(data, 'Burn in time [s]'),
        pressure=get_value(data, 'Pressure [mbar]'),
        target_2=PubChemPureSubstanceSectionCustom(
            name=get_value(data, 'Material name', None, False), load_data=False
        ),
        gas_2=PubChemPureSubstanceSectionCustom(
            name=get_value(data, 'Gas', None, False), load_data=False
        ),
    )
    archive.processes = [process]
    material = get_value(data, 'Material name', '', False)
    return (f'{i}_{j}_sputtering_{material}', archive)


def map_close_space_sublimation(i, j, lab_ids, data, upload_id, css_class):
    material = get_value(data, 'Material name', '', False)
    archive = css_class(
        name='Close Space Sublimation ' + get_value(data, 'Material name', '', False),
        location=get_value(data, 'Tool/GB name', '', False),
        positon_in_experimental_plan=i,
        description=get_value(data, 'Notes', '', False),
        samples=[
            CompositeSystemReference(
                reference=get_reference(upload_id, f'{lab_id}.archive.json'),
                lab_id=lab_id,
            )
            for lab_id in lab_ids
        ],
        layer=map_layer(data),
    )
    archive.process = CSSProcess(
        thickness=get_value(data, 'Thickness [nm]'),
        substrate_temperature=get_value(data, 'Substrate temperature [°C]'),
        source_temperature=get_value(data, 'Source temperature [°C]'),
        substrate_source_distance=get_value(data, 'Substrate source distance [mm]'),
        deposition_time=get_value(data, 'Deposition Time [s]'),
        carrier_gas=get_value(data, 'Carrier gas', None, False),
        pressure=convert_quantity(get_value(data, 'Process pressure [bar]'), 1000),
        chemical_2=PubChemPureSubstanceSectionCustom(
            name=get_value(data, 'Material name', None, False), load_data=False
        ),
        material_state=get_value(data, 'Material state', None, False),
    )

    return (f'{i}_{j}_close_space_subimation_{material}', archive)


def map_dip_coating(i, j, lab_ids, data, upload_id, dc_class):
    archive = dc_class(
        name='dip coating ' + get_value(data, 'Material name', '', False),
        location=get_value(data, 'Tool/GB name', '', False),
        positon_in_experimental_plan=i,
        description=get_value(data, 'Notes', None, False),
        samples=[
            CompositeSystemReference(
                reference=get_reference(upload_id, f'{lab_id}.archive.json'),
                lab_id=lab_id,
            )
            for lab_id in lab_ids
        ],
        solution=[
            PrecursorSolution(
                solution_details=map_solutions(data),  # check unit
                # check unit
                solution_volume=convert_quantity(
                    get_value(data, 'Solution volume [um]', None), 1 / 1000
                ),
            )
        ],
        layer=map_layer(data),
        properties=DipCoatingProperties(
            time=convert_quantity(get_value(data, 'Dipping duration [s]'), 1 / 60),
        ),
        annealing=map_annealing(data),
    )
    material = get_value(data, 'Material name', '', False)
    return (f'{i}_{j}_dip_coating_{material}', archive)


def map_laser_scribing(i, j, lab_ids, data, upload_id, laser_class):
    archive = laser_class(
        name='laser scribing',
        positon_in_experimental_plan=i,
        samples=[
            CompositeSystemReference(
                reference=get_reference(upload_id, f'{lab_id}.archive.json'),
                lab_id=lab_id,
            )
            for lab_id in lab_ids
        ],
        recipe_file=get_value(data, 'Recipe file', None, False),
        properties=LaserScribingProperties(
            laser_wavelength=get_value(data, 'Laser wavelength [nm]', None),
            laser_pulse_time=get_value(data, 'Laser pulse time [ps]', None),
            laser_pulse_frequency=get_value(data, 'Laser pulse frequency [kHz]', None),
            speed=get_value(data, 'Speed [mm/s]', None),
            fluence=get_value(data, 'Fluence [J/cm2]', None),
            power_in_percent=get_value(data, 'Power [%]', None),
        ),
    )

    return (f'{i}_{j}_laser_scribing', archive)


def map_atomic_layer_deposition(i, j, lab_ids, data, upload_id, ald_class):
    archive = ald_class(
        name='atomic layer deposition '
        + get_value(data, 'Material name', '', number=False),
        location=get_value(data, 'Tool/GB name', '', False),
        positon_in_experimental_plan=i,
        description=get_value(data, 'Notes', '', number=False),
        samples=[
            CompositeSystemReference(
                reference=get_reference(upload_id, f'{lab_id}.archive.json'),
                lab_id=lab_id,
            )
            for lab_id in lab_ids
        ],
        layer=map_layer(data),
        properties=ALDPropertiesIris(
            #source=get_value(data, 'Source', None, number=False),
            thickness=get_value(data, 'Thickness [nm]', None),
            temperature=get_value(data, 'Reactor Temperature [°C]', None),
            #rate=get_value(data, 'Rate [A/s]', None),
            #time=get_value(data, 'Time [s]', None),
            number_of_cycles=get_value(data, 'Number of cycles', None),
            material=ALDMaterial(
                material=PubChemPureSubstanceSectionCustom(
                    name=get_value(data, 'Precursor 1', None, number=False),
                    load_data=False,
                ),
                pulse_duration=get_value(data, 'Pulse duration 1 [s]', None),
                pulse_flow_rate=get_value(data, 'Pulse flow rate 1 [ccm]', None),
                manifold_temperature=get_value(data, 'Manifold temperature [°C]', None),
                purge_duration=get_value(data, 'Purge duration 1 [s]', None),
                purge_flow_rate=get_value(data, 'Purge flow rate 1 [ccm]', None),
                bottle_temperature=get_value(data, 'Bottle temperature 1 [°C]', None),
            ),
            oxidizer_reducer=ALDMaterial(
                material=PubChemPureSubstanceSectionCustom(
                    name=get_value(
                        data, 'Precursor 2 (Oxidizer/Reducer)', None, number=False
                    ),
                    load_data=False,
                ),
                pulse_duration=get_value(data, 'Pulse duration 2 [s]', None),
                pulse_flow_rate=get_value(data, 'Pulse flow rate 2 [ccm]', None),
               # manifold_temperature=get_value(data, 'Manifold temperature 2 [°C]', None),
                purge_duration=get_value(data, 'Purge duration 2 [s]', None),
                purge_flow_rate=get_value(data, 'Purge flow rate 2 [ccm]', None),
                bottle_temperature=get_value(data, 'Bottle temperature 2 [°C]', None),
            ),
        ),
    )
    material = get_value(data, 'Material name', '', number=False)
    return (f'{i}_{j}_ALD_{material}', archive)


def map_generic(i, j, lab_ids, data, upload_id, generic_class):
    archive = generic_class(
        name=get_value(data, 'Name', '', False),
        positon_in_experimental_plan=i,
        description=get_value(data, 'Notes', '', False),
        samples=[
            CompositeSystemReference(
                reference=get_reference(upload_id, f'{lab_id}.archive.json'),
                lab_id=lab_id,
            )
            for lab_id in lab_ids
        ],
    )
    return (f'{i}_{j}_generic_process', archive)
