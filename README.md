Role Name
=========

This role contains a template and variables that are useful for generating XML configuration files with input-validation and formatting control.

Requirements
------------

None.

Role Variables
--------------

Standard [template](https://docs.ansible.com/ansible/latest/modules/template_module.html#template-module) options are supported, with the following additions and modifications.

| Parameter             | Defaults / Choices / Datatype          | Comments                |
+ ----------------------+----------------------------------------+-------------------------+
| block_end_string      | `}%`                                   | Unchanged from default. |
| block_start_string    | `{%`                                   | Unchanged from default. |
| dest                  | *required* !!str                       | Path to generated file  |
| header                | `{{ ansible-managed|comment("xml") }}` | Static header text.     |
| indent                | 2                                      | Number of spaces to indent contents from surrounding tag.|
| maxlevel              | 10                                     | Maximum tag nesting depth. |
| schema                | *required* !!map                       | Allowed tags and attributes. |
| src                   | [`xml.j2`](templates/xml.j2)           | Set in [main.yml](tasks/main.yml) |
| value                 | *required* !!map                       | XML tags and attributes |
| variable_end_string   | `}}`                                   | Unchanged from default. |
| variable_start_string | `{{`                                   | Unchanged from default. |

[`xml_types`](vars/main.yml) is a hash containing some useful values for schema-building.

Dependencies
------------

None.

Example Playbook
----------------

The following are based on the [w3schools XML Examples](https://www.w3schools.com/xml/xml_examples.asp) page.

Write a [Simple note.](https://www.w3schools.com/xml/note.xml)

```
- include_role:
    name: 'xml'
  vars:
    dest: 'note.xml'
    schema:
      to: '%s'
      from: '%s'
      heading: '%s'
      body: '%s'
    value:
      to: 'Tove'
      from: 'Jani'
      heading: 'Reminder'
      body: "Don't forget me this weekend!"
```

Combine [values](defaults/examples/cd_catalog/values.yml) with [schema](vars/examples/cd_catalog/schema.yml) to produce a [CD catalog](https://www.w3schools.com/xml/cd_catalog.xml)

```
- include_role:
    defaults_from: 'examples/cd_catalog/values.yml'
    name: 'xml'
	vars_from: 'examples/cd_catalog/schema.yml'
  vars:
    dest: 'cd_catalog.xml'
```

License
-------

BSD

Author Information
------------------

Robert August Vincent II  
*(pronounced "Bob" or "Bob-Vee")*  
Security Operations Division  
Office of the Chief Information Security Officer  
U.S. General Services Administration  
Contractor - Team Valiant  
