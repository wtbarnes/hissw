#!/bin/tcsh
# Set SSW home
setenv SSW {{ ssw_home }}
# Set SSW instruments
setenv SSW_INSTR "{{ ssw_packages | join(' ') }}"
# Setup needed environment variables
{% if ssw_home is not none %}
source $SSW/gen/setup/setup.ssw
{% endif %}
# Setup IDL environment
setenv IDL_DIR {{ idl_home }}
# Startup SSW IDL
{{ executable }} {{ command_filename }}
