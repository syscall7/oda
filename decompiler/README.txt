This directory contains a Python wrapper the ODA team developed to provide
access to the Snowman decompiler.  The main components are:

    * build.sh - script to build everything
    * pysnowman - simple shared library to wrap the key parts of Snowman
    * snowman.pyx - Cython module that wraps the wrapper shared library

To build, simply execute the build script:

    sudo ./build.sh
