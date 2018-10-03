xml
===

This role contains a template and variables that are useful for generating XML configuration files with input-validation and formatting control.

Requirements
------------

None.

Role Variables
--------------

Standard [template](https://docs.ansible.com/ansible/latest/modules/template_module.html#template-module)
options are supported, except for `block_end_string`, `block_start_string`,
`lstrip_blocks`, `src`, `trim_blocks`, `variable_end_string`,
and `variable_start_string`.

Additional parameters are:

| Required | Datatype | Comments                     |
|----------|----------|------------------------------|
| dest     | string   | Path to generated file       |
| schema   | dict     | Allowed tags and attributes. |
| value    | dict     | XML content to render.       |

| Optional | Datatype | Comments:  Defaults                                           |
|----------|----------|---------------------------------------------------------------|
| header   | string   | Static header text: `{{ ansible_managed\|comment("xml") }}`   |
| spaces   | int      | Nested tag indentation: `2` |

Dependencies
------------

None.

Example Playbook
----------------

*(Data copied from [Qt Documentation](https://doc.qt.io/))*

Combine recipe [values](defaults/examples/recipes/values.yml) with [schema](vars/examples/recipes/schema.yml) to produce a [cookbook](http://doc.qt.io/qt-5/qtxmlpatterns-recipes-files-cookbook-xml.html).

```
- hosts: localhost
  tasks:
    - include_role:
        defaults_from: 'examples/recipes/values.yml'
        name: 'xml'
        vars_from: 'examples/recipes/schema.yml'
      vars:
        dest: 'cookbook.xml'
```

To-Do
-----

* Tests
* Better examples
* Code a way to require that an element must contain one of a list
  of attributes, or be non-empty.

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
