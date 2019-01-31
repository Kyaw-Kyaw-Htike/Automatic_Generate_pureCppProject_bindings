# Copyright (C) 2019 Kyaw Kyaw Htike @ Ali Abdul Ghafur. All rights reserved.
import glob
import os
import shutil
import subprocess
import sys

# values need to be specified by user
header_files_dir_and_pattern_sdk = r'C:\Users\Kyaw\Desktop\swig_example\ConsoleApplication2\*.h'
fpath_static_lib_sdk = r"C:\Users\Kyaw\Desktop\swig_example\ConsoleApplication2\x64\Release\ConsoleApplication2.lib"
dir_output = r'C:\Users\Kyaw\Desktop\swig_example\output_gen'
path_swig_exe = r"C:\Users\Kyaw\Desktop\swig_example\swigwin-3.0.12\swig.exe"
fpath_vcvarsall_bat = r'C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\vcvarsall.bat'
param_arch_for_vcvarsall_bat = 'amd64'
fpath_cl_exe = r"C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\bin\amd64\cl.exe"
fpath_link_exe = r"C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\bin\amd64\link.exe"
name_module = 'RnDModule'
# swig_language = 'csharp'
# swig_language = 'python'
swig_language = 'java'
extension_output_dll = 'dll'
# extension_output_dll = 'pyd'
# dirs_headers_include_interpreter = []
# dirs_libs_link_interpreter = []
dirs_headers_include_interpreter = [r'C:\Program Files\Java\jdk1.8.0_172\include', r'C:\Program Files\Java\jdk1.8.0_172\include\win32']
dirs_libs_link_interpreter = [r"C:\Program Files\Java\jdk1.8.0_172\lib\jvm.lib"]
# dirs_headers_include_interpreter = [r'D:\Anaconda3\envs\deep_learning\include']
# dirs_libs_link_interpreter = [r"D:\Anaconda3\envs\deep_learning\libs\python36.lib"]
desired_output_file_extensions = ['*.py', '*.cs', '*.java', '*.java', '*.dll', '*.pyd']

# values fixed (i.e. not to be changed by user)
dir_working = os.path.join(dir_output, 'working')
name_cpp_gen_swig = 'interface_wrap.cxx'
name_output_dll = name_module + '.' + extension_output_dll
if swig_language == 'python':
    name_output_dll = '_' + name_output_dll

if not os.path.exists(dir_output):
    sys.exit('The specified output directory does it exist. Create it first.')
if os.listdir(dir_output):
    sys.exit('The specified output directory is not empty. Clean it up first.')

# create the working directory inside the output folder
os.mkdir(dir_working)

# get paths of all header files specified by user
fpaths_header_files = glob.glob(header_files_dir_and_pattern_sdk)
print('Number of header files found =', len(fpaths_header_files))

# copy all the header files to the working directory
for hf in fpaths_header_files:
    shutil.copy(hf, dir_working)

# generate interface file in the working directory
with open(os.path.join(dir_working, 'interface.i'), 'w') as fid_out:
    fid_out.write('%module {}\n\n'.format(name_module))
    fid_out.write('%{\n')
    for hf in fpaths_header_files:
        fid_out.write('# include "{}"\n'.format(os.path.basename(hf)))
    fid_out.write('%}\n\n')
    # fid_out.write('%include <windows.i>\n')

    for hf in fpaths_header_files:
        fid_out.write('%include "{}"\n'.format(os.path.basename(hf)))

# run the swig
subprocess.call([path_swig_exe, '-' + swig_language, '-c++', 'interface.i'], cwd=dir_working, shell=False)

# build the generated cpp files using VISUAL STUDIO
str_cmd_headers_include = []
for d in dirs_headers_include_interpreter:
    str_cmd_headers_include.append('-I"{}"'.format(d))
str_cmd_headers_include = ' '.join(str_cmd_headers_include)

str_cmd_libs_link = []
str_cmd_libs_link.append('"{}"'.format(fpath_static_lib_sdk))
for d in dirs_libs_link_interpreter:
    str_cmd_libs_link.append('"{}"'.format(d))
str_cmd_libs_link = ' '.join(str_cmd_libs_link)

fpath_compile_batch_file = os.path.join(dir_working, 'compile_commands.cmd')
with open(fpath_compile_batch_file, 'w') as fid_out:
    fid_out.write(f'''call "{fpath_vcvarsall_bat}" {param_arch_for_vcvarsall_bat}\n''')
    fid_out.write(f''' "{fpath_cl_exe}" /GS /GL /W3 /Gy /Fo"{os.path.join(dir_working, name_module+'.obj')}" /Fa"{os.path.join(dir_working, name_module+'.asm')}" /Zc:wchar_t {str_cmd_headers_include} /Zi /Gm- /O2 /sdl /Fd"vc140.pdb" /Zc:inline /fp:precise /D "NDEBUG" /D "_WINDOWS" /D "_USRDLL" /D "GENERATE_DLL_EXPORTS" /D "_WINDLL" /D "_UNICODE" /D "UNICODE" /errorReport:prompt /WX- /Zc:forScope /Gd /Oi /MD /EHsc /nologo /Fp"{name_module}.pch" {name_cpp_gen_swig} /link /OUT:"{name_output_dll}" /MANIFEST /LTCG:incremental /NXCOMPAT /DYNAMICBASE {str_cmd_libs_link} "kernel32.lib" "user32.lib" "gdi32.lib" "winspool.lib" "comdlg32.lib" "advapi32.lib" "shell32.lib" "ole32.lib" "oleaut32.lib" "uuid.lib" "odbc32.lib" "odbccp32.lib" /IMPLIB:"{name_module}.lib" /DEBUG /DLL /MACHINE:X64 /OPT:REF /INCREMENTAL:NO /SUBSYSTEM:WINDOWS /MANIFESTUAC:"level='asInvoker' uiAccess='false'" /ManifestFile:"{name_module}.dll.intermediate.manifest" /OPT:ICF /ERRORREPORT:PROMPT /NOLOGO /TLBID:1\n''')
subprocess.call(fpath_compile_batch_file, cwd=dir_working, shell=False)

# copy the desired compiled files from working folder to output folder
for d in desired_output_file_extensions:
    fpaths_desired = glob.glob(os.path.join(dir_working, d))
    for f in fpaths_desired:
        shutil.copy(f, dir_output)

