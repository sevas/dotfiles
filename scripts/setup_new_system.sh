#!/bin/bash

pushd .
cd ~

mkdir -p .hgext
cd .hgext
hg clone https://bitbucket.org/sjl/hg-prompt



popd
pushd .
mkdir -p ~/.config

cp -r ../config/fish ~/.config

cd ~/.config
mkdir -p fish/lib
cd fish/lib
git clone https://github.com/sjl/z-fish



cd ~
cd .hgext
hg clone https://bitbucket.org/sevas/mercurial-cli-templates



cd ~
mkdir -p build
cd build
hg clone https://bitbucket.org/sevas/python-update-alternatives

cd python-update-alternatives

python update_python_switchers.py


popd

