#!/bin/sh

push .
cd ~

mkdir -p .hgext
cd .hgext
hg clone https://bitbucket.org/sjl/hg-prompt

cd ~
cd .config
mkdir -p fish/lib
cd fish/lib
git clone https://github.com/sjl/z-fish



popd