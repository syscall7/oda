from libc.stdint cimport uint64_t    

# ------------------------------------------------------------------------------
# PROTOTYPES
# ------------------------------------------------------------------------------

cdef extern const char* snowman_decompile_by_addr(char *filename, uint64_t start, uint64_t end);

# ------------------------------------------------------------------------------
# MODULE-LEVEL FUNCTONS
# ------------------------------------------------------------------------------
def decompile(filename, start, end):
    ret = snowman_decompile_by_addr(filename.encode('UTF-8'), start, end)
    return ret.decode('UTF-8')

