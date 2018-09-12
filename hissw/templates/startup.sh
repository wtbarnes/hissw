#!/bin/tcsh
# Set SSW home
setenv SSW {{ ssw_home }}
# Set SSW instruments
setenv SSW_INSTR "{{ ssw_packages | join(' ') }}"
# Setup needed environment variables
source $SSW/gen/setup/setup.ssw
# Setup IDL environment
setenv IDL_DIR {{ idl_home }}
# Startup SSW IDL
sswidl {{ command_filename }}
