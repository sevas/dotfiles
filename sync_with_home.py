#!/usr/bin/env python
import shutil
import os.path


dotfiles = [".bash_profile", ".bash_pyfuncs", ".inputrc", ".pythonrc.py"]
scripts = ["update_python_switchers.py"]



def get_home_dir():
    return os.path.expandvars("$HOME")



def get_bin_dir():
    return os.path.join(os.path.expandvars("$HOME"), "bin")



def copy_files(src_dir, dst_dir, files):
    for f in files:
        dst = os.path.join(dst_dir, f)
        src = os.path.join(src_dir, f)
        print("Copying {0} to {1}".format(src, dst))
        shutil.copy(src, dst)



def copy_dotfiles_from_home():
    home = get_home_dir()
    copy_files(home, "./", dotfiles)


def copy_scripts_from_home():
    bin_dir = get_bin_dir()
    copy_files(bin_dir, "./scripts", scripts)



def copy_dotfiles_to_home():
    home = get_home_dir()
    copy_files("./", home, dotfiles)


def copy_scripts_to_home():
    bin_dir = get_bin_dir()
    copy_files("./scripts", bin_dir, scripts)
    



if __name__=="__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--sync", choices=["to home", "from home"], 
                        required=True, dest="sync_mode" )
    
    
    args = parser.parse_args()
    
    if args.sync_mode == "to home":
        copy_dotfiles_to_home()
        copy_scripts_to_home()
        
    elif args.sync_mode == "from home":
        copy_dotfiles_from_home()
        copy_scripts_from_home()