# ------------------------------------------------------------------------------
# File: active_scan.S
# Date: 3/29/15
# Purpose: Test active scanning to discover new text regions
# Description: This file represents a raw binary that has a mix of code and
#              data regions.  The entry point is loc_0 in the middle of the
#              file.  The control zig zags back and forth around the start.
# ------------------------------------------------------------------------------
.global _start

.section .data

_start:
main:
loc_0:
    push %ebp
    jmp loc_1
    pop %ebp
    ret

.fill 16, 1, 0xff

loc_3:
    push %ebp
    jmp loc_4
    pop %ebp
    ret

.fill 16, 1, 0xff

loc_1:
    push %ebp
    jmp loc_2
    pop %ebp
    ret

.fill 16, 1, 0xff

loc_4:
    push %ebp
    jmp loc_5
    pop %ebp
    ret

.fill 16, 1, 0xff

loc_2:
    push %ebp
    jmp loc_3
    pop %ebp
    ret

.fill 16, 1, 0xff

loc_5:
    push %ebp
    nop
    pop %ebp
    ret
    
