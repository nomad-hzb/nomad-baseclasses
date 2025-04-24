import pandas as pd
from nomad.datamodel.metainfo.basesections import (
    CompositeSystemReference,
)
from nomad.units import ureg

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
    LP50NozzleVoltageProfile,
    NotionNozzleVoltageProfile,
    PrintHeadPath,
    PrintHeadProperties,
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


def get_value(data, key, default=None, number=True, unit=None):
    if not isinstance(key, list):
        key = [key]
    if unit and not isinstance(unit, list):
        unit = [unit]

    try:
        if not unit:
            for k in key:
                if k not in data:
                    continue
                if pd.isna(data[k]):
                    return default
                if number:
                    return float(data[k])
                return str(data[k]).strip()
        if unit:
            for k, u in zip(key, unit):
                if k not in data:
                    continue
                if pd.isna(data[k]):
                    return default
                if number and u:
                    Q_ = ureg.Quantity
                    return Q_(float(data[k]), ureg(u))
        return default
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
        temperature=get_value(data, 'Annealing temperature [°C]', None, unit='°C'),
        time=get_value(data, 'Annealing time [min]', None, unit='minute'),
        atmosphere=get_value(
            data, ['Annealing athmosphere', 'Annealing atmosphere'], None, False
        ),
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
        final_solvents.append(
            SolutionChemical(
                chemical_2=PubChemPureSubstanceSectionCustom(
                    name=get_value(data, f'{solvent} name', None, False),
                    load_data=False,
                ),
                chemical_volume=get_value(
                    data, f'{solvent} volume [uL]', None, unit='uL'
                ),
                amount_relative=get_value(data, f'{solvent} relative amount', None),
            )
        )
    for solute in sorted(set(solutes)):
        final_solutes.append(
            SolutionChemical(
                chemical_2=PubChemPureSubstanceSectionCustom(
                    name=get_value(
                        data, [f'{solute} type', f'{solute} name'], None, False
                    ),
                    load_data=False,
                ),
                concentration_mol=get_value(
                    data, f'{solute} Concentration [mM]', None, unit='mM'
                ),
                concentration_mass=get_value(
                    data,
                    [
                        f'{solute} Concentration [wt%]',
                        f'{solute} Concentration [mg/ml]',
                    ],
                    None,
                    unit=['wt%', 'mg/ml'],
                ),
                amount_relative=get_value(data, f'{solute} relative amount', None),
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
                solution_volume=get_value(
                    data,
                    ['Solution volume [um]', 'Solution volume [uL]'],
                    None,
                    unit=['uL', 'uL'],
                ),
            )
        ],
        annealing=map_annealing(data),
        recipe_steps=[
            SpinCoatingRecipeSteps(
                speed=get_value(data, f'Rotation speed {step}[rpm]', None, unit='rpm'),
                time=get_value(data, f'Rotation time {step}[s]', None, unit='s'),
                acceleration=get_value(
                    data, f'Acceleration {step}[rpm/s]', None, unit='rpm/s'
                ),
            )
            for step in ['', '1 ', '2 ', '3 ', '4 ']
            if get_value(data, f'Rotation time {step}[s]')
        ],
    )
    if get_value(data, 'Anti solvent name', None, False):
        archive.quenching = AntiSolventQuenching(
            anti_solvent_volume=get_value(
                data, 'Anti solvent volume [ml]', None, unit='mL'
            ),
            anti_solvent_dropping_time=get_value(
                data, 'Anti solvent dropping time [s]', None, unit='s'
            ),
            anti_solvent_dropping_height=get_value(
                data, 'Anti solvent dropping heigt [mm]', None, unit='mm'
            ),
            anti_solvent_dropping_flow_rate=get_value(
                data,
                [
                    'Anti solvent dropping speed [ul/s]',
                    'Anti solvent dropping speed [uL/s]',
                ],
                None,
                unit=['uL/s', 'uL/s'],
            ),
            anti_solvent_2=PubChemPureSubstanceSectionCustom(
                name=get_value(data, 'Anti solvent name', None, False), load_data=False
            ),
        )
    if get_value(data, 'Vacuum quenching duration [s]', None, False, unit='s'):
        archive.quenching = VacuumQuenching(
            start_time=get_value(
                data, 'Vacuum quenching start time [s]', None, unit='s'
            ),
            duration=get_value(data, 'Vacuum quenching duration [s]', None, unit='s'),
            pressure=get_value(
                data, 'Vacuum quenching pressure [bar]', None, unit='bar'
            ),
        )

    if get_value(data, 'Gas', None, False):
        archive.quenching = GasQuenchingWithNozzle(
            starting_delay=get_value(
                data, 'Gas quenching start time [s]', None, unit='s'
            ),
            flow_rate=get_value(
                data, 'Gas quenching flow rate [ml/s]', None, unit='ml/s'
            ),
            height=get_value(data, 'Gas quenching height [mm]', None, unit='mm'),
            duration=get_value(data, 'Gas quenching duration [s]', None, unit='s'),
            pressure=get_value(data, 'Gas quenching pressure [bar]', None, unit='bar'),
            velocity=get_value(data, 'Gas quenching velocity [m/s]', None, unit='m/s'),
            nozzle_shape=get_value(data, 'Nozzle shape', None, False),
            nozzle_size=get_value(data, 'Nozzle size [mm²]', None, False, unit='mm**2'),
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
                solution_volume=get_value(
                    data,
                    ['Solution volume [um]', 'Solution volume [uL]'],
                    None,
                    unit=['uL', 'uL'],
                ),
            )
        ],
        layer=map_layer(data),
        annealing=map_annealing(data),
        properties=SlotDieCoatingProperties(
            coating_run=get_value(data, 'Coating run', None, False),
            flow_rate=get_value(
                data,
                ['Flow rate [uL/min]', 'Flow rate [ul/min]'],
                None,
                unit=['uL/minute', 'uL/minute'],
            ),
            slot_die_head_distance_to_thinfilm=get_value(
                data, 'Head gap [mm]', unit='mm'
            ),
            slot_die_head_speed=get_value(data, 'Speed [mm/s]', unit='mm/s'),
            coated_area=get_value(data, 'Coated area [mm²]', unit='mm**2'),
        ),
        quenching=AirKnifeGasQuenching(
            air_knife_angle=get_value(data, 'Air knife angle [°]', None),
            # is this the same as (drying) gas flow rate/velocity?
            bead_volume=get_value(data, 'Bead volume [mm/s]', None, unit='mm/s'),
            drying_speed=get_value(
                data, 'Drying speed [cm/min]', None, unit='cm/minute'
            ),
            air_knife_distance_to_thin_film=get_value(
                data, 'Air knife gap [cm]', None, unit='cm'
            ),
            drying_gas_temperature=get_value(
                data,
                ['Drying gas temperature [°]', 'Drying gas temperature [°C]'],
                None,
                unit=['°C', '°C'],
            ),
            heat_transfer_coefficient=get_value(
                data, 'Heat transfer coefficient [W m^-2 K^-1]', None, unit='W/(K*m**2)'
            ),
        ),
    )
    material = get_value(data, 'Material name', '', False)
    return (f'{i}_{j}_slot_die_coating_{material}', archive)


def map_inkjet_printing(i, j, lab_ids, data, upload_id, inkjet_class):
    location = get_value(data, 'Tool/GB name', '', False)
    archive = inkjet_class(
        name='inkjet printing ' + get_value(data, 'Material name', '', False),
        location=location,
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
                solution_volume=get_value(
                    data,
                    ['Solution volume [um]', 'Solution volume [uL]'],
                    None,
                    unit=['uL', 'uL'],
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
                    data, 'Droplet per second [1/s]', None, unit='1/s'
                ),
                print_speed=get_value(data, 'Printing speed [mm/s]', None, unit='mm/s'),
                print_nozzle_drop_volume=get_value(
                    data,
                    ['Droplet volume [pl]', 'Droplet volume [pL]'],
                    None,
                    unit=['pL', 'pL'],
                ),
                print_head_temperature=get_value(
                    data, 'Nozzle temperature [°C]', None, unit='°C'
                ),
                print_head_distance_to_substrate=get_value(
                    data, 'Dropping Height [mm]', None, unit='mm'
                ),
                print_head_name=get_value(data, 'Printhead name', None, False),
            ),
            cartridge_pressure=get_value(
                data,
                ['Ink reservoir pressure [bar]', 'Ink reservoir pressure [mbar]'],
                None,
                unit=['bar', 'mbar'],
            ),
            substrate_temperature=get_value(
                data, 'Table temperature [°C]', None, unit='°C'
            ),
            drop_density=get_value(data, 'Droplet density [dpi]', None),
            printed_area=get_value(data, 'Printed area [mm²]', None, unit='mm**2'),
        ),
        print_head_path=PrintHeadPath(
            quality_factor=get_value(data, 'Quality factor', None, False),
            step_size=get_value(data, 'Step size', None, False),
            directional=get_value(data, 'Printing direction', None, False),
        ),
        atmosphere=Atmosphere(
            relative_humidity=get_value(data, 'rel. humidity [%]', None),
            temperature=get_value(data, 'Room temperature [°C]', None, unit='°C'),
        ),
        annealing=map_annealing(data),
    )
    if location in ['Pixdro', 'iLPixdro']:  # printer param
        voltage_a = get_value(data, 'Wf Level 1[V]', None, unit='V')
        voltage_b = get_value(data, 'Wf Level 2[V]', None, unit='V')
        voltage_c = get_value(data, 'Wf Level 3[V]', None, unit='V')
        archive.nozzle_voltage_profile = LP50NozzleVoltageProfile(
            number_of_pulses=get_value(data, 'Wf Number of Pulses', None, False),
            voltage_a=voltage_a,
            # umrechnen time [us] = V_level [V]/ rise[V/us]
            rise_edge_a=voltage_a
            / get_value(data, 'Wf Rise 1[V/us]', None, unit='V/us')
            if voltage_a
            else None,
            peak_time_a=get_value(data, 'Wf Width 1[us]', None, unit=['us']),
            fall_edge_a=voltage_a
            / get_value(data, 'Wf Fall 1[V/us]', None, unit='V/us')
            if voltage_a
            else None,
            time_space_a=get_value(data, 'Wf Space 1[us]', None, unit=['us']),
            voltage_b=voltage_b,
            # umrechnen time [us] = V_level [V]/ rise[V/us]
            rise_edge_b=voltage_b
            / get_value(data, 'Wf Rise 2[V/us]', None, unit='V/us')
            if voltage_b
            else None,
            peak_time_b=get_value(data, 'Wf Width 2[us]', None, unit=['us']),
            fall_edge_b=voltage_b
            / get_value(data, 'Wf Fall 2[V/us]', None, unit='V/us')
            if voltage_b
            else None,
            time_space_b=get_value(data, 'Wf Space 2[us]', None, unit=['us']),
            voltage_c=voltage_c,
            # umrechnen time [us] = V_level [V]/ rise[V/us]
            rise_edge_c=voltage_c
            / get_value(data, 'Wf Rise 3[V/us]', None, unit='V/us')
            if voltage_c
            else None,
            peak_time_c=get_value(data, 'Wf Width 3[us]', None, unit=['us']),
            fall_edge_c=voltage_c
            / get_value(data, 'Wf Fall 3[V/us]', None, unit='V/us')
            if voltage_c
            else None,
            time_space_c=get_value(data, 'Wf Space 3[us]', None, unit=['us']),
        )

    if location in ['iLNotion', 'Notion']:  # printer param
        archive.nozzle_voltage_profile = NotionNozzleVoltageProfile(
            number_of_pulses=get_value(data, 'Wf Number of Pulses', None),
            # for loop over number of pulses with changing _a suffix of variales below
            delay_time_a=get_value(data, 'Wf Delay Time [us]', None, unit='us'),
            rise_edge_a=get_value(data, 'Wf Rise Time [us]', None, unit='us'),
            peak_time_a=get_value(data, 'Wf Hold Time [us]', None, unit='us'),
            fall_edge_a=get_value(data, 'Wf Fall Time [us]', None, unit='us'),
            time_space_a=get_value(data, 'Wf Relax Time [us]', None, unit='us'),
            voltage_a=get_value(data, 'Wf Voltage [V]', None, unit='V'),
            # multipulse_a=get_value(data, 'Wf Multipulse [1/0]', None, False),
            number_of_greylevels_a=get_value(data, 'Wf Number Greylevels', None),
            grey_level_0_pulse_a=get_value(
                data, 'Wf Grey Level 0 Use Pulse [1/0]', None
            ),
            grey_level_1_pulse_a=get_value(
                data, 'Wf Grey Level 1 Use Pulse [1/0]', None
            ),
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
                time=get_value(
                    data,
                    [f'Time {i} [s]', f'Time {i} [min]'],
                    None,
                    unit=['s', 'minute'],
                ),
                temperature=get_value(data, f'Temperature {i} [°C]', None, unit='°C'),
                solvent_2=PubChemPureSubstanceSectionCustom(
                    name=get_value(data, f'Solvent {i}', None, False), load_data=False
                ),
            )
            for i in range(10)
            if get_value(data, f'Solvent {i}', None, False)
        ],
        cleaning_uv=[
            UVCleaning(
                time=get_value(
                    data,
                    ['UV-Ozone Time [s]', 'UV-Ozone Time [min]'],
                    None,
                    unit=['s', 'minute'],
                )
            )
        ],
        cleaning_plasma=[
            PlasmaCleaning(
                time=get_value(
                    data,
                    ['Gas-Plasma Time [s]', 'Gas-Plasma Time [min]'],
                    None,
                    unit=['s', 'minute'],
                ),
                power=get_value(data, 'Gas-Plasma Power [W]', None, unit='W'),
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
        solar_cell_area=get_value(data, 'Sample area [cm^2]', None, unit=['cm**2']),
        pixel_area=get_value(
            data, ['Pixel area', 'Pixel area [cm^2]'], None, unit=['cm**2', 'cm**2']
        ),
        number_of_pixels=get_value(data, 'Number of pixels', None),
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
                ] * 2

        if not evaporation:
            return (file_name, archive)

        if get_value(data, f'Source temperature start{mat}[°C]', None) and get_value(
            data, f'Source temperature end{mat}[°C]', None
        ):
            evaporation.temparature = [
                get_value(data, f'Source temperature start{mat}[°C]', None, unit='°C'),
                get_value(data, f'Source temperature end{mat}[°C]', None, unit='°C'),
            ]

        evaporation.thickness = get_value(data, f'Thickness{mat} [nm]', unit='nm')
        evaporation.start_rate = get_value(
            data, f'Rate start{mat} [angstrom/s]', unit='angstrom/s'
        )
        evaporation.target_rate = get_value(
            data,
            [f'Rate{mat} [angstrom/s]', f'Rate target{mat} [angstrom/s]'],
            unit=['angstrom/s', 'angstrom/s'],
        )
        evaporation.substrate_temparature = get_value(
            data, f'Substrate temperature{mat} [°C]', unit='°C'
        )
        evaporation.pressure = get_value(
            data,
            [f'Base pressure{mat} [bar]', f'Base pressure{mat} [mbar]'],
            None,
            unit=['bar', 'mbar'],
        )
        evaporation.pressure_start = get_value(
            data,
            [f'Pressure start{mat} [bar]', f'Pressure start{mat} [mbar]'],
            None,
            unit=['bar', 'mbar'],
        )
        evaporation.pressure_end = get_value(
            data,
            [f'Pressure end{mat} [bar]', f'Pressure end{mat} [mbar]'],
            None,
            unit=['bar', 'mbar'],
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
        thickness=get_value(data, 'Thickness [nm]', unit='nm'),
        gas_flow_rate=get_value(data, 'Gas flow rate [cm^3/min]', unit='cm**3/minute'),
        rotation_rate=get_value(data, 'Rotation rate [rpm]'),
        power=get_value(data, 'Power [W]', unit='W'),
        temperature=get_value(data, 'Temperature [°C]', unit='°C'),
        deposition_time=get_value(data, 'Deposition time [s]', unit='s'),
        burn_in_time=get_value(data, 'Burn in time [s]', unit='s'),
        pressure=get_value(data, 'Pressure [mbar]', unit='mbar'),
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
        thickness=get_value(data, 'Thickness [nm]', unit='nm'),
        substrate_temperature=get_value(data, 'Substrate temperature [°C]', unit='°C'),
        source_temperature=get_value(data, 'Source temperature [°C]', unit='°C'),
        substrate_source_distance=get_value(
            data, 'Substrate source distance [mm]', unit='mm'
        ),
        deposition_time=get_value(data, 'Deposition Time [s]', unit='s'),
        carrier_gas=get_value(data, 'Carrier gas', None, False),
        pressure=get_value(data, 'Process pressure [bar]', None, unit='bar'),
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
                solution_volume=get_value(
                    data,
                    ['Solution volume [um]', 'Solution volume [uL]'],
                    None,
                    unit=['uL', 'uL'],
                ),
            )
        ],
        layer=map_layer(data),
        properties=DipCoatingProperties(
            time=get_value(data, 'Dipping duration [s]', unit='s'),
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
            source=get_value(data, 'Source', None, number=False),
            thickness=get_value(data, 'Thickness [nm]', None),
            temperature=get_value(
                data,
                ['Temperature [°C]', 'Reactor Temperature [°C]'],
                None,
                unit=['°C', '°C'],
            ),
            rate=get_value(data, 'Rate [A/s]', None),
            time=get_value(data, 'Time [s]', None),
            number_of_cycles=get_value(data, 'Number of cycles', None),
            material=ALDMaterial(
                material=PubChemPureSubstanceSectionCustom(
                    name=get_value(data, 'Precursor 1', None, number=False),
                    load_data=False,
                ),
                pulse_duration=get_value(data, 'Pulse duration 1 [s]', None),
                pulse_flow_rate=get_value(data, 'Pulse flow rate 1 [ccm]', None),
                manifold_temperature=get_value(
                    data,
                    [
                        'Manifold Temperature [°C]',
                        'Manifold temperature [°C]',
                        'Manifold temperature 1 [°C]',
                    ],
                    None,
                    unit=['°C', '°C', '°C'],
                ),
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
                manifold_temperature=get_value(
                    data, 'Manifold temperature 2 [°C]', None
                ),
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
