#!/bin/bash -e
# ------------------------------------------------------------------------------
# File: build.sh
# Description: ODA script to build the Python wrapper for Snowman
# ------------------------------------------------------------------------------

# assumes Cython and pydev are already installed
# install snowman dependencies
sudo apt-get install libboost-dev qtbase5-dev

# version of snowman we are using
VERSION=0.1.1

# download snowman source
wget https://github.com/yegord/snowman/archive/v${VERSION}.zip

# extract source
unzip v${VERSION}.zip

# copy our pysnowman wrapper into the Snowman source tree
cp -R pysnowman ./snowman-$VERSION/src/

# apply ODA patch (generated with diff -u)
# NOTE: The patch turns on position independent code so we can build a shared
#       library and adds our pysnowman module to the build.
patch --verbose -u -d snowman-${VERSION}/src/ <<'HERE_DOC'
--- snowman-0.1.1/src/CMakeLists.txt	2017-11-18 10:05:20.000000000 -0400
+++ snowman-0.1.1-patched/src/CMakeLists.txt	2017-11-18 10:48:23.663272842 -0500
@@ -1,6 +1,9 @@
 cmake_minimum_required(VERSION 3.9)
 project(Decompiler C CXX)

+set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fPIC")
+set(CMAKE_CXX_FLAGS "${CMAKE_C_FLAGS} -fPIC")
+
 enable_testing()

 # Show what's going on when running make.
@@ -170,6 +173,7 @@
 add_subdirectory(nc)
 add_subdirectory(nocode)
 add_subdirectory(snowman)
+add_subdirectory(pysnowman)
 if(${IDA_PLUGIN_ENABLED})
     add_subdirectory(ida-plugin)
 endif()
HERE_DOC

# create separate build directory for snowman
mkdir snowman-${VERSION}/build
cd snowman-${VERSION}/build

# build snowman and our pysnowman wrapper
# NOTE: For debug use cmake -D CMAKE_BUILD_TYPE=Debug ../src
cmake ../src
cmake --build .

# install the ODA pysnowman shared library 
sudo cp ./pysnowman/libpysnowman.so /usr/lib/

# build the snowman python module
cd -
sudo python setup.py build install
