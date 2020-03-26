#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2019 Jameer Pathan <jameerpathan111@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: foreman_scap_content
short_description: Manage Foreman SCAP content using Foreman API.
description:
  - Create, Update and Delete Foreman SCAP content using Foreman API.
author:
  - "Jameer Pathan (@jameerpathan111)"
options:
  title:
    description:
      - Title of SCAP content.
    required: true
    type: str
  updated_title:
    description:
      - New SCAP content title.
      - When this parameter is set, the module will not be idempotent.
    type: str
  scap_file:
    description:
      - File containing XML SCAP content.
      - Required when creating SCAP content.
    required: false
    type: path
  original_filename:
    description:
      - Original file name of the XML file.
      - If unset, the filename of I(scap_file) will be used.
    required: false
    type: str
extends_documentation_fragment:
  - foreman
  - foreman.entity_state
  - foreman.taxonomy
'''

EXAMPLES = '''
- name: Create SCAP content
  foreman_scap_content:
    title: "Red Hat firefox default content"
    scap_file: "/home/user/Downloads/ssg-firefox-ds.xml"
    original_filename: "ssg-firefox-ds.xml"
    organizations:
      - "Default Organization"
    locations:
      - "Default Location"
    server_url: "https://foreman.example.com"
    username: "admin"
    password: "secret"
    state: present

- name: Update SCAP content
  foreman_scap_content:
    title: "Red Hat firefox default content"
    updated_title: "Updated scap content title"
    scap_file: "/home/user/Downloads/updated-ssg-firefox-ds.xml"
    original_filename: "updated-ssg-firefox-ds.xml"
    organizations:
      - "Org One"
      - "Org Two"
    locations:
      - "Loc One"
      - "Loc Two"
    server_url: "https://foreman.example.com"
    username: "admin"
    password: "secret"
    state: present

- name: Delete SCAP content
  foreman_scap_content:
    title: "Red Hat firefox default content"
    server_url: "https://foreman.example.com"
    username: "admin"
    password: "secret"
    state: absent
'''

RETURN = ''' # '''

import hashlib
import os
from ansible.module_utils.foreman_helper import ForemanTaxonomicEntityAnsibleModule


class ForemanScapContentModule(ForemanTaxonomicEntityAnsibleModule):
    pass


def main():
    module = ForemanScapContentModule(
        argument_spec=dict(
            updated_title=dict(type='str'),
        ),
        foreman_spec=dict(
            title=dict(type='str', required=True),
            original_filename=dict(type='str'),
            scap_file=dict(type='path'),
        ),
        entity_key='title',
        required_plugins=[('openscap', ['*'])],
    )

    with module.api_connection():
        entity, module_params = module.resolve_entities()

        if not module.desired_absent:
            if not entity and 'scap_file' not in module_params:
                module.fail_json(msg="Content of scap_file not provided. XML containing SCAP content is required.")

            if 'scap_file' in module_params and 'original_filename' not in module_params:
                module_params['original_filename'] = os.path.basename(module_params['scap_file'])

            if 'scap_file' in module_params:
                with open(module_params['scap_file']) as input_file:
                    module_params['scap_file'] = input_file.read()

            if entity and 'scap_file' in module_params:
                digest = hashlib.sha256(module_params['scap_file'].encode("utf-8")).hexdigest()
                # workaround for https://projects.theforeman.org/issues/29409
                digest_stripped = hashlib.sha256(module_params['scap_file'].strip().encode("utf-8")).hexdigest()
                if entity['digest'] in [digest, digest_stripped]:
                    module_params.pop('scap_file')

        module.run(module_params=module_params, entity=entity)


if __name__ == '__main__':
    main()
