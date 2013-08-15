#!/usr/bin/env python


import os
import sys
import platform
import subprocess

SYSTEM_ROOT = "/System/Library/Frameworks/Python.framework"
MACPYTHON_ROOT = "/Library/Frameworks/Python.framework"
EPD64_ROOT = "/Library/Frameworks/EPD64.framework"



def get_python_version(python_root):
    python_filepath = os.path.join(python_root, 'bin', 'python')
    p = subprocess.Popen([python_filepath, '-V'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    return stderr.strip()


def has_python(prefix):
    python_filepath = os.path.join(prefix, 'bin', 'python')
    if os.path.exists(python_filepath):
        return True


def get_anaconda_version(python_version):
    return [e.strip() for e in python_version.split("::") if e]


def detect_anaconda_installs():
    p = subprocess.Popen(['locate', 'bin/conda'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    results = stdout.split("\n")

    if not results:
        return []

    prefixes = [each.split('bin/conda')[0] for each in results if each and 'pkgs' not in each]
    return prefixes


def detect_python_versions(python_framework_root):
    def not_empty(version_directory_name):
        full_version_path = os.path.join(python_framework_root, 'Versions', version_directory_name, 'bin')
        if os.path.exists(full_version_path):
            return True
        else:
            print("!!! Missing bin/ directory under '{0}'. This installation looks broken. Skipping {1}".format(full_version_path, version_directory_name))
            return False

    versions = os.listdir(python_framework_root + "/Versions/")
    versions = [v for v in versions if v != 'Current' and not_empty(v)]
    return versions


def detect_system_python_installs():
    root = SYSTEM_ROOT
    return detect_python_versions(root)


def is_epd_version(version):
    """
    Detects whether a version string is an EPD version
    number or a regular python version number.

    This works because EPD starts with much higher version
    numbers (6.x, 7.x, ...) nowadays
    """
    def get_major_version(v):
        return int(v.split('.')[0])

    # EPD versions don't start with 2.x or 3.x
    return get_major_version(version) not in [2, 3]


def detect_epd32_installs():
    root = MACPYTHON_ROOT

    epd_versions = [v for v in detect_python_versions(root) if is_epd_version(v)]
    return epd_versions


def detect_epd64_installs():
    directories = os.listdir(os.path.join(EPD64_ROOT, "Versions"))
    versions = [v for v in directories if v != 'Current']

    return versions


def detect_macpython_installs():
    root = MACPYTHON_ROOT
    return [v for v in detect_python_versions(root) if not is_epd_version(v)]



def make_python_dir(framework_root, version):
    return os.path.join(framework_root, 'Versions', version, 'bin')

def generate_bash_select_func(framework_root, install_type, version):
    values = {
        'path':             make_python_dir(framework_root, version),
        'install_type':     install_type,
        'version':          version,
        'stripped_version': version.replace(".", ""),
        'func_name':        install_type.replace(" ", "_").lower()
    }

    return """
        select_{func_name}_{stripped_version}()
        {{
            echo \"Setting environment for {install_type} {version}\"
            PATH=\"{path}:${{OLD_PATH}}\"
            export PATH
            export PROMPT_PYTHON_VERSION="{install_type} {version}"

        }}
                """.format(**values)


def generate_anaconda_bash_select_func(framework_root):
    py_version = get_python_version(framework_root)
    py, anaconda_version_string = get_anaconda_version(py_version)
    name, version, arch = anaconda_version_string.split(" ")

    values = {
        'path':             os.path.join(framework_root, 'bin'),
        'install_type':     name,
        'version':          version+arch,
        'stripped_version': version.replace(".", ""),
        'func_name':        name.replace(" ", "_").lower()
    }

    return """
        select_{func_name}_{stripped_version}()
        {{
            echo \"Setting environment for {install_type} {version}\"
            PATH=\"{path}:${{OLD_PATH}}\"
            export PATH
            export PROMPT_PYTHON_VERSION="{install_type} {version}"

        }}
                """.format(**values), anaconda_version_string

def generate_bash_select_functions(outfile, framework_root, install_type, versions):
    for v in versions:
        print("+++ Adding {:<40} [{}]".format(install_type+" "+v, make_python_dir(framework_root, v)))
        bash_function = generate_bash_select_func(framework_root, install_type, v)
        outfile.write(bash_function)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Detects all python installations and creates bash functions to switch between them')
    args = parser.parse_args()

    outname = os.path.expandvars("$HOME/.python_switchers.sh")

    with open(outname, 'w+') as outfile:
        system_versions = detect_system_python_installs()
        generate_bash_select_functions(outfile,
                                       SYSTEM_ROOT,
                                       "System Python",
                                       system_versions)

        macpython_versions = detect_macpython_installs()
        generate_bash_select_functions(outfile,
                                       MACPYTHON_ROOT,
                                       "MacPython",
                                       macpython_versions)

        epd32_versions = detect_epd32_installs()
        generate_bash_select_functions(outfile,
                                       MACPYTHON_ROOT,
                                       "EPD 32",
                                       epd32_versions)

        epd64_versions = detect_epd64_installs()
        generate_bash_select_functions(outfile,
                                       EPD64_ROOT,
                                       "EPD 64",
                                       epd64_versions)

        for anaconda_root in detect_anaconda_installs():
            bash_func, version = generate_anaconda_bash_select_func(anaconda_root)
            print("+++ Adding {:<40} [{}]".format(version, anaconda_root))
            outfile.write(bash_func)

        print "--- Saved python switcher bash functions to %s" % outname

