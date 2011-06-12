#!/usr/bin/env python


import os


SYSTEM_ROOT = "/System/Library/Frameworks/Python.framework" 
MACPYTHON_ROOT = "/Library/Frameworks/Python.framework"

def detect_python_versions(python_framework_root):
    versions = os.listdir(python_framework_root + "/Versions/")
    versions = [v for v in versions if v != 'Current']
    return versions

    

def detect_system_python_installs():
    root = SYSTEM_ROOT
    return detect_python_versions(root)


def detect_epd_installs():
    root = MACPYTHON_ROOT
    return [v for v in detect_python_versions(root) if v.startswith('6')]


def detect_macpython_installs():
    root = MACPYTHON_ROOT
    return [v for v in detect_python_versions(root) if not v.startswith('6')]
    




def generate_bash_select_func(framework_root, install_type, version, use_generic_prompt):
    values = {
        'framework_root'   : framework_root,
        'install_type'     : install_type,
        'version'          : version,
        'stripped_version' : version.replace(".", ""),
        'func_name'        : install_type.replace(" ", "_").lower()
        }

    if use_generic_prompt:
        return """
        select_{func_name}{stripped_version}()
        {{
            echo \"Setting environment for {install_type} {version}\"
            PATH=\"{framework_root}/Versions/{version}/bin/:${{OLD_PATH}}\"
            export PATH

            export PS1="({install_type} {version}) \h:\W \u\$ "

        }}
                """.format(**values)
        
    else:
        return """
select_{func_name}{stripped_version}()
{{
    echo \"Setting environment for {install_type} {version}\"
    PATH=\"{framework_root}/Versions/{version}/bin/:${{OLD_PATH}}\"
    export PATH
    
    export PS1="\n${{LIGHT_CYAN}}(${{BLUE}}{install_type} {version}${{LIGHT_CYAN}}) $PURPLE\u$DEFAULT at $BROWN\h$DEFAULT in $GREEN\w\
    $DEFAULT\n$ "
    
}}
        """.format(**values)

        



def generate_bash_select_functions(outfile, framework_root, install_type, versions, use_generic_prompt):

    for v in versions:
        print "Adding %s %s" % (install_type, v)
        bash_function = generate_bash_select_func(framework_root,
                                        install_type,
                                        v,
                                        use_generic_prompt)
        outfile.write(bash_function)



if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Detects all python installations and creates bash functions to switch between them')
    parser.add_argument('--use_generic_prompt', type=bool, dest='use_generic_prompt', default=True, required=False, help='True (default): Use the default PS1 var False: Use a custom fancy prompt')
    args = parser.parse_args()
    
    outname = os.path.expandvars("$HOME/.python_switchers.sh")
    outfile = open(outname, 'w+')

    
    
    system_versions = detect_system_python_installs()
    generate_bash_select_functions(outfile,
                                   SYSTEM_ROOT,
                                   "System Python",
                                   system_versions,
                                   args.use_generic_prompt)


    macpython_versions = detect_macpython_installs()
    generate_bash_select_functions(outfile,
                                   MACPYTHON_ROOT,
                                   "MacPython",
                                   macpython_versions, 
                                   args.use_generic_prompt)


    epd_versions = detect_epd_installs()
    generate_bash_select_functions(outfile,
                                   MACPYTHON_ROOT,
                                   "EPD",
                                   epd_versions,
                                   args.use_generic_prompt)

    outfile.close()
    print "Saved python switcher bash functions to %s" % outname
