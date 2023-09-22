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

import random
import string
import chardet
import json

from nomad.metainfo import MProxy
import pandas as pd

from nomad.datamodel.metainfo.basesections import (
    CompositeSystemReference
)


def traverse_dictionary(entry_dict, key, value):

    for k, v in entry_dict.items():
        if isinstance(value, dict):
            traverse_dictionary(v, key, value)
        elif isinstance(value, list):
            for entry in v:
                traverse_dictionary(entry, key, value)
        elif k == key:
            entry_dict[k] = value


def rewrite_json_recursively(archive, key, value):
    with archive.m_context.raw_file(archive.metadata.mainfile) as f:
        file = f.name

    with open(file, "r") as jsonFile:
        data = json.load(jsonFile)
    traverse_dictionary(data, key, value)
    with open(file, "w") as jsonFile:
        json.dump(data, jsonFile)


def rewrite_json(keys_list, archive, value):
    with archive.m_context.raw_file(archive.metadata.mainfile) as f:
        file = f.name

    with open(file, "r") as jsonFile:
        data = json.load(jsonFile)
    tmp = data
    for key in keys_list[:-1]:
        print(tmp)
        tmp = tmp[key]
    tmp[keys_list[-1]] = value

    with open(file, "w") as jsonFile:
        json.dump(data, jsonFile)


def get_parameter(parameters, dictionary, tuple_index=None):
    tmp_dict = dictionary
    try:
        for p in parameters:
            tmp_dict = tmp_dict[p]
        return tmp_dict[tuple_index] if tuple_index else tmp_dict
    except Exception:
        return None


def lookup(date_pd_series, format=None):
    """
    This is an extremely fast approach to datetime parsing.
    For large data, the same dates are often repeated. Rather than
    re-parse these, we store all unique dates, parse them, and
    use a lookup to convert all dates.
    """
    dates = {date: pd.to_datetime(date, format=format)
             for date in date_pd_series.unique()}
    return date_pd_series.map(dates)


def get_encoding(file_obj):
    return chardet.detect(file_obj.read())["encoding"]


def add_next_md_line(key, item, indent=0):
    if key == "m_def":
        return ""
    try:
        shift = '&nbsp;' * indent
        return f"{shift}**{key.capitalize()}**: {item}  \n"
    except Exception as e:
        print(e)
        return "  \n"


def add_key_item(md, key, item, item_entry, indent=0):
    if key in [
        "previous_process",
        "is_standard_process", "positon_in_experimental_plan", "molecular_mass", "inchi", "inchi_key", "smile",
        "canonical_smile", "cas_number", "pub_chem_cid", "pub_chem_link",
        "reload_referenced_solution",
        "samples",
        "batch",
        "name",
        "datetime",
        "lab_id",
            "m_def"]:
        return md
    shift = '&nbsp;' * indent
    if isinstance(item, dict):
        md += f"{shift}**{key.capitalize()}**:  \n"
        for key2, item2 in item.items():
            md = add_key_item(md, key2, item2, getattr(item_entry, key2), 4+indent)
    elif isinstance(item, list):
        md += f"{shift}**{key.capitalize()}**:  \n"
        for list_idx, subsection in enumerate(item):
            shift2 = '&nbsp;' * 4
            md += f"{shift}{shift2}**{list_idx+1}.**  \n"
            for key2, item2 in subsection.items():
                md = add_key_item(md, key2, item2, getattr(item_entry[list_idx], key2), 8+indent)

    elif isinstance(item_entry, MProxy):
        md += add_next_md_line(key, item_entry.name, 4+indent)
        item_dict = item_entry.m_to_dict()
        for key2, item2 in item_dict.items():
            md = add_key_item(md, key2, item2, getattr(
                item_entry, key2), 8+indent)
    else:
        md += add_next_md_line(key, item_entry, indent)
    return md


def add_section_markdown(
        md,
        index_plan,
        index_batch,
        batch_process,
        process_batch):
    md += f"### {index_plan+1}.{index_batch+1} {batch_process.name.capitalize()}  \n"
    data_dict = batch_process.m_to_dict()
    md += f"**Batch Id**: {process_batch}  \n"
    for key, item in data_dict.items():
        try:
            md = add_key_item(md, key, item, getattr(batch_process, key))
        except Exception as e:
            print(e)

    return md


def randStr(chars=string.ascii_uppercase + string.digits, N=6):
    return ''.join(random.choice(chars) for _ in range(N))


def get_entry_id_from_file_name(file_name, archive):
    from nomad.utils import hash
    return hash(archive.metadata.upload_id, file_name)


def update_archive(entity, archive, file_name):
    # use with care
    import json
    entity_entry = entity.m_to_dict(with_root_def=True)
    with archive.m_context.raw_file(file_name, 'w') as outfile:
        json.dump({"data": entity_entry}, outfile)


def create_archive(entity, archive, file_name):
    import json
    if not archive.m_context.raw_path_exists(file_name):
        entity_entry = entity.m_to_dict(with_root_def=True)
        with archive.m_context.raw_file(file_name, 'w') as outfile:
            json.dump({"data": entity_entry}, outfile)
        archive.m_context.process_updated_raw_file(file_name)


def get_reference(upload_id, entry_id):
    return f'../uploads/{upload_id}/archive/{entry_id}#data'


def set_sample_reference(archive, entry, search_id):
    from nomad.search import search
    import inspect
    import baseclasses

    query = {
        'results.eln.lab_ids': search_id
    }
    search_result = search(
        owner='all',
        query=query,
        user_id=archive.metadata.main_author.user_id)
    if len(search_result.data) == 1:
        data = search_result.data[0]
        upload_id, entry_id = data["upload_id"], data["entry_id"]
        if "sample" in data["entry_type"].lower():
            entry.samples = [CompositeSystemReference(reference=get_reference(upload_id, entry_id))]
        if "solution" in data["entry_type"].lower() or "ink" in data["entry_type"].lower():
            entry.samples = [CompositeSystemReference(reference=get_reference(upload_id, entry_id))]


def find_sample_by_id(archive, sample_id):
    from nomad.search import search

    if sample_id is None:
        return None

    query = {
        'results.eln.lab_ids': sample_id
    }

    search_result = search(
        owner='all',
        query=query,
        user_id=archive.metadata.main_author.user_id)
    if len(search_result.data) > 0:
        entry_id = search_result.data[0]["entry_id"]
        upload_id = search_result.data[0]["upload_id"]
        return get_reference(upload_id, entry_id)


def search_class(archive, entry_type):
    from nomad.search import search
    query = {
        'upload_id': archive.metadata.upload_id,
        'entry_type': entry_type
    }
    search_result = search(
        owner='all',
        query=query,
        user_id=archive.metadata.main_author.user_id)
    if len(search_result.data) == 1:
        data = search_result.data[0]
        return data
