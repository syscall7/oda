#!/bin/sh
# This build script creates two active_scan outputs.  The first is an ELF file
# that is basically the .data section.  The second is a binary file with the
# contents of .data.
gcc -nostdlib -m32 -o active_scan_follow_calls.o active_scan_follow_calls.S
objcopy -O binary -j .data active_scan_follow_calls.o active_scan_follow_calls.bin
