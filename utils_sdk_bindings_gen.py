# Copyright (C) 2019 Kyaw Kyaw Htike @ Ali Abdul Ghafur. All rights reserved.
import os
import subprocess

class Compiler_MSVC:
    def __init__(self):
        self.fpath_vcvarsall_bat = r"C:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Auxiliary\Build\vcvarsall.bat"
        self.param_arch_for_vcvarsall_bat = 'amd64'
        self.fpath_cl_exe = r"C:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Tools\MSVC\14.16.27023\bin\Hostx64\x64\cl.exe"
        self.fpath_link_exe = r"C:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Tools\MSVC\14.16.27023\bin\Hostx64\x64\link.exe"
    def compile_dll(self, dir_working, name_module, extension_output_dll, ):
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
