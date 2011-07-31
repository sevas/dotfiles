#!/usr/bin/env python


import os


SYSTEM_ROOT = "/System/Library/Frameworks/Python.framework" 
MACPYTHON_ROOT = "/Library/Frameworks/Python.framework"
EPD64_ROOT = "/Library/Frameworks/EPD64.framework"

def detect_python_versions(python_framework_root):
    versions = os.listdir(python_framework_root + "/Versions/")
    versions = [v for v in versions if v != 'Current']
    return versions

    

def detect_system_python_installs():
    root = SYSTEM_ROOT
    return detect_python_versions(root)


def detect_epd32_installs():
    root = MACPYTHON_ROOT
    
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
    
    epd_versions = [v for v in detect_python_versions(root) if is_epd_version(v)]
    return epd_versions 
    
    
    
def detect_epd64_installs():
    directories = os.listdir(os.path.join(EPD64_ROOT, "Versions"))
    versions = [v for v in directories if v != 'Current']
    
    return versions


def detect_macpython_installs():
    root = MACPYTHON_ROOT
    return [v for v in detect_python_versions(root) if not v.startswith('6')]
    




def generate_bash_select_func(framework_root, install_type, version, use_fancy_prompt):
    values = {
        'framework_root'   : framework_root,
        'install_type'     : install_type,
        'version'          : version,
        'stripped_version' : version.replace(".", ""),
        'func_name'        : install_type.replace(" ", "_").lower()
        }

    if use_fancy_prompt:
        return """
        select_{func_name}_{stripped_version}()
        {{
            echo \"Setting environment for {install_type} {version}\"
            PATH=\"{framework_root}/Versions/{version}/bin/:${{OLD_PATH}}\"
            export PATH

            export PS1="\n${{LIGHT_CYAN}}(${{BLUE}}{install_type} {version}${{LIGHT_CYAN}}) $PURPLE\u$DEFAULT at $BROWN\h$DEFAULT in $GREEN\w\
            $DEFAULT\n$ "

        }}
                """.format(**values)
    else:
        return """
        select_{func_name}_{stripped_version}()
        {{
            echo \"Setting environment for {install_type} {version}\"
            PATH=\"{framework_root}/Versions/{version}/bin/:${{OLD_PATH}}\"
            export PATH

            export PS1="({install_type} {version}) \h:\W \u\$ "

        }}
                """.format(**values)        



def generate_bash_select_functions(outfile, framework_root, install_type, versions, use_fancy_prompt):

    for v in versions:
        print "Adding %s %s" % (install_type, v)
        bash_function = generate_bash_select_func(framework_root,
                                        install_type,
                                        v,
                                        use_fancy_prompt)
        outfile.write(bash_function)



if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Detects all python installations and creates bash functions to switch between them')
    parser.add_argument('--use-fancy-prompt', dest='use_fancy_prompt', action='store_true', help='Use a custom fancy prompt with colors!')
    args = parser.parse_args()
    
    outname = os.path.expandvars("$HOME/.python_switchers.sh")
    outfile = open(outname, 'w+')


    if args.use_fancy_prompt:
        print 'Using fancy prompt'
    else:
        print 'Using generic prompt'
        
    
    
    system_versions = detect_system_python_installs()
    generate_bash_select_functions(outfile,
                                   SYSTEM_ROOT,
                                   "System Python",
                                   system_versions,
                                   args.use_fancy_prompt)


    macpython_versions = detect_macpython_installs()
    generate_bash_select_functions(outfile,
                                   MACPYTHON_ROOT,
                                   "MacPython",
                                   macpython_versions, 
                                   args.use_fancy_prompt)


    epd32_versions = detect_epd32_installs()
    generate_bash_select_functions(outfile,
                                   MACPYTHON_ROOT,
                                   "EPD 32",
                                   epd32_versions,
                                   args.use_fancy_prompt)


    epd64_versions = detect_epd64_installs()
    generate_bash_select_functions(outfile,
                                    EPD64_ROOT,
                                    "EPD 64",
                                    epd64_versions,
                                    args.use_fancy_prompt)



    outfile.close()
    print "Saved python switcher bash functions to %s" % outname
