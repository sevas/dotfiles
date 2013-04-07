#!/usr/bin/env python


import os


SYSTEM_ROOT = "/System/Library/Frameworks/Python.framework"
MACPYTHON_ROOT = "/Library/Frameworks/Python.framework"
EPD64_ROOT = "/Library/Frameworks/EPD64.framework"


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


def generate_bash_select_func(framework_root, install_type, version):
    values = {
        'framework_root':   framework_root,
        'install_type':     install_type,
        'version':          version,
        'stripped_version': version.replace(".", ""),
        'func_name':        install_type.replace(" ", "_").lower()
    }

    return """
        select_{func_name}_{stripped_version}()
        {{
            echo \"Setting environment for {install_type} {version}\"
            PATH=\"{framework_root}/Versions/{version}/bin:${{OLD_PATH}}\"
            export PATH
            export PROMPT_PYTHON_VERSION="{install_type} {version}"

        }}
                """.format(**values)


def generate_bash_select_functions(outfile, framework_root, install_type, versions):

    for v in versions:
        print("+++ Adding %s %s" % (install_type, v))
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

        print "Saved python switcher bash functions to %s" % outname

