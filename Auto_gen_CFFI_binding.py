# Copyright (C) 2019 Kyaw Kyaw Htike @ Ali Abdul Ghafur. All rights reserved.
import glob
import os
import shutil
import subprocess
import sys
import re

# user specified values
dir_SDK_project = r'C:\Users\Kyaw\Desktop\New folder (15)\New folder'
dir_output = r'C:\Users\Kyaw\Desktop\New folder (15)\New folder\bindings_output'
void_pointer_mode = True

# don't change below
dir_SDK_project = os.path.normpath(dir_SDK_project)
search_pattern_header_file_names = '*_PUBLIC.h'
folder_name_project = os.path.basename(dir_SDK_project)
basename_for_sdk = folder_name_project.upper().replace('_', '')
define_str_sdk = basename_for_sdk + '_API'
name_dll = basename_for_sdk + '.dll'
fpath_dll = os.path.normpath(os.path.join(dir_SDK_project, '..', 'x64', 'Release', name_dll))

if not os.path.exists(dir_output):
    sys.exit('The specified output directory does not exist. Create it first.')
# if os.listdir(dir_output):
#     sys.exit('The specified output directory is not empty. Clean it up first.')

fpaths_header_files = glob.glob(os.path.join(dir_SDK_project, search_pattern_header_file_names))
print('Number of header files found =', len(fpaths_header_files))

# copy the dll into the output folder
shutil.copy(fpath_dll, dir_output)

# get list of all function declarations from all header files
c_declarations = []
len_define_str_sdk = len(define_str_sdk)
for fpath_input_header_file in fpaths_header_files:
    fid = open(fpath_input_header_file, 'r')
    header_file_contents = fid.readlines()
    fid.close()
    for cur_line in header_file_contents:
        print(cur_line)
        cur_line = cur_line.strip(' \t\n\r')
        if not cur_line[0:len_define_str_sdk] == define_str_sdk:
            continue
        cur_line = cur_line[len_define_str_sdk + 1:]
        if cur_line[0:6] == 'struct':
            continue
        c_declarations.append(cur_line)

# define all the regular expression details needed
type_c = '((?:unsigned +)?[a-zA-Z][a-zA-Z0-9_]*(?: *\*)?)'
variable_name = '([a-z][a-zA-Z0-9_]*)'
owp = ' *' # optional white space
cwp = ' +' # compulsory white space
function_name = '([a-z][a-zA-Z0-9_]+)'
function_argType_and_argVar_1st = f'(?:{owp}{type_c}{cwp}{variable_name}{owp})?'
function_argType_and_argVar_subsequent = f'(?:,{owp}{type_c}{cwp}{variable_name}{owp})?'
function_all_argTypes_and_argVars = function_argType_and_argVar_1st
for i in range(100):
    function_all_argTypes_and_argVars += function_argType_and_argVar_subsequent
p = re.compile(f'''{owp}{type_c}{cwp}{function_name}{owp}\({function_all_argTypes_and_argVars}\){owp};''')

# parse each c function declaration to generate python code for CFFI
c_declarations_cffi = []
def_declarations_for_python = []
calling_cffi_functions_for_python = []

for c_declaration in c_declarations:
    parsed_strings = p.match(c_declaration).groups()
    parsed_strings = [xi for xi in parsed_strings if xi is not None]
    parsed_strings = [xi.replace(' ', '') for xi in parsed_strings]
    parsed_strings = ['unsigned ' + xi[8:] if xi[0:8]=='unsigned' else xi for xi in parsed_strings]
    if void_pointer_mode:
        parsed_strings = ['void*' if (xi.endswith('*') and xi != 'unsigned char*' and xi != 'char*' and xi != 'int*' and xi != 'double*' and xi != 'float*'and xi != 'long*') else xi for xi in parsed_strings]
    else:
        parsed_strings = ['struct ' + xi if (xi.endswith('*') and xi != 'unsigned char*' and xi != 'char*' and xi != 'int*' and xi != 'double*' and xi != 'float*' and xi != 'long*') else xi for xi in parsed_strings]
    c_declaration_cffi = f'''{parsed_strings[0]} {parsed_strings[1]}('''
    def_declaration_for_python = f'def {parsed_strings[1]}('
    calling_cffi_function_for_python = f'C.{parsed_strings[1]}('
    if parsed_strings[0] != 'void':
        calling_cffi_function_for_python = f'return C.{parsed_strings[1]}('
    for i in range(2, len(parsed_strings), 2):
        if i < len(parsed_strings) - 2:
            c_declaration_cffi += f'''{parsed_strings[i]} {parsed_strings[i+1]},'''
            def_declaration_for_python += f'''{parsed_strings[i+1]},'''
            calling_cffi_function_for_python += f'''{parsed_strings[i+1]},'''
        else:
            c_declaration_cffi += f'''{parsed_strings[i]} {parsed_strings[i+1]}'''
            def_declaration_for_python += f'''{parsed_strings[i+1]}'''
            calling_cffi_function_for_python += f'''{parsed_strings[i+1]}'''
    c_declaration_cffi += ');'
    def_declaration_for_python += '):'
    calling_cffi_function_for_python += ')'
    c_declarations_cffi.append(c_declaration_cffi)
    def_declarations_for_python.append(def_declaration_for_python)
    calling_cffi_functions_for_python.append(calling_cffi_function_for_python)

with open(os.path.join(dir_output, basename_for_sdk + '.py'), 'w') as fid:
    fid.write(f'''from cffi import FFI
import os
fpath_dll = os.path.join(os.path.dirname(__file__), '{name_dll}')
ffi = FFI()
C = ffi.dlopen(fpath_dll)

ffi.cdef("""
''')

    fid.write('\n'.join(c_declarations_cffi) + '\n')
    fid.write('"""\n)\n\n')

    for (def_declaration_for_python, calling_cffi_function_for_python) in zip(def_declarations_for_python, calling_cffi_functions_for_python):
        fid.write(f'{def_declaration_for_python}\n')
        fid.write(f'\t{calling_cffi_function_for_python}\n')
