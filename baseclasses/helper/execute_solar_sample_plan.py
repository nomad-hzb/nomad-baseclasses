#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import numpy as np
import itertools
from nomad.datamodel.metainfo.basesections import CompositeSystemReference, PubChemPureSubstanceSection
from nomad.units import ureg
from .. import ReadableIdentifiersCustom

from ..helper.utilities import get_reference, create_archive, get_entry_id_from_file_name, add_section_markdown, rewrite_json, get_solutions, convert_datetime
from ..solar_energy import SolarCellProperties
from ..wet_chemical_deposition import PrecursorSolution


def log_error(plan_obj, logger, msg):
    if logger:
        logger.error(
            msg, normalizer=plan_obj.__class__.__name__,
            section='system')
    else:
        raise Exception


def set_value(section, path, value, unit):
    path_split = path.split("/")
    next_key = path_split[0]
    if len(path_split) == 1:
        getattr(type(section), next_key)  # to raise an error if key is not defined
        if unit and unit != "None":
            q = ureg.Quantity(float(value), ureg(unit))
            setattr(section, next_key,  q)
        elif next_key == "datetime":
            setattr(section, next_key, convert_datetime(value, datetime_format='%d/%m/%Y %H:%M', utc=False))
        else:
            setattr(section, next_key, value)
    elif isinstance(section, list):
        set_value(section[np.int64(next_key)], "/".join(path_split[1:]), value, unit)
    elif isinstance(section, PrecursorSolution):
        if not section.solution_details:
            section.solution_details = section.solution.m_copy(deep=True)
        set_value(section[next_key], "/".join(path_split[1:]), value, unit)
    elif isinstance(section[next_key], PubChemPureSubstanceSection) and (next_key in ["anti_solvent_2", "chemcial_2"]):
        pubchem = PubChemPureSubstanceSection(load_data=False)
        setattr(section, next_key, pubchem)
        set_value(section[next_key], "/".join(path_split[1:]), value, unit)
    else:
        set_value(section[next_key], "/".join(path_split[1:]), value, unit)


def set_process_parameters(process, parameters, i, plan_obj, logger):
    names = []
    for p in parameters:
        if p[0] == i:
            names.append(str(p[2]).replace("/", ""))
            try:
                set_value(process, p[1], p[2], p[3])
            except Exception as e:
                log_error(plan_obj, logger,
                          f"Could not set {p[1]} to {p[2]} {p[3]}, likely due to a faulty path or unit")
    process.name += f" {','.join(names)}"


def add_sample(plan_obj, archive, idx1, idx2, sample_cls):
    subs = plan_obj.solar_cell_properties.substrate
    architecture = plan_obj.solar_cell_properties.architecture

    # For each sample number, create instance of sample.
    sample_id = f'{plan_obj.lab_id}_{idx1}_{idx2}'
    file_name = f'{sample_id}.archive.json'
    sample = sample_cls(
        name=f'{plan_obj.name} {sample_id}',
        lab_id=sample_id,
        datetime=plan_obj.datetime,
        substrate=subs,
        architecture=architecture)
    create_archive(sample, archive, file_name, overwrite=True)
    entry_id = get_entry_id_from_file_name(file_name, archive)
    return entry_id


def add_batch(plan_obj, archive, batch_cls, sample_refs, is_subbatch, idx1=None):
    file_name = f'{plan_obj.lab_id}'
    if is_subbatch:
        file_name += f"_{idx1}"
    file_name += '.archive.json'
    batch_id = plan_obj.lab_id
    if is_subbatch:
        batch_id += f"_{idx1}"
    batch = batch_cls(
        name=f'{plan_obj.name} {plan_obj.lab_id}_{idx1}' if is_subbatch else f'{plan_obj.name} {plan_obj.lab_id}',
        datetime=plan_obj.datetime,
        lab_id=batch_id,
        entities=[CompositeSystemReference(reference=sample_ref) for sublist in sample_refs for sample_ref in sublist],
        description=plan_obj.description if plan_obj.description and not is_subbatch else None)
    if is_subbatch and plan_obj.substrates_per_subbatch == 1:
        return
    create_archive(batch, archive, file_name, overwrite=True)


def create_documentation(plan_obj, archive, md, solution_list):
    from markdown2 import Markdown
    markdowner = Markdown()
    md = md.replace("_", "\\_")
    sol = f"<b> Solutions for batch {plan_obj.lab_id}</b><br><br>"
    sol += get_solutions(solution_list)
    html = markdowner.convert(md)
    summary_html = "----------start summary----------<br>" + str(sol) + "<br>" + str(html) +\
        "<br>----------end summary----------"
    desc_tmp = plan_obj.description
    if desc_tmp is not None:
        pos_start = desc_tmp.find("----------start summary----------")
        pos_end = desc_tmp.find("----------end summary----------")
        if pos_start > 0 and pos_end > 0:
            desc_tmp = desc_tmp[:pos_start] + desc_tmp[pos_end + 31:]

    plan_obj.description = desc_tmp +\
        summary_html if desc_tmp is not None else summary_html
    output = f"batch_plan_{plan_obj.lab_id}.html"
    with archive.m_context.raw_file(output, 'w') as outfile:
        outfile.write(str(sol) + "<br>" + str(html))
    plan_obj.batch_plan_pdf = output


def add_process(plan_obj, archive, step, process, idx1, idx2):
    file_name_base = f'{plan_obj.lab_id}_{idx1}' if \
        step.vary_parameters else \
        f'{plan_obj.lab_id}'
    if plan_obj.substrates_per_subbatch == 1 and step.vary_parameters:
        file_name_base += "_0"
    file_name = f"{file_name_base}.archive.json"
    entry_id = get_entry_id_from_file_name(file_name, archive)

    process.name = process.name.replace(
        "Standard", "").replace("-", "").strip()
    if plan_obj.substrates_per_subbatch == 1 and step.vary_parameters:
        process.samples = [CompositeSystemReference(reference=get_reference(
            archive.metadata.upload_id, entry_id))]
    else:
        process.batch = get_reference(
            archive.metadata.upload_id, entry_id)

    if "name" in process:
        name = f'{process.name}'
    else:
        name = f'{process.method}'

    if file_name_base not in name:
        name = f'{name} {file_name_base}'

    # file_name_process = f'{name.replace(" ","_")}_{file_name_base}_{randStr()}.archive.json'
    file_name_process = f'{idx2+1}_{name.replace("  ","_").replace(" ","_")}.archive.json'
    process.positon_in_experimental_plan = idx2 + 1
    entry_id = get_entry_id_from_file_name(
        file_name_process, archive)

    if not process.datetime:
        process.datetime = plan_obj.datetime if plan_obj.datetime else ''
    create_archive(process, archive, file_name_process, overwrite=True)
    return file_name_base


def execute_solar_sample_plan(plan_obj, archive, sample_cls, batch_cls, logger=None):
    if plan_obj.plan_is_created:
        log_error(plan_obj, logger, "The experimental plan has already been created. This can not been undone without deleting the files! If you did that uncheck the plan_is_created checkbox.")

    if plan_obj.standard_plan is not None:
        plan_obj.solar_cell_properties = SolarCellProperties(
            substrate=plan_obj.standard_plan.substrate,
            architecture=plan_obj.standard_plan.architecture
        )

    if not (plan_obj.number_of_substrates >= 0
            and plan_obj.number_of_substrates % plan_obj.substrates_per_subbatch == 0
            ):
        log_error(plan_obj, logger,
                  f"Number of substrates is {plan_obj.number_of_substrates} and substrates per subbatch is {plan_obj.substrates_per_subbatch}, which does not devide!")
        return

    number_of_subbatches = plan_obj.number_of_substrates // plan_obj.substrates_per_subbatch

    # standard process integration
    if plan_obj.load_standard_processes:
        plan_obj.load_standard_processes = False
        rewrite_json(["data", "load_standard_processes"], archive, False)

        parameters_before = []
        parameters_linear = []
        parameters_single = []
        for i, step in enumerate(plan_obj.plan):
            if not step.parameters:
                continue
            for parameter in step.parameters:
                if not parameter.parameter_values:
                    log_error(plan_obj, logger, f"Parameter {parameter.parameter_path} has no values!")
                    return
                if len(parameter.parameter_values) > number_of_subbatches:
                    log_error(plan_obj, logger, f"Parameter {parameter.parameter_path} has too many values!")
                    return
                if len(parameter.parameter_values) == 1:
                    parameters_single.append(
                        (i, parameter.parameter_path, parameter.parameter_values[0], parameter.parameter_unit))
                elif len(parameter.parameter_values) == number_of_subbatches:
                    step.vary_parameters = True
                    parameters_linear.append([(i, parameter.parameter_path, val, parameter.parameter_unit)
                                             for val in parameter.parameter_values])
                else:
                    step.vary_parameters = True
                    parameters_before.append([(i, parameter.parameter_path, val, parameter.parameter_unit)
                                             for val in parameter.parameter_values])

        parameters = [[] for x in range(number_of_subbatches)]
        if parameters_before:
            parameters = [list(p) for p in list(itertools.product(*parameters_before))]
            if len(parameters) != number_of_subbatches:
                log_error(plan_obj, logger, 'Not the correct amount of varied parameters given for tensor product')
                return

        for params in parameters_linear:
            for j, p in enumerate(params):
                parameters[j].append(p)

        for i, step in enumerate(plan_obj.plan):
            if not step.vary_parameters:
                process = step.process_reference.m_resolved().m_copy(deep=True)
                set_process_parameters(process, parameters_single, i, plan_obj, logger)
                plan_obj.plan[i].batch_processes = [process]
                continue

            if step.parameters:
                batch_processes = []
                for j in range(number_of_subbatches):
                    process = step.process_reference.m_resolved().m_copy(deep=True)
                    set_process_parameters(process, parameters[j], i, plan_obj, logger)
                    set_process_parameters(process, parameters_single, i, plan_obj, logger)
                    batch_processes.append(process)
                plan_obj.plan[i].batch_processes = batch_processes
            else:
                plan_obj.plan[i].batch_processes = [
                    step.process_reference.m_resolved().m_copy(deep=True)] * number_of_subbatches

    # process, sample and batch creation
    if plan_obj.create_samples_and_processes \
            and plan_obj.lab_id and plan_obj.solar_cell_properties:
        plan_obj.create_samples_and_processes = False
        rewrite_json(["data", "create_samples_and_processes"], archive, False)

        # create samples and batches
        sample_refs = []
        for idx1 in range(number_of_subbatches):
            sample_refs_subbatch = []
            for idx2 in range(plan_obj.substrates_per_subbatch):
                entry_id = add_sample(plan_obj, archive, idx1, idx2, sample_cls)
                sample_refs_subbatch.append(get_reference(
                    archive.metadata.upload_id, entry_id))
            sample_refs.append(sample_refs_subbatch)
            add_batch(plan_obj, archive, batch_cls, [sample_refs_subbatch], True, idx1)

        add_batch(plan_obj, archive, batch_cls, sample_refs, False)

        # create processes
        md = f"# Batch plan of batch {plan_obj.lab_id}\n\n"
        solution_list = []
        for idx2, step in enumerate(plan_obj.plan):
            for idx1, batch_process in enumerate(step.batch_processes):
                if not batch_process.present:
                    continue
                file_name_base = add_process(plan_obj, archive, step, batch_process, idx1, idx2)
                md = add_section_markdown(md,  idx2, idx1, batch_process, file_name_base)
                if "solution" not in batch_process:
                    continue
                for s in getattr(batch_process, "solution", []):
                    if getattr(s, "solution_details"):
                        solution_list.append(s["solution_details"])
                    elif getattr(s, "solution"):
                        solution_list.append(s["solution"])

        create_documentation(plan_obj, archive, md, solution_list)
        plan_obj.plan_is_created = True
        rewrite_json(["data", "plan_is_created"], archive, True)
        rewrite_json(["data", "description"], archive, plan_obj.description)
