;include paths for any packages we are loading
{% if ssw_paths | length > 0 %}
ssw_path,/{{ ssw_paths | join(', /') }}
{% endif %}
;add any other paths we need to the IDL path
!PATH={%for p in extra_paths%}EXPAND_PATH('{{ p }}')+':'+{%endfor%}!PATH
;run user scripts
.run {{ procedure_filename }}
hissw_procedure
;exit sswidl
exit
