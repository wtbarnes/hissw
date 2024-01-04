#!/bin/tcsh
# Set SSW home
setenv SSW {{ ssw_home }}
# Set SSW instruments
setenv SSW_INSTR "{{ ssw_packages | join(' ') }}"
# Setup needed environment variables
{% if use_ssw %}
source $SSW/gen/setup/setup.ssw
{% endif %}
# Setup IDL environment
setenv IDL_DIR {{ idl_home }}
# Startup SSW IDL
{{ executable }} {{ command_filename }}
