PRO hissw_procedure
    ;run user script
    {{ _script }}
    ;save workspace or desired variables
    save,{% for var in _save_vars %}{{ var }},{% endfor %}filename='{{ _save_filename }}'
END