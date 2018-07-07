PRO hissw_procedure
    ;run user script
    {{ script }}
    ;save workspace or desired variables
    save,{% for var in save_vars %}{{ var }},{% endfor %}filename='{{ save_filename }}'
END