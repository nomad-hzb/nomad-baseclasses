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

from nomad.metainfo import MProxy


def get_encoding(file_obj):
    return chardet.detect(file_obj.read())["encoding"]


def add_next_md_line(key, item, indent=0):
    try:
        shift = '&nbsp;' * indent
        return f"{shift}**{key.capitalize()}**: {item}  \n"
    except Exception as e:
        print(e)
        return "  \n"


def add_key_item(md, key, item, item_entry, indent=0):
    if key in [
        "previous_process",
        "is_standard_process",
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
        subsection = getattr(item_entry, key)
        for key2 in item.keys():
            md += add_next_md_line(key2, getattr(subsection, key2), 4+indent)
    elif isinstance(item, list):
        md += f"{shift}**{key.capitalize()}**:  \n"
        for list_idx, subsection in enumerate(item):
            shift2 = '&nbsp;' * 4
            md += f"{shift}{shift2}**{list_idx+1}.**  \n"
            for key2, item2 in subsection.items():
                md += add_next_md_line(key2,
                                       getattr(item_entry[list_idx], key2), 8+indent)
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
        entry.samples = [get_reference(upload_id, entry_id)]


def find_sample_by_id(archive, sample_id):
    from nomad.search import search

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
